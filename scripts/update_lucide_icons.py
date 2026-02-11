#!/usr/bin/env python3
"""Download the latest Lucide icons and bundle as lucide.zip.

Usage:
    python scripts/update_lucide_icons.py

Downloads the latest Lucide release from GitHub, extracts all SVG icons
and the LICENSE file, and writes them to src/rockgarden/icons/lucide.zip.
"""

import io
import json
import urllib.request
import zipfile
from pathlib import Path

GITHUB_API = "https://api.github.com/repos/lucide-icons/lucide/releases/latest"
OUTPUT_PATH = Path("src/rockgarden/icons/lucide.zip")


def get_latest_release_url() -> tuple[str, str]:
    """Get the download URL and tag for the latest Lucide release."""
    req = urllib.request.Request(
        GITHUB_API, headers={"Accept": "application/vnd.github.v3+json"}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    tag = data["tag_name"]
    zipball = data["zipball_url"]
    return zipball, tag


def download_and_build_zip(zipball_url: str) -> bytes:
    """Download the Lucide release and repackage icons into a flat ZIP."""
    print(f"Downloading {zipball_url}...")
    with urllib.request.urlopen(zipball_url) as resp:
        release_data = resp.read()

    output_buf = io.BytesIO()
    icon_count = 0
    has_license = False

    with zipfile.ZipFile(io.BytesIO(release_data)) as src_zip:
        for entry in src_zip.namelist():
            parts = entry.split("/", 1)
            if len(parts) < 2:
                continue
            rel_path = parts[1]

            if rel_path.startswith("icons/") and rel_path.endswith(".svg"):
                icon_name = rel_path.removeprefix("icons/")
                svg_content = src_zip.read(entry)
                with zipfile.ZipFile(
                    output_buf, "a", zipfile.ZIP_DEFLATED, compresslevel=9
                ) as out_zip:
                    out_zip.writestr(icon_name, svg_content)
                icon_count += 1

            elif rel_path == "LICENSE":
                license_content = src_zip.read(entry)
                with zipfile.ZipFile(
                    output_buf, "a", zipfile.ZIP_DEFLATED, compresslevel=9
                ) as out_zip:
                    out_zip.writestr("LICENSE", license_content)
                has_license = True

    print(f"Packaged {icon_count} icons, license included: {has_license}")
    return output_buf.getvalue()


def main():
    zipball_url, tag = get_latest_release_url()
    print(f"Latest Lucide release: {tag}")

    zip_data = download_and_build_zip(zipball_url)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_bytes(zip_data)
    print(f"Written to {OUTPUT_PATH} ({len(zip_data)} bytes)")


if __name__ == "__main__":
    main()
