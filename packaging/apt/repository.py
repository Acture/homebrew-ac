#!/usr/bin/env python3
"""Build an APT snapshot from pinned, checksum-verified upstream releases."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import cast

LOG: logging.Logger = logging.getLogger(__name__)
ARCHITECTURES: tuple[str, ...] = ("amd64", "arm64")


def run(
    command: list[str], *, cwd: Path | None = None, data: bytes | None = None
) -> bytes:
    return subprocess.run(
        command, cwd=cwd, input=data, stdout=subprocess.PIPE, check=True
    ).stdout


def records(path: Path) -> list[dict[str, object]]:
    value: object = json.loads(path.read_text())
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, dict) for item in value)
    ):
        raise ValueError(f"{path}: expected a nonempty list of records")
    return cast(list[dict[str, object]], value)


def field(record: dict[str, object], name: str, pattern: str = r"[^\r\n]+") -> str:
    value = record.get(name)
    if not isinstance(value, str) or re.fullmatch(pattern, value) is None:
        raise ValueError(f"invalid {name}: {value!r}")
    return value


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        result = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def checksums(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text().splitlines():
        match = re.fullmatch(r"([a-fA-F0-9]{64}) [ *]([^/\r\n]+)", line)
        if match is None or match[2] in result:
            raise ValueError(f"invalid or duplicate checksum in {path}: {line!r}")
        result[match[2]] = match[1].lower()
    return result


def fetch(specification: Path, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=False)
    manifest: list[dict[str, str]] = []
    for index, record in enumerate(records(specification), start=1):
        repository = field(record, "repository", r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
        package = field(record, "package", r"[a-z0-9][a-z0-9+.-]+")
        tag = field(record, "tag", r"v[0-9][A-Za-z0-9.+-]*")
        commit = field(record, "commit", r"[a-f0-9]{40}")
        version = field(record, "version", r"[0-9][A-Za-z0-9.+:~_-]*")
        architectures = record.get("architectures")
        if (
            not isinstance(architectures, list)
            or not architectures
            or not all(
                isinstance(architecture, str)
                and architecture in (*ARCHITECTURES, "all")
                for architecture in architectures
            )
        ):
            raise ValueError(f"invalid architectures for {package}")
        LOG.info("Fetching %s %s", repository, tag)
        release: object = json.loads(
            run(["gh", "api", f"repos/{repository}/releases/tags/{tag}"])
        )
        if (
            not isinstance(release, dict)
            or release.get("draft") is not False
            or release.get("prerelease") is not False
        ):
            raise ValueError(f"{repository} {tag} is not a published stable release")
        actual_commit = (
            run(["gh", "api", f"repos/{repository}/commits/{tag}", "--jq", ".sha"])
            .decode()
            .strip()
        )
        if actual_commit != commit:
            raise ValueError(f"{repository} {tag} no longer points at {commit}")
        directory = output / str(index)
        run(
            [
                "gh",
                "release",
                "download",
                tag,
                "--repo",
                repository,
                "--dir",
                str(directory),
                "--pattern",
                "*.deb",
                "--pattern",
                "SHA256SUMS",
            ]
        )
        sums = checksums(directory / "SHA256SUMS")
        for architecture in architectures:
            name = f"{package}_{version}_{architecture}.deb"
            path = directory / name
            checksum = sums.get(name)
            if checksum is None or digest(path) != checksum:
                raise ValueError(f"release checksum mismatch: {name}")
            manifest.append(
                {
                    "file": path.relative_to(output).as_posix(),
                    "package": package,
                    "version": version,
                    "architecture": architecture,
                    "sha256": checksum,
                    "repository": repository,
                    "tag": tag,
                    "commit": commit,
                }
            )
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def copy_packages(inputs: Path, output: Path) -> None:
    identities: set[tuple[str, str, str]] = set()
    for record in records(inputs / "manifest.json"):
        source = inputs / field(record, "file")
        if source.is_symlink() or not source.resolve().is_relative_to(inputs.resolve()):
            raise ValueError("package path escapes the input directory")
        expected = field(record, "sha256", r"[a-f0-9]{64}")
        if digest(source) != expected:
            raise ValueError(f"package checksum mismatch: {source}")
        package = field(record, "package", r"[a-z0-9][a-z0-9+.-]+")
        version = field(record, "version", r"[0-9][A-Za-z0-9.+:~_-]*")
        architecture = field(record, "architecture", r"all|amd64|arm64")
        identity = (package, version, architecture)
        actual = tuple(
            run(["dpkg-deb", "--field", str(source), name]).decode().strip()
            for name in ("Package", "Version", "Architecture")
        )
        if actual != identity or identity in identities:
            raise ValueError(f"mismatched or duplicate package identity: {identity}")
        identities.add(identity)
        target = (
            output
            / "pool/main"
            / package[0]
            / package
            / f"{package}_{version}_{architecture}.deb"
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        LOG.info("Verified %s %s (%s)", *identity)


def paragraphs(text: str) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for paragraph in text.strip().split("\n\n"):
        values: dict[str, str] = {}
        current = ""
        for line in paragraph.splitlines():
            if line.startswith((" ", "\t")) and current:
                values[current] += "\n" + line.strip()
            else:
                name, separator, value = line.partition(":")
                if not separator or name in values:
                    raise ValueError("invalid Debian control paragraph")
                current = name
                values[name] = value.strip()
        result.append(values)
    return result


def preserve(previous: Path, output: Path, fingerprint: str) -> None:
    previous_key = previous / "acture-archive-keyring.asc"
    if key_fingerprint(previous_key) != fingerprint:
        raise ValueError("previous snapshot has a different signing key")
    status = run(
        [
            "gpg",
            "--batch",
            "--status-fd",
            "1",
            "--verify",
            str(previous / "dists/stable/InRelease"),
        ]
    ).decode()
    valid = [
        line.split()
        for line in status.splitlines()
        if line.startswith("[GNUPG:] VALIDSIG ")
    ]
    if not any(fingerprint in (line[2], line[-1]) for line in valid):
        raise ValueError("previous snapshot was not signed by the expected key")
    signed = run(
        ["gpg", "--batch", "--decrypt", str(previous / "dists/stable/InRelease")]
    ).decode()
    release = paragraphs(signed)[0]
    indexes = {
        line.split()[2]: line.split()[0]
        for line in release["SHA256"].splitlines()
        if line.strip()
    }
    packages: dict[str, str] = {}
    for architecture in ARCHITECTURES:
        name = f"main/binary-{architecture}/Packages"
        index = previous / "dists/stable" / name
        if digest(index) != indexes[name]:
            raise ValueError(f"previous index checksum mismatch: {name}")
        if index.stat().st_size:
            for record in paragraphs(index.read_text()):
                packages[record["Filename"]] = record["SHA256"]
    for path in previous.glob("pool/**/*.deb"):
        if packages.get(path.relative_to(previous).as_posix()) != digest(path):
            raise ValueError(f"previous package checksum mismatch: {path.name}")
        target = output / path.relative_to(previous)
        if target.exists() and digest(path) != digest(target):
            raise ValueError(f"attempted to replace an existing package: {target.name}")
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copyfile(path, target)
    for path in previous.glob("dists/stable/main/binary-*/by-hash/SHA256/*"):
        if digest(path) != path.name:
            raise ValueError(f"corrupt previous index: {path}")
        target = output / path.relative_to(previous)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)


def key_fingerprint(path: Path) -> str:
    text = run(["gpg", "--batch", "--with-colons", "--show-keys", str(path)]).decode()
    fingerprints = [
        line.split(":")[9] for line in text.splitlines() if line.startswith("fpr:")
    ]
    if (
        not fingerprints
        or sum(line.startswith("pub:") for line in text.splitlines()) != 1
    ):
        raise ValueError("expected exactly one public signing key")
    return fingerprints[0]


def repository_uri(uri: str) -> str:
    if re.fullmatch(r"https://[A-Za-z0-9.-]+(?:/[A-Za-z0-9._~-]+)*/?", uri) is None:
        raise ValueError(
            "repository URI must be an HTTPS URL without credentials or query parameters"
        )
    return uri.rstrip("/") + "/"


def build(
    inputs: Path, output: Path, fingerprint: str, uri: str, previous: Path | None = None
) -> None:
    if re.fullmatch(r"[A-F0-9]{40}", fingerprint) is None:
        raise ValueError("a full uppercase signing-key fingerprint is required")
    uri = repository_uri(uri)
    if output.exists():
        raise ValueError("output must not exist; build a new snapshot")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as directory:
        stage = Path(directory) / "repository"
        stage.mkdir()
        key = stage / "acture-archive-keyring.asc"
        key.write_bytes(
            run(
                [
                    "gpg",
                    "--batch",
                    "--armor",
                    "--export-options",
                    "export-minimal",
                    "--export",
                    fingerprint,
                ]
            )
        )
        if key_fingerprint(key) != fingerprint:
            raise ValueError("exported key does not match the requested fingerprint")
        copy_packages(inputs, stage)
        if previous is not None:
            preserve(previous, stage, fingerprint)
        for architecture in ARCHITECTURES:
            index = stage / f"dists/stable/main/binary-{architecture}/Packages"
            index.parent.mkdir(parents=True, exist_ok=True)
            index.write_bytes(
                run(
                    [
                        "dpkg-scanpackages",
                        "--multiversion",
                        "--arch",
                        architecture,
                        "pool",
                    ],
                    cwd=stage,
                )
            )
            index.with_suffix(".gz").write_bytes(
                gzip.compress(index.read_bytes(), mtime=0)
            )
            for path in (index, index.with_suffix(".gz")):
                hashed = index.parent / "by-hash/SHA256" / digest(path)
                hashed.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, hashed)
        expiry = format_datetime(
            datetime.now(timezone.utc) + timedelta(days=14), usegmt=True
        )
        release = stage / "dists/stable/Release"
        options = {
            "Origin": "Acture",
            "Label": "Acture",
            "Suite": "stable",
            "Codename": "stable",
            "Architectures": "amd64 arm64",
            "Components": "main",
            "Acquire-By-Hash": "yes",
            "Valid-Until": expiry,
            "Description": "Acture software packages",
        }
        command = ["apt-ftparchive"]
        for name, value in options.items():
            command.extend(["-o", f"APT::FTPArchive::Release::{name}={value}"])
        release.write_bytes(run([*command, "release", "dists/stable"], cwd=stage))
        signing = [
            "gpg",
            "--batch",
            "--yes",
            "--local-user",
            fingerprint,
            "--digest-algo",
            "SHA256",
            "--armor",
        ]
        passphrase = os.environ.get("APT_SIGNING_PASSPHRASE")
        data = None if passphrase is None else (passphrase + "\n").encode()
        if passphrase is not None:
            signing.extend(["--pinentry-mode", "loopback", "--passphrase-fd", "0"])
        for action, name in (
            ("--clearsign", "InRelease"),
            ("--detach-sign", "Release.gpg"),
        ):
            run(
                [
                    *signing,
                    action,
                    "--output",
                    str(release.with_name(name)),
                    str(release),
                ],
                data=data,
            )
        (stage / "acture.sources").write_text(
            f"Types: deb\nURIs: {uri}\nSuites: stable\nComponents: main\n"
            "Architectures: amd64 arm64\nSigned-By: /etc/apt/keyrings/acture-archive-keyring.asc\n"
        )
        (stage / "fingerprint.txt").write_text(fingerprint + "\n")
        (stage / ".nojekyll").touch()
        (stage / "index.html").write_text(
            "<!doctype html><html lang=en><meta charset=utf-8><title>Acture APT repository</title>"
            "<h1>Acture APT repository</h1><p>Debian 13 and Ubuntu 24.04, amd64 and arm64.</p>"
            '<p><a href="acture-archive-keyring.asc">Signing key</a> · '
            '<a href="fingerprint.txt">Fingerprint</a> · <a href="acture.sources">APT source</a></p>'
        )
        os.replace(stage, output)
    LOG.info("Built signed snapshot at %s", output)


class Arguments(argparse.Namespace):
    command: str
    releases: Path
    inputs: Path
    output: Path
    fingerprint: str
    uri: str
    previous: Path | None


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    download = commands.add_parser(
        "fetch", help="fetch pinned stable releases and verify their checksums"
    )
    download.add_argument("--releases", type=Path, required=True)
    download.add_argument("--output", type=Path, required=True)
    snapshot = commands.add_parser("build", help="build and sign an APT snapshot")
    snapshot.add_argument("--inputs", type=Path, required=True)
    snapshot.add_argument("--output", type=Path, required=True)
    snapshot.add_argument("--fingerprint", required=True)
    snapshot.add_argument("--uri", required=True)
    snapshot.add_argument("--previous", type=Path)
    args = parser.parse_args(namespace=Arguments())
    if args.command == "fetch":
        fetch(args.releases, args.output)
    else:
        build(args.inputs, args.output, args.fingerprint, args.uri, args.previous)


if __name__ == "__main__":
    main()
