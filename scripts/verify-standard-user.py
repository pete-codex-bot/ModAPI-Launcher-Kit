#!/usr/bin/env python3
"""Static source and PE-resource checks for the standard-user variants."""

from __future__ import annotations

import argparse
import hashlib
import re
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    ROOT / "Spore ModAPI Easy Installer" / "EasyInstaller.cs",
    ROOT / "Spore ModAPI Easy Uninstaller" / "EasyUninstaller.cs",
)
EXECUTABLES = (
    "Spore ModAPI Easy Installer.exe",
    "Spore ModAPI Easy Uninstaller.exe",
)


def fail(message: str) -> None:
    raise ValueError(message)


def verify_sources() -> None:
    for source in SOURCES:
        text = source.read_text(encoding="utf-8-sig")
        if "Permissions.RerunAsAdministrator" in text:
            fail(f"elevation call remains in {source.relative_to(ROOT)}")
        if re.search(r'Verb\s*=\s*["\']runas["\']', text, re.IGNORECASE):
            fail(f"direct runas verb remains in {source.relative_to(ROOT)}")


def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def extract_manifest(data: bytes, filename: str) -> str:
    if data[:2] != b"MZ":
        fail(f"{filename} is not a PE executable (missing MZ header)")
    pe_offset = u32(data, 0x3C)
    if data[pe_offset : pe_offset + 4] != b"PE\0\0":
        fail(f"{filename} is not a PE executable (missing PE header)")

    coff = pe_offset + 4
    section_count = u16(data, coff + 2)
    optional_size = u16(data, coff + 16)
    optional = coff + 20
    magic = u16(data, optional)
    if magic == 0x10B:
        data_directories = optional + 96
    elif magic == 0x20B:
        data_directories = optional + 112
    else:
        fail(f"{filename} has an unsupported PE optional-header format")

    resource_rva = u32(data, data_directories + (2 * 8))
    if resource_rva == 0:
        fail(f"{filename} has no PE resource directory")

    sections = []
    section_table = optional + optional_size
    for index in range(section_count):
        entry = section_table + (index * 40)
        virtual_size = u32(data, entry + 8)
        virtual_address = u32(data, entry + 12)
        raw_size = u32(data, entry + 16)
        raw_pointer = u32(data, entry + 20)
        sections.append((virtual_address, max(virtual_size, raw_size), raw_pointer))

    def rva_to_offset(rva: int) -> int:
        for virtual_address, size, raw_pointer in sections:
            if virtual_address <= rva < virtual_address + size:
                return raw_pointer + (rva - virtual_address)
        fail(f"{filename} contains an unmapped resource RVA 0x{rva:x}")

    resource_base = rva_to_offset(resource_rva)

    def directory_entries(relative_offset: int):
        directory = resource_base + relative_offset
        count = u16(data, directory + 12) + u16(data, directory + 14)
        for index in range(count):
            entry = directory + 16 + (index * 8)
            yield u32(data, entry), u32(data, entry + 4)

    manifest_branch = None
    for identifier, child in directory_entries(0):
        if not identifier & 0x80000000 and identifier == 24:  # RT_MANIFEST
            manifest_branch = child
            break
    if manifest_branch is None or not manifest_branch & 0x80000000:
        fail(f"{filename} has no RT_MANIFEST resource")

    child = manifest_branch
    for _ in range(2):  # resource name, then language
        entries = list(directory_entries(child & 0x7FFFFFFF))
        if not entries:
            fail(f"{filename} has an empty RT_MANIFEST resource tree")
        child = entries[0][1]

    if child & 0x80000000:
        fail(f"{filename} has an unexpected RT_MANIFEST resource layout")
    data_entry = resource_base + child
    manifest_rva = u32(data, data_entry)
    manifest_size = u32(data, data_entry + 4)
    payload = data[rva_to_offset(manifest_rva) : rva_to_offset(manifest_rva) + manifest_size]

    if payload.startswith((b"\xff\xfe", b"\xfe\xff")) or b"\0<\0" in payload[:16]:
        return payload.decode("utf-16")
    return payload.decode("utf-8-sig")


def verify_hashes(artifact_dir: Path) -> None:
    hash_file = artifact_dir / "SHA256SUMS.txt"
    if not hash_file.is_file():
        fail(f"missing {hash_file}")
    expected = {}
    for line in hash_file.read_text(encoding="utf-8-sig").splitlines():
        digest, name = line.split(maxsplit=1)
        expected[name.strip()] = digest.lower()
    for name, digest in expected.items():
        path = artifact_dir / name
        if not path.is_file():
            fail(f"hash list references missing file: {path}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            fail(f"SHA-256 mismatch for {path}")


def verify_binaries(artifact_dir: Path) -> None:
    verify_hashes(artifact_dir)
    for name in EXECUTABLES:
        path = artifact_dir / name
        if not path.is_file():
            fail(f"missing executable: {path}")
        data = path.read_bytes()
        manifest = extract_manifest(data, name)
        if not re.search(r'requestedExecutionLevel\s+level=["\']asInvoker["\']', manifest):
            fail(f"{name} does not request asInvoker")
        if re.search(r'level=["\'](?:requireAdministrator|highestAvailable)["\']', manifest):
            fail(f"{name} contains an elevated requestedExecutionLevel")
        if b"RerunAsAdministrator" in data or "RerunAsAdministrator".encode("utf-16le") in data:
            fail(f"{name} still references RerunAsAdministrator in its .NET metadata")
        if re.search(rb"(?i)(?<![a-z])runas(?![a-z])", data):
            fail(f"{name} unexpectedly contains a runas string")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_dir", nargs="?", type=Path)
    parser.add_argument("--source-only", action="store_true")
    args = parser.parse_args()

    try:
        verify_sources()
        print("PASS: installer and uninstaller source contain no elevation call or direct runas verb")
        if not args.source_only:
            if args.artifact_dir is None:
                parser.error("artifact_dir is required unless --source-only is used")
            verify_binaries(args.artifact_dir.resolve())
            print("PASS: both PE executables request asInvoker and contain no elevation reference")
            print("PASS: artifact SHA-256 hashes match")
    except (OSError, UnicodeError, ValueError, struct.error) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
