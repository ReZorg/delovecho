#!/usr/bin/env python3
"""
TC Archive Operations
=====================
Pack and unpack archives using TC-style workflows.

Usage:
    python archive_ops.py pack <source_pattern> <archive.zip> [--level 0-9]
    python archive_ops.py unpack <archive> <target_dir>
    python archive_ops.py list <archive>

Supported formats:
    Pack:   zip
    Unpack: zip, tar, tar.gz, tar.bz2, tar.xz, gz, bz2

Examples:
    python archive_ops.py pack "./docs/*.pdf" backup.zip
    python archive_ops.py pack "./project/" project_backup.zip --level 9
    python archive_ops.py unpack archive.zip ./output/
    python archive_ops.py unpack data.tar.gz ./extracted/
    python archive_ops.py list backup.zip
"""

import os
import sys
import glob
import gzip
import bz2
import zipfile
import tarfile
import argparse
from pathlib import Path
from datetime import datetime


def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:,.0f} {unit}" if unit == 'B' else f"{size:,.1f} {unit}"
        size /= 1024
    return f"{size:,.1f} TB"


def cmd_pack(pattern, archive_path, level=6):
    """Pack files into a ZIP archive."""
    archive_path = Path(archive_path)
    if not archive_path.suffix:
        archive_path = archive_path.with_suffix('.zip')

    # Collect files
    source = Path(pattern)
    if source.is_dir():
        files = sorted(source.rglob('*'))
        files = [f for f in files if f.is_file()]
        base = source
    else:
        files = sorted(Path(p) for p in glob.glob(pattern, recursive=True) if Path(p).is_file())
        base = Path(pattern).parent if files else Path('.')

    if not files:
        print("No files matched pattern.")
        return

    compression = zipfile.ZIP_DEFLATED if level > 0 else zipfile.ZIP_STORED
    total_original = 0
    total_compressed = 0

    with zipfile.ZipFile(archive_path, 'w', compression, compresslevel=level) as zf:
        for f in files:
            arcname = f.relative_to(base) if f.is_relative_to(base) else f.name
            zf.write(f, arcname)
            info = zf.getinfo(str(arcname))
            total_original += info.file_size
            total_compressed += info.compress_size
            ratio = (1 - info.compress_size / info.file_size) * 100 if info.file_size > 0 else 0
            print(f"  + {arcname} ({format_size(info.file_size)} → {format_size(info.compress_size)}, {ratio:.0f}%)")

    overall_ratio = (1 - total_compressed / total_original) * 100 if total_original > 0 else 0
    print(f"\n✓ Packed {len(files)} files into {archive_path.name}")
    print(f"  Original:   {format_size(total_original)}")
    print(f"  Compressed: {format_size(total_compressed)} ({overall_ratio:.0f}% saved)")


def cmd_unpack(archive_path, target_dir):
    """Unpack an archive to target directory."""
    archive_path = Path(archive_path)
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    if not archive_path.exists():
        print(f"Error: {archive_path} not found")
        sys.exit(1)

    name = archive_path.name.lower()
    count = 0

    if name.endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'r') as zf:
            for info in zf.infolist():
                print(f"  ← {info.filename} ({format_size(info.file_size)})")
                count += 1
            zf.extractall(target_dir)

    elif name.endswith(('.tar.gz', '.tgz', '.tar.bz2', '.tbz2', '.tar.xz', '.tar')):
        with tarfile.open(archive_path, 'r:*') as tf:
            members = tf.getmembers()
            for m in members:
                if m.isfile():
                    print(f"  ← {m.name} ({format_size(m.size)})")
                    count += 1
            tf.extractall(target_dir, filter='data')

    elif name.endswith('.gz'):
        out_name = archive_path.stem
        out_path = target_dir / out_name
        with gzip.open(archive_path, 'rb') as f_in:
            with open(out_path, 'wb') as f_out:
                f_out.write(f_in.read())
        print(f"  ← {out_name} ({format_size(out_path.stat().st_size)})")
        count = 1

    elif name.endswith('.bz2'):
        out_name = archive_path.stem
        out_path = target_dir / out_name
        with bz2.open(archive_path, 'rb') as f_in:
            with open(out_path, 'wb') as f_out:
                f_out.write(f_in.read())
        print(f"  ← {out_name} ({format_size(out_path.stat().st_size)})")
        count = 1

    else:
        print(f"Error: Unsupported archive format: {archive_path.suffix}")
        sys.exit(1)

    print(f"\n✓ Unpacked {count} file(s) to {target_dir}")


def cmd_list(archive_path):
    """List contents of an archive."""
    archive_path = Path(archive_path)
    if not archive_path.exists():
        print(f"Error: {archive_path} not found")
        sys.exit(1)

    name = archive_path.name.lower()
    total_size = 0
    count = 0

    print(f"  Archive: {archive_path.name}")
    print(f"  {'Name':<45} {'Size':>10} {'Compressed':>12} {'Ratio':>7}")
    print(f"  {'─' * 76}")

    if name.endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'r') as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                ratio = (1 - info.compress_size / info.file_size) * 100 if info.file_size > 0 else 0
                print(f"  {info.filename:<45} {format_size(info.file_size):>10} {format_size(info.compress_size):>12} {ratio:>6.0f}%")
                total_size += info.file_size
                count += 1

    elif name.endswith(('.tar.gz', '.tgz', '.tar.bz2', '.tbz2', '.tar.xz', '.tar')):
        with tarfile.open(archive_path, 'r:*') as tf:
            for m in tf.getmembers():
                if m.isfile():
                    print(f"  {m.name:<45} {format_size(m.size):>10} {'—':>12} {'—':>7}")
                    total_size += m.size
                    count += 1

    print(f"  {'─' * 76}")
    print(f"  {count} file(s), {format_size(total_size)} total")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TC Archive Operations')
    sub = parser.add_subparsers(dest='command', required=True)

    p_pack = sub.add_parser('pack')
    p_pack.add_argument('source', help='Source files/directory')
    p_pack.add_argument('archive', help='Output archive path')
    p_pack.add_argument('--level', type=int, default=6, help='Compression level 0-9')

    p_unpack = sub.add_parser('unpack')
    p_unpack.add_argument('archive', help='Archive file to unpack')
    p_unpack.add_argument('target', help='Target directory')

    p_list = sub.add_parser('list')
    p_list.add_argument('archive', help='Archive file to list')

    args = parser.parse_args()

    if args.command == 'pack':
        cmd_pack(args.source, args.archive, args.level)
    elif args.command == 'unpack':
        cmd_unpack(args.archive, args.target)
    elif args.command == 'list':
        cmd_list(args.archive)
