#!/usr/bin/env python3
"""Fetch and verify the official PostgreSQL documentation source archives.

The archives remain under ignored ``data/raw`` and are extracted under ignored
``data/processed``.  The published sidecar SHA-256 file is always checked before
the archive is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tarfile
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

VERSIONS = {
    "15": {
        "release": "15.19",
        "url": "https://ftp.postgresql.org/pub/source/v15.19/postgresql-15.19.tar.gz",
        "sha256": "4bf5474f0ee4afc55de5e71fb5cc8cd133ee56cd1bf16092093897b7c93328fb",
    },
    "16": {
        "release": "16.15",
        "url": "https://ftp.postgresql.org/pub/source/v16.15/postgresql-16.15.tar.gz",
        "sha256": "4f200ca23dfb120ff9838f13ce06014aad1d3c432d16ee9f93ab2000c0eeef7b",
    },
    "17": {
        "release": "17.11",
        "url": "https://ftp.postgresql.org/pub/source/v17.11/postgresql-17.11.tar.gz",
        "sha256": "5367f6fb2ec97efe1eb2e0c7926bb33438e51b0bd3a9733b88498056a7dc9a7e",
    },
}
USER_AGENT = "evidence-rag-phase3/1.0 (documentation benchmark; polite bulk download)"


def _download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as handle:
        shutil.copyfileobj(response, handle, length=1024 * 1024)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch_version(version: str, raw_dir: Path, processed_dir: Path) -> dict[str, str]:
    config = VERSIONS[version]
    archive = raw_dir / f"postgresql-{config['release']}.tar.gz"
    raw_dir.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        print(f"downloading pg-{version}: {config['url']}")
        _download(config["url"], archive)
    actual = _sha256(archive)
    if actual != config["sha256"]:
        raise RuntimeError(f"checksum mismatch for pg-{version}: {actual} != {config['sha256']}")
    destination = processed_dir / f"pg-{version}"
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as tar:
        prefix = f"postgresql-{config['release']}/doc/src/sgml/"
        members = [member for member in tar.getmembers() if member.name.startswith(prefix)]
        if not members:
            raise RuntimeError(f"documentation SGML not found in {archive}")
        tar.extractall(destination, members=members, filter="data")
    return {
        "version": f"pg-{version}",
        "release": config["release"],
        "source_url": config["url"],
        "sha256": actual,
        "retrieved_at_utc": datetime.now(UTC).isoformat(),
        "archive": str(archive),
        "extracted": str(destination),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--versions", nargs="+", choices=sorted(VERSIONS), default=sorted(VERSIONS))
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/postgresql"))
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed/postgresql"))
    parser.add_argument("--manifest", type=Path, default=Path("data/source-manifest.json"))
    args = parser.parse_args()
    entries = [
        fetch_version(version, args.raw_dir, args.processed_dir) for version in args.versions
    ]
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(entries, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"verified {len(entries)} PostgreSQL source archives")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
