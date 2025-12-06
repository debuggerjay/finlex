#!/usr/bin/env python3
"""
Download relevant Finlex open data archives for AI agent use.

Datasets:
- statute-consolidated.zip (3.6 GB) - Current Finnish law
- legal-literature-references.zip (284 MB) - Case law references
- chancellor-of-justice-decision.zip (204 MB) - Chancellor decisions
- data-protection-ombudsman-decision.zip (3.2 MB) - GDPR/privacy decisions
- tax-treaty-consolidated.zip (3.8 MB) - Tax treaties
"""

import os
import sys
import zipfile
import hashlib
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

BASE_URL = "https://www.finlex.fi/api/assets/open-data/archives"

# Relevant datasets for AI agent
DATASETS = {
    "statute-consolidated": {
        "url": f"{BASE_URL}/statute-consolidated.zip",
        "description": "Ajantasaistettu lainsäädäntö (Current Finnish law)",
        "size_approx": "3.6 GB",
    },
    "legal-literature-references": {
        "url": f"{BASE_URL}/legal-literature-references.zip",
        "description": "Oikeuskäytäntö kirjallisuudessa (Case law references)",
        "size_approx": "284 MB",
    },
    "chancellor-of-justice-decision": {
        "url": f"{BASE_URL}/chancellor-of-justice-decision.zip",
        "description": "Valtioneuvoston oikeuskansleri (Chancellor decisions)",
        "size_approx": "204 MB",
    },
    "data-protection-ombudsman-decision": {
        "url": f"{BASE_URL}/data-protection-ombudsman-decision.zip",
        "description": "Tietosuojavaltuutetun päätökset (Data protection decisions)",
        "size_approx": "3.2 MB",
    },
    "tax-treaty-consolidated": {
        "url": f"{BASE_URL}/tax-treaty-consolidated.zip",
        "description": "Tuloverosopimukset (Tax treaties)",
        "size_approx": "3.8 MB",
    },
}


def format_size(bytes_size: int) -> str:
    """Format bytes to human readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def download_file(url: str, dest_path: Path, chunk_size: int = 8192) -> bool:
    """Download a file with progress indication."""
    try:
        req = Request(url, headers={"User-Agent": "Finlex-Downloader/1.0"})
        with urlopen(req, timeout=30) as response:
            total_size = int(response.headers.get("Content-Length", 0))
            downloaded = 0

            with open(dest_path, "wb") as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        bar_len = 40
                        filled = int(bar_len * downloaded / total_size)
                        bar = "█" * filled + "░" * (bar_len - filled)
                        sys.stdout.write(
                            f"\r  [{bar}] {percent:5.1f}% ({format_size(downloaded)}/{format_size(total_size)})"
                        )
                        sys.stdout.flush()

            print()  # newline after progress bar
            return True

    except HTTPError as e:
        print(f"\n  ❌ HTTP Error {e.code}: {e.reason}")
        return False
    except URLError as e:
        print(f"\n  ❌ URL Error: {e.reason}")
        return False
    except Exception as e:
        print(f"\n  ❌ Error: {e}")
        return False


def extract_zip(zip_path: Path, extract_to: Path) -> bool:
    """Extract a zip file."""
    try:
        print(f"  📦 Extracting to {extract_to}/")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_to)
        return True
    except zipfile.BadZipFile:
        print(f"  ❌ Bad zip file: {zip_path}")
        return False
    except Exception as e:
        print(f"  ❌ Extract error: {e}")
        return False


def main():
    print("=" * 60)
    print("Finlex Open Data Downloader")
    print("Source: https://www.finlex.fi/fi/avoin-data/lataa-aineistoja")
    print("=" * 60)
    print()

    # Create directories
    archives_dir = Path("archives")
    data_dir = Path("data")
    archives_dir.mkdir(exist_ok=True)
    data_dir.mkdir(exist_ok=True)

    print(f"Datasets to download: {len(DATASETS)}")
    print()

    for name, info in DATASETS.items():
        print(f"📥 {name}")
        print(f"   {info['description']}")
        print(f"   Size: ~{info['size_approx']}")

        zip_path = archives_dir / f"{name}.zip"
        extract_path = data_dir / name

        # Check if already extracted
        if extract_path.exists() and any(extract_path.iterdir()):
            print(f"  ✅ Already extracted, skipping.")
            print()
            continue

        # Download if not present
        if not zip_path.exists():
            print(f"  ⬇️  Downloading...")
            if not download_file(info["url"], zip_path):
                print()
                continue
        else:
            print(f"  ✅ Archive exists: {zip_path}")

        # Extract
        extract_path.mkdir(parents=True, exist_ok=True)
        if extract_zip(zip_path, extract_path):
            print(f"  ✅ Done!")
            # Optionally remove zip after extraction to save space
            # zip_path.unlink()
        print()

    print("=" * 60)
    print("Download complete!")
    print(f"Archives saved to: {archives_dir.absolute()}")
    print(f"Extracted data in: {data_dir.absolute()}")
    print("=" * 60)


if __name__ == "__main__":
    main()

