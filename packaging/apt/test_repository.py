from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import repository


class ValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.folder: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root: Path = Path(self.folder.name)

    def test_duplicate_checksum_is_rejected(self) -> None:
        path = self.root / "SHA256SUMS"
        path.write_text(("a" * 64 + "  probe.deb\n") * 2)
        with self.assertRaisesRegex(ValueError, "duplicate checksum"):
            repository.checksums(path)

    def test_checksum_paths_are_rejected(self) -> None:
        path = self.root / "SHA256SUMS"
        path.write_text("a" * 64 + "  ../probe.deb\n")
        with self.assertRaisesRegex(ValueError, "invalid"):
            repository.checksums(path)

    def test_corrupt_package_is_rejected_before_inspection(self) -> None:
        (self.root / "probe.deb").write_bytes(b"corrupt")
        (self.root / "manifest.json").write_text(
            json.dumps(
                [
                    {
                        "file": "probe.deb",
                        "sha256": "a" * 64,
                    }
                ]
            )
        )
        with patch.object(repository, "run") as command:
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                repository.copy_packages(self.root, self.root / "output")
            command.assert_not_called()

    def test_input_cannot_escape_its_directory(self) -> None:
        (self.root / "manifest.json").write_text(
            json.dumps([{"file": "../outside.deb"}])
        )
        with self.assertRaisesRegex(ValueError, "escapes"):
            repository.copy_packages(self.root, self.root / "output")

    def test_key_id_is_insufficient(self) -> None:
        with self.assertRaisesRegex(ValueError, "full uppercase"):
            repository.build(
                self.root, self.root / "output", "01234567", "https://example.test"
            )

    def test_uri_cannot_inject_source_fields(self) -> None:
        with self.assertRaisesRegex(ValueError, "HTTPS URL"):
            repository.build(
                self.root,
                self.root / "output",
                "A" * 40,
                "https://example.test\nTrusted: yes",
            )


LINUX_TOOLS: tuple[str, ...] = (
    "dpkg-deb",
    "dpkg-scanpackages",
    "apt-ftparchive",
    "apt-get",
    "gpg",
    "dpkg-query",
)


@unittest.skipUnless(
    all(shutil.which(tool) for tool in LINUX_TOOLS),
    "requires Debian/Ubuntu APT build tools",
)
class AptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.folder: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root: Path = Path(self.folder.name)
        self.root.chmod(0o755)
        home = self.root / "gnupg"
        home.mkdir(mode=0o700)
        environment = patch.dict(
            os.environ, {"GNUPGHOME": str(home), "APT_SIGNING_PASSPHRASE": ""}
        )
        environment.start()
        self.addCleanup(environment.stop)
        repository.run(
            [
                "gpg",
                "--batch",
                "--pinentry-mode",
                "loopback",
                "--passphrase",
                "",
                "--quick-generate-key",
                "APT integration test <apt-test@example.invalid>",
                "rsa2048",
                "sign",
                "1d",
            ]
        )
        keys = repository.run(
            ["gpg", "--batch", "--with-colons", "--list-keys"]
        ).decode()
        self.fingerprint: str = next(
            line.split(":")[9] for line in keys.splitlines() if line.startswith("fpr:")
        )

    def package(self, version: str, architecture: str = "all") -> Path:
        inputs = self.root / f"inputs-{version}-{architecture}"
        inputs.mkdir()
        content = inputs / "package"
        (content / "DEBIAN").mkdir(parents=True)
        (content / "DEBIAN/control").write_text(
            f"Package: ac-apt-probe\nVersion: {version}\nArchitecture: {architecture}\n"
            "Maintainer: Test <apt-test@example.invalid>\nDescription: isolated APT installation probe\n"
        )
        marker = content / "usr/share/ac-apt-probe/version"
        marker.parent.mkdir(parents=True)
        marker.write_text(version)
        path = inputs / "probe.deb"
        repository.run(
            ["dpkg-deb", "--build", "--root-owner-group", str(content), str(path)]
        )
        (inputs / "manifest.json").write_text(
            json.dumps(
                [
                    {
                        "file": path.name,
                        "package": "ac-apt-probe",
                        "version": version,
                        "architecture": architecture,
                        "sha256": repository.digest(path),
                    }
                ]
            )
        )
        return inputs

    def snapshot(self, inputs: Path, name: str, previous: Path | None = None) -> Path:
        output = self.root / name
        repository.build(
            inputs, output, self.fingerprint, "https://example.test", previous
        )
        return output

    def client(self, site: Path) -> list[str]:
        state = self.root / "client"
        state.mkdir(exist_ok=True)
        status = state / "root/var/lib/dpkg/status"
        status.parent.mkdir(parents=True, exist_ok=True)
        status.touch(exist_ok=True)
        source = state / "acture.sources"
        source.write_text(
            f"Types: deb\nURIs: file:{site}\nSuites: stable\nComponents: main\n"
            f"Signed-By: {site}/acture-archive-keyring.asc\n"
        )
        lists = state / "lists"
        archives = state / "archives"
        (lists / "partial").mkdir(parents=True, exist_ok=True)
        (archives / "partial").mkdir(parents=True, exist_ok=True)
        return [
            "apt-get",
            "-o",
            f"Dir::Etc::sourcelist={source}",
            "-o",
            "Dir::Etc::sourceparts=-",
            "-o",
            f"Dir::State::status={status}",
            "-o",
            f"Dir::State::lists={lists}",
            "-o",
            f"Dir::Cache::archives={archives}",
            "-o",
            "Acquire::Languages=none",
            "-o",
            f"DPkg::Options::=--root={state / 'root'}",
            "-o",
            "DPkg::Options::=--force-not-root",
        ]

    def test_signed_install_and_upgrade_preserve_old_packages_and_indexes(self) -> None:
        first = self.snapshot(self.package("1.0"), "first")
        arguments = self.client(first)
        repository.run([*arguments, "update", "--error-on=any"])
        repository.run(
            [*arguments, "install", "-y", "--no-install-recommends", "ac-apt-probe"]
        )
        marker = self.root / "client/root/usr/share/ac-apt-probe/version"
        self.assertEqual(marker.read_text(), "1.0")
        second = self.snapshot(self.package("2.0"), "second", first)
        arguments = self.client(second)
        repository.run([*arguments, "update", "--error-on=any"])
        repository.run(
            [*arguments, "install", "-y", "--no-install-recommends", "ac-apt-probe"]
        )
        self.assertEqual(marker.read_text(), "2.0")
        for old in first.glob("pool/**/*.deb"):
            self.assertEqual(
                repository.digest(old),
                repository.digest(second / old.relative_to(first)),
            )
        for old in first.glob("dists/**/by-hash/SHA256/*"):
            self.assertTrue((second / old.relative_to(first)).is_file())

    def test_tampered_signature_is_rejected_by_apt(self) -> None:
        site = self.snapshot(self.package("1.0"), "site")
        signature = site / "dists/stable/InRelease"
        signature.write_text(
            signature.read_text().replace("Origin: Acture", "Origin: Forged")
        )
        with self.assertRaises(subprocess.CalledProcessError):
            repository.run([*self.client(site), "update", "--error-on=any"])

    def test_architecture_specific_package_does_not_leak_into_other_index(self) -> None:
        site = self.snapshot(self.package("1.0", "amd64"), "site")
        self.assertIn(
            "Package: ac-apt-probe",
            (site / "dists/stable/main/binary-amd64/Packages").read_text(),
        )
        self.assertNotIn(
            "Package: ac-apt-probe",
            (site / "dists/stable/main/binary-arm64/Packages").read_text(),
        )

    def test_existing_version_cannot_be_replaced(self) -> None:
        original = self.package("1.0")
        site = self.snapshot(original, "first")
        artifact = next(site.glob("pool/**/*.deb"))
        artifact.write_bytes(artifact.read_bytes() + b"tampered")
        with self.assertRaisesRegex(ValueError, "previous package checksum mismatch"):
            self.snapshot(self.package("2.0"), "second", site)


if __name__ == "__main__":
    unittest.main()
