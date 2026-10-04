#!/usr/bin/env python3
"""Verify and install packages from a snapshot inside clean distribution containers."""

from __future__ import annotations

import argparse
import logging
import re
import subprocess
from pathlib import Path

import repository

LOG: logging.Logger = logging.getLogger(__name__)

COMMAND: str = """set -eu
apt-get update -qq
apt-get install -y -qq --no-install-recommends ca-certificates gnupg
install -D -m 0644 /repository/acture-archive-keyring.asc /etc/apt/keyrings/acture-archive-keyring.asc
gpg --batch --with-colons --show-keys /etc/apt/keyrings/acture-archive-keyring.asc | grep -q \"fpr:::::::::$FINGERPRINT:\"
printf 'Types: deb\\nURIs: %s\\nSuites: stable\\nComponents: main\\nSigned-By: /etc/apt/keyrings/acture-archive-keyring.asc\\n' "$REPOSITORY_URI" >/etc/apt/sources.list.d/acture.sources
apt-get update --error-on=any
apt-get install -y --no-install-recommends \"$PACKAGE\"
\"$PACKAGE\" --version
\"$PACKAGE\" --help >/dev/null
"""


def verify(site: Path, package: str, images: list[str], uri: str | None = None) -> None:
    if re.fullmatch(r"devtunnel-service|trapi2litellm", package) is None:
        raise ValueError("package must be one of the approved service commands")
    fingerprint = (site / "fingerprint.txt").read_text().strip()
    if repository.key_fingerprint(site / "acture-archive-keyring.asc") != fingerprint:
        raise ValueError("snapshot key does not match its published fingerprint")
    source_uri = "file:/repository/" if uri is None else repository.repository_uri(uri)
    for image in images:
        LOG.info("Verifying %s on %s", package, image)
        subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "--volume",
                f"{site.resolve()}:/repository:ro",
                "--env",
                f"FINGERPRINT={fingerprint}",
                "--env",
                f"PACKAGE={package}",
                "--env",
                f"REPOSITORY_URI={source_uri}",
                image,
                "sh",
                "-c",
                COMMAND,
            ],
            check=True,
        )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path)
    parser.add_argument("package", choices=("devtunnel-service", "trapi2litellm"))
    parser.add_argument(
        "--image", choices=("debian:13", "ubuntu:24.04"), action="append"
    )
    parser.add_argument(
        "--uri", help="verify the live HTTPS source using the snapshot key"
    )
    args = parser.parse_args()
    verify(
        args.site, args.package, args.image or ["debian:13", "ubuntu:24.04"], args.uri
    )


if __name__ == "__main__":
    main()
