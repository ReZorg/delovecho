#!/usr/bin/env python3
"""
TC Multi-Rename Tool
====================
Batch-rename files using Total Commander's placeholder syntax.

Usage:
    python multi_rename.py <directory> <pattern> [--ext <ext_pattern>] [--dry-run] [--recursive]

Placeholders:
    [N]         Original name (no extension)
    [N1-3]      Characters 1-3 of name
    [N2,5]      5 characters starting at position 2
    [N-5-]      From 5th-last character to end
    [A]         Full name with extension
    [E]         Extension (without dot)
    [C]         Counter (default: start=1, step=1)
    [C10+5:3]   Counter: start=10, step=5, width=3
    [C:a]       Counter: auto-width based on file count
    [P]         Parent directory name
    [G]         Grandparent directory name
    [Y],[M],[D] Year(4), Month(2), Day(2) from file mtime
    [h],[m],[s] Hours(24h,2), Minutes(2), Seconds(2) from file mtime
    [U]         Uppercase from this position onward
    [L]         Lowercase from this position onward
    [F]         Title Case from this position onward
    [S]         File size in bytes

Examples:
    # Simple counter rename
    python multi_rename.py ./photos "[N]_[C:3].[E]"

    # Date-based rename
    python multi_rename.py ./photos "Photo_[Y]-[M]-[D]_[C:2].[E]"

    # Lowercase everything
    python multi_rename.py ./docs "[L][N].[E]"

    # Distribute into subfolders (3 per folder)
    python multi_rename.py ./images "[C+1/3]/[N].[E]"

    # Dry run to preview
    python multi_rename.py ./photos "[N]_[C:3].[E]" --dry-run
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime


def parse_counter_spec(spec):
    """Parse counter spec like C, C10+5:3, C:a, C+1/100"""
    start, step, width, every = 1, 1, 0, 1
    auto_width = False

    if not spec:
        return start, step, width, every, auto_width

    # Parse fractional: +1/100
    frac_match = re.search(r'\+(\d+)/(\d+)', spec)
    if frac_match:
        step = int(frac_match.group(1))
        every = int(frac_match.group(2))
        spec = spec[:frac_match.start()] + spec[frac_match.end():]

    # Parse start
    start_match = re.match(r'^(\d+)', spec)
    if start_match:
        start = int(start_match.group(1))
        spec = spec[start_match.end():]

    # Parse step (if not already parsed from fractional)
    if every == 1:
        step_match = re.match(r'\+(\d+)', spec)
        if step_match:
            step = int(step_match.group(1))
            spec = spec[step_match.end():]

    # Parse width
    width_match = re.search(r':(\d+|a)', spec)
    if width_match:
        if width_match.group(1) == 'a':
            auto_width = True
        else:
            width = int(width_match.group(1))

    return start, step, width, every, auto_width


def extract_name_part(name, range_spec):
    """Extract characters from name based on TC range spec like N1-3, N2,5, N-5-"""
    if not range_spec:
        return name

    # N-8,5 = 5 chars starting at 8th-last
    m = re.match(r'-(\d+),(\d+)', range_spec)
    if m:
        pos = len(name) - int(m.group(1))
        count = int(m.group(2))
        return name[max(0, pos):pos + count]

    # N-8-5 = from 8th-last to 5th-last
    m = re.match(r'-(\d+)-(\d+)', range_spec)
    if m:
        start = len(name) - int(m.group(1))
        end = len(name) - int(m.group(2)) + 1
        return name[max(0, start):end]

    # N2--5 = from 2nd to 5th-last
    m = re.match(r'(\d+)--(\d+)', range_spec)
    if m:
        start = int(m.group(1)) - 1
        end = len(name) - int(m.group(2)) + 1
        return name[start:end]

    # N-5- = from 5th-last to end
    m = re.match(r'-(\d+)-$', range_spec)
    if m:
        pos = len(name) - int(m.group(1))
        return name[max(0, pos):]

    # N2-5 = characters 2 to 5
    m = re.match(r'(\d+)-(\d+)', range_spec)
    if m:
        return name[int(m.group(1)) - 1:int(m.group(2))]

    # N2- = all from position 2
    m = re.match(r'(\d+)-$', range_spec)
    if m:
        return name[int(m.group(1)) - 1:]

    # N2,5 = 5 chars starting at 2
    m = re.match(r'(\d+),(\d+)', range_spec)
    if m:
        start = int(m.group(1)) - 1
        count = int(m.group(2))
        return name[start:start + count]

    # N1 = single character
    m = re.match(r'(\d+)$', range_spec)
    if m:
        idx = int(m.group(1)) - 1
        return name[idx] if idx < len(name) else ''

    return name


def apply_pattern(pattern, filepath, counter_val, counter_width, file_count):
    """Apply TC rename pattern to a single file."""
    p = Path(filepath)
    name = p.stem
    ext = p.suffix[1:] if p.suffix else ''
    full_name = p.name
    parent = p.parent.name
    grandparent = p.parent.parent.name if p.parent.parent != p.parent else ''
    stat = p.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime)
    size = stat.st_size

    result = ''
    case_mode = None  # None, 'upper', 'lower', 'title'
    i = 0

    while i < len(pattern):
        if pattern[i] == '[' and i + 1 < len(pattern):
            # Find closing bracket
            end = pattern.index(']', i + 1) if ']' in pattern[i + 1:] else -1
            if end == -1:
                result += pattern[i]
                i += 1
                continue

            token = pattern[i + 1:end]
            replacement = ''

            if token == '[':
                replacement = '['
            elif token == ']':
                replacement = ']'
            elif token == 'U':
                case_mode = 'upper'
            elif token == 'L':
                case_mode = 'lower'
            elif token == 'F' or token == 'f':
                case_mode = 'title'
            elif token == 'n':
                case_mode = None
            elif token.startswith('N'):
                replacement = extract_name_part(name, token[1:])
            elif token.startswith('A'):
                replacement = extract_name_part(full_name, token[1:])
            elif token.startswith('E'):
                replacement = extract_name_part(ext, token[1:])
            elif token.startswith('P'):
                replacement = extract_name_part(parent, token[1:])
            elif token.startswith('G'):
                replacement = extract_name_part(grandparent, token[1:])
            elif token.startswith('C'):
                spec = token[1:]
                start, step, width, every, auto_width = parse_counter_spec(spec)
                if auto_width:
                    width = len(str(file_count))
                val = counter_val
                if width > 0:
                    replacement = str(val).zfill(width)
                else:
                    replacement = str(val)
            elif token == 'S':
                replacement = str(size)
            elif token == 'Y':
                replacement = mtime.strftime('%Y')
            elif token == 'y':
                replacement = mtime.strftime('%y')
            elif token == 'M':
                replacement = mtime.strftime('%m')
            elif token == 'D':
                replacement = mtime.strftime('%d')
            elif token == 'h':
                replacement = mtime.strftime('%H')
            elif token == 'H':
                replacement = mtime.strftime('%I')
            elif token == 'm':
                replacement = mtime.strftime('%M')
            elif token == 's':
                replacement = mtime.strftime('%S')
            elif token == 'd':
                replacement = mtime.strftime('%Y-%m-%d')
            elif token == 't':
                replacement = mtime.strftime('%H.%M.%S')
            elif token.startswith('T'):
                pass  # Time source switches — no output
            elif token.startswith('R'):
                import random
                digits = int(token[1:]) if len(token) > 1 else 6
                replacement = str(random.randint(10 ** (digits - 1), 10 ** digits - 1))

            # Apply case mode
            if replacement and case_mode:
                if case_mode == 'upper':
                    replacement = replacement.upper()
                elif case_mode == 'lower':
                    replacement = replacement.lower()
                elif case_mode == 'title':
                    replacement = replacement.title()

            result += replacement
            i = end + 1
        else:
            char = pattern[i]
            if case_mode == 'upper':
                char = char.upper()
            elif case_mode == 'lower':
                char = char.lower()
            result += char
            i += 1

    return result


def multi_rename(directory, pattern, ext_pattern=None, dry_run=False, recursive=False):
    """Batch rename files in directory using TC pattern syntax."""
    directory = Path(directory)
    if not directory.is_dir():
        print(f"Error: {directory} is not a directory")
        sys.exit(1)

    if recursive:
        files = sorted([f for f in directory.rglob('*') if f.is_file()])
    else:
        files = sorted([f for f in directory.iterdir() if f.is_file()])

    # Filter by extension pattern if given
    if ext_pattern:
        import fnmatch
        files = [f for f in files if fnmatch.fnmatch(f.name, ext_pattern)]

    if not files:
        print("No files matched.")
        return

    # Parse counter spec from pattern
    counter_match = re.search(r'\[C([^\]]*)\]', pattern)
    start, step, width, every, auto_width = 1, 1, 0, 1, False
    if counter_match:
        start, step, width, every, auto_width = parse_counter_spec(counter_match.group(1))

    if auto_width:
        width = len(str(len(files)))

    renames = []
    counter_val = start
    for idx, filepath in enumerate(files):
        new_name = apply_pattern(pattern, filepath, counter_val, width, len(files))
        new_path = filepath.parent / new_name
        renames.append((filepath, new_path))

        if (idx + 1) % every == 0:
            counter_val += step

    # Display plan
    max_old = max(len(f.name) for f, _ in renames)
    print(f"{'Original':<{max_old + 2}} → New Name")
    print("─" * (max_old + 40))
    for old, new in renames:
        print(f"{old.name:<{max_old + 2}} → {new.name}")

    if dry_run:
        print(f"\n[DRY RUN] {len(renames)} files would be renamed.")
        return

    # Execute renames
    for old, new in renames:
        new.parent.mkdir(parents=True, exist_ok=True)
        old.rename(new)

    print(f"\n✓ {len(renames)} files renamed.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TC Multi-Rename Tool')
    parser.add_argument('directory', help='Directory containing files to rename')
    parser.add_argument('pattern', help='TC rename pattern (e.g. "[N]_[C:3].[E]")')
    parser.add_argument('--ext', help='Filter files by pattern (e.g. "*.jpg")')
    parser.add_argument('--dry-run', action='store_true', help='Preview without renaming')
    parser.add_argument('--recursive', action='store_true', help='Include subdirectories')
    args = parser.parse_args()

    multi_rename(args.directory, args.pattern, args.ext, args.dry_run, args.recursive)
