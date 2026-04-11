#!/usr/bin/env python3
"""
TC File Search
==============
Search for files using Total Commander's search syntax.

Usage:
    python tc_search.py <directory> <pattern> [options]

Supports:
    - Wildcards: *, ?
    - Exclusion: "* | *.log temp/"  (pipe separates includes from excludes)
    - Depth limit: "D:2 *.txt"  (search max 2 levels deep)
    - Text search: --containing "search text"
    - Regex: --regex "^report.*v[0-9]+"
    - Size filter: --min-size 1KB  --max-size 10MB
    - Date filter: --not-older-than 7d  (d=days, h=hours, m=minutes)
    - Hidden files: --show-hidden

Examples:
    python tc_search.py /home/ubuntu "*.pdf"
    python tc_search.py /home/ubuntu "* | *.log *.tmp"
    python tc_search.py /home/ubuntu "*.py" --containing "import os"
    python tc_search.py /home/ubuntu "D:2 *.txt" --not-older-than 30d
    python tc_search.py /home/ubuntu --regex "^IMG_\\d{8}"
"""

import os
import re
import sys
import fnmatch
import argparse
from pathlib import Path
from datetime import datetime, timedelta


def parse_size(size_str):
    """Parse size string like 1KB, 10MB, 1GB to bytes."""
    units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
    size_str = size_str.upper().strip()
    for unit, multiplier in sorted(units.items(), key=lambda x: -len(x[0])):
        if size_str.endswith(unit):
            return int(float(size_str[:-len(unit)]) * multiplier)
    return int(size_str)


def parse_age(age_str):
    """Parse age string like 7d, 24h, 30m to timedelta."""
    unit = age_str[-1].lower()
    value = int(age_str[:-1])
    if unit == 'd':
        return timedelta(days=value)
    elif unit == 'h':
        return timedelta(hours=value)
    elif unit == 'm':
        return timedelta(minutes=value)
    raise ValueError(f"Unknown time unit: {unit}")


def tc_search(directory, pattern='*', containing=None, regex=None,
              min_size=None, max_size=None, not_older_than=None,
              show_hidden=False, case_sensitive=False):
    """Search files using TC-style syntax."""
    directory = Path(directory)
    if not directory.is_dir():
        print(f"Error: {directory} is not a directory")
        sys.exit(1)

    # Parse depth limit
    max_depth = None
    depth_match = re.match(r'D:(\d+)\s+(.+)', pattern)
    if depth_match:
        max_depth = int(depth_match.group(1))
        pattern = depth_match.group(2)

    # Parse exclusion pattern
    include_patterns = [pattern]
    exclude_patterns = []
    exclude_dirs = []
    if '|' in pattern:
        parts = pattern.split('|', 1)
        include_patterns = parts[0].strip().split()
        excludes = parts[1].strip().split()
        for ex in excludes:
            if ex.endswith('/'):
                exclude_dirs.append(ex.rstrip('/'))
            else:
                exclude_patterns.append(ex)

    # Collect files
    results = []
    now = datetime.now()

    for root, dirs, files in os.walk(directory):
        rel_root = Path(root).relative_to(directory)
        depth = len(rel_root.parts) if str(rel_root) != '.' else 0

        if max_depth is not None and depth > max_depth:
            dirs.clear()
            continue

        # Exclude directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        if not show_hidden:
            dirs[:] = [d for d in dirs if not d.startswith('.')]

        for fname in files:
            if not show_hidden and fname.startswith('.'):
                continue

            filepath = Path(root) / fname

            # Include pattern match
            matched = any(fnmatch.fnmatch(fname, p) for p in include_patterns)
            if not matched:
                continue

            # Exclude pattern match
            excluded = any(fnmatch.fnmatch(fname, p) for p in exclude_patterns)
            if excluded:
                continue

            # Size filters
            try:
                stat = filepath.stat()
            except OSError:
                continue

            if min_size is not None and stat.st_size < min_size:
                continue
            if max_size is not None and stat.st_size > max_size:
                continue

            # Date filter
            if not_older_than is not None:
                mtime = datetime.fromtimestamp(stat.st_mtime)
                if now - mtime > not_older_than:
                    continue

            # Regex filter on filename
            if regex:
                flags = 0 if case_sensitive else re.IGNORECASE
                if not re.search(regex, fname, flags):
                    continue

            # Text content search
            if containing:
                try:
                    text = filepath.read_text(errors='ignore')
                    if case_sensitive:
                        if containing not in text:
                            continue
                    else:
                        if containing.lower() not in text.lower():
                            continue
                except (OSError, UnicodeDecodeError):
                    continue

            results.append(filepath)

    return sorted(results)


def format_size(size):
    """Format byte size to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:,.0f} {unit}" if unit == 'B' else f"{size:,.1f} {unit}"
        size /= 1024
    return f"{size:,.1f} TB"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TC File Search')
    parser.add_argument('directory', help='Directory to search')
    parser.add_argument('pattern', nargs='?', default='*', help='File pattern (TC syntax)')
    parser.add_argument('--containing', help='Search for text inside files')
    parser.add_argument('--regex', help='Regex pattern for filenames')
    parser.add_argument('--min-size', help='Minimum file size (e.g. 1KB, 10MB)')
    parser.add_argument('--max-size', help='Maximum file size (e.g. 100MB)')
    parser.add_argument('--not-older-than', help='Max age (e.g. 7d, 24h, 30m)')
    parser.add_argument('--show-hidden', action='store_true', help='Include hidden files')
    parser.add_argument('--case-sensitive', action='store_true')
    args = parser.parse_args()

    min_size = parse_size(args.min_size) if args.min_size else None
    max_size = parse_size(args.max_size) if args.max_size else None
    not_older = parse_age(args.not_older_than) if args.not_older_than else None

    results = tc_search(args.directory, args.pattern, args.containing, args.regex,
                        min_size, max_size, not_older, args.show_hidden, args.case_sensitive)

    if results:
        base = Path(args.directory)
        for f in results:
            stat = f.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
            size = format_size(stat.st_size)
            rel = f.relative_to(base)
            print(f"{mtime}  {size:>10}  {rel}")
        print(f"\n{len(results)} file(s) found.")
    else:
        print("No files found.")
