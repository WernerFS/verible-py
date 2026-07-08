#!/usr/bin/env python3
"""Regenerate the verible download_scripts block in setup.cfg."""
from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.request

REPO = "chipsalliance/verible"
TOOLS = ("verible-verilog-lint", "verible-verilog-format")

PLATFORMS = (
    {
        "asset": "linux-static-x86_64.tar.gz",
        "extract": "tar",
        "suffix": "",
        "archive_root": "verible-{tag}",
        "bindir": "bin/",
        "markers": (
            'sys_platform == "linux" and platform_machine == "x86_64"',
        ),
    },
    {
        "asset": "linux-static-arm64.tar.gz",
        "extract": "tar",
        "suffix": "",
        "archive_root": "verible-{tag}",
        "bindir": "bin/",
        "markers": (
            'sys_platform == "linux" and platform_machine == "arm64"',
        ),
    },
    {
        "asset": "win64.zip",
        "extract": "zip",
        "suffix": ".exe",
        "archive_root": "verible-{tag}-win64",
        "bindir": "",
        "markers": (
            'sys_platform == "win32" and platform_machine == "AMD64"',
            'sys_platform == "cygwin" and platform_machine == "x86_64"',
        ),
    },
    {
        "asset": "macOS.tar.gz",
        "extract": "tar",
        "suffix": "",
        "archive_root": "verible-{tag}",
        "bindir": "bin/",
        "markers": ('sys_platform == "darwin"',),
    },
)


def api(url):
    req = urllib.request.Request(url)
    if tok := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req) as f:
        return json.load(f)


def sha256(url):
    h = hashlib.sha256()
    with urllib.request.urlopen(url) as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    rel = api(f"https://api.github.com/repos/{REPO}/releases")[0]
    tag = rel["tag_name"]
    assets = {a["name"]: a for a in rel["assets"]}

    lines = []
    for tool in TOOLS:
        for p in PLATFORMS:
            a = assets[f"verible-{tag}-{p['asset']}"]
            url = a["browser_download_url"]
            digest = a.get("digest", "")
            h = digest[7:] if digest.startswith("sha256:") else sha256(url)
            root = p["archive_root"].format(tag=tag)
            out = f"{tool}{p['suffix']}"
            lines += [
                f"    [{out}]",
                f"    group = {tool}",
                *(f"    marker = {m}" for m in p["markers"]),
                f"    url = {url}",
                f"    sha256 = {h}",
                f"    extract = {p['extract']}",
                f"    extract_path = {root}/{p['bindir']}{out}",
            ]

    block = "[setuptools_download]\ndownload_scripts =\n" + "\n".join(lines)

    cfg = open("setup.cfg").read()
    cfg = re.sub(
        r"^\[setuptools_download\].*?(?=^\[|\Z)",
        lambda _: f"{block}\n", cfg, flags=re.DOTALL | re.MULTILINE
    )

    cfg = re.sub(
        r"^version = .*",
        lambda _: f"version = {tag}", cfg, flags=re.MULTILINE,
    )
    open("setup.cfg", "w").write(cfg)

    if gh_env := os.environ.get("GITHUB_ENV"):
        with open(gh_env, "a") as f:
            f.write(f"VERIBLE_VERSION={tag}\n")


if __name__ == "__main__":
    raise SystemExit(main())
