---
name: tc
description: "Total Commander file management operations: batch rename, search, copy/move, archive pack/unpack, directory tree, and file properties. Use when performing bulk file operations, organizing files with pattern-based renaming, searching with wildcards/regex/content filters, packing or unpacking archives (ZIP, TAR, GZ, 7z), or inspecting file/folder properties and disk usage."
---

# TC -- File Manager

Perform file management operations inspired by Total Commander's dual-panel workflow. Provides scripts for batch rename, search, copy/move, archive operations, directory tree, and file properties.

## Workflow

Determine the operation type:

- **Batch rename files?** --> Use `multi_rename.py` (Multi-Rename section)
- **Search for files?** --> Use `tc_search.py` (Search section)
- **Copy, move, delete, or inspect files?** --> Use `file_ops.py` (File Operations section)
- **Pack or unpack archives?** --> Use `archive_ops.py` (Archive Operations section)

## Multi-Rename

Batch-rename files using TC's placeholder syntax. Always use `--dry-run` first to preview.

```bash
python /home/ubuntu/skills/tc/scripts/multi_rename.py <directory> <pattern> [--ext "*.jpg"] [--dry-run] [--recursive]
```

### Core Placeholders

| Placeholder | Meaning | Example |
|-------------|---------|---------|
| `[N]` | Name (no extension) | `photo` |
| `[N1-3]` | Characters 1-3 of name | `pho` |
| `[E]` | Extension | `jpg` |
| `[C:3]` | Counter, 3-digit width | `001` |
| `[Y]` `[M]` `[D]` | Year, month, day (from mtime) | `2025` `01` `15` |
| `[h]` `[m]` `[s]` | Hours, minutes, seconds | `14` `30` `00` |
| `[U]` | UPPERCASE from here | `PHOTO.JPG` |
| `[L]` | lowercase from here | `photo.jpg` |
| `[F]` | Title Case from here | `Photo.Jpg` |
| `[P]` | Parent directory name | `vacation` |
| `[S]` | File size in bytes | `1048576` |
| `[R5]` | Random 5-digit number | `48271` |

### Examples

```bash
# Number photos sequentially
python .../multi_rename.py ./photos "[N]_[C:3].[E]" --dry-run
# photo.jpg --> photo_001.jpg

# Date-based rename
python .../multi_rename.py ./photos "Photo_[Y]-[M]-[D]_[C:2].[E]" --ext "*.jpg" --dry-run
# --> Photo_2025-01-15_01.jpg

# Lowercase all filenames
python .../multi_rename.py ./docs "[L][N].[E]" --dry-run

# Distribute into subfolders (3 per folder)
python .../multi_rename.py ./images "[C+1/3]/[N].[E]" --dry-run
```

**Full placeholder reference:** See `references/multi-rename.md` for all range variants, counter options, date/time switches, and advanced patterns.

## Search

Search for files using wildcards, regex, content filters, size/date constraints, and exclusion patterns.

```bash
python /home/ubuntu/skills/tc/scripts/tc_search.py <directory> <pattern> [options]
```

### Options

| Option | Description | Example |
|--------|-------------|---------|
| `pattern` | Wildcard pattern (TC syntax) | `*.pdf`, `report_202?*` |
| `"* \| *.log temp/"` | Exclude patterns after pipe | Exclude .log and temp/ |
| `"D:2 *.txt"` | Depth limit | Max 2 levels deep |
| `--containing "text"` | Search text inside files | `--containing "import os"` |
| `--regex "pattern"` | Regex on filenames | `--regex "^IMG_\d{8}"` |
| `--min-size 1KB` | Minimum file size | `--min-size 100MB` |
| `--max-size 10MB` | Maximum file size | `--max-size 1GB` |
| `--not-older-than 7d` | Max age (d/h/m) | `--not-older-than 24h` |
| `--show-hidden` | Include dotfiles | |

### Examples

```bash
# Find all PDFs
python .../tc_search.py /home/ubuntu "*.pdf"

# Find large files
python .../tc_search.py /home/ubuntu "*" --min-size 100MB

# Find Python files containing "TODO"
python .../tc_search.py ./project "*.py" --containing "TODO"

# Find recent images, exclude thumbnails
python .../tc_search.py ./photos "* | thumb_*" --not-older-than 30d

# Regex search for dated filenames
python .../tc_search.py ./docs --regex "^report_\d{4}-\d{2}"
```

## File Operations

Copy, move, delete files, create directories, inspect properties, and display directory trees.

```bash
python /home/ubuntu/skills/tc/scripts/file_ops.py <command> [args]
```

### Commands

```bash
# Copy files (supports glob patterns)
python .../file_ops.py copy "./src/*.pdf" ./backup/ [--flatten] [--dry-run]

# Move files
python .../file_ops.py move "./downloads/*.jpg" ./photos/ [--dry-run]

# Delete files
python .../file_ops.py delete "./temp/*.log" [--dry-run]

# Create directory (with parents)
python .../file_ops.py mkdir ./project/src/components

# Show file/folder properties
python .../file_ops.py props ./report.pdf

# Display directory tree
python .../file_ops.py tree /home/ubuntu --depth 2
```

**Properties output** includes: path, type, size (with byte count), modification/access/creation timestamps, permissions, and for directories: file count, subdirectory count, and total disk usage.

## Archive Operations

Pack files into ZIP archives and unpack various archive formats.

```bash
python /home/ubuntu/skills/tc/scripts/archive_ops.py <command> [args]
```

### Commands

```bash
# Pack files into ZIP
python .../archive_ops.py pack "./docs/*.pdf" backup.zip [--level 9]
python .../archive_ops.py pack ./project/ project_backup.zip

# Unpack archive
python .../archive_ops.py unpack archive.zip ./output/
python .../archive_ops.py unpack data.tar.gz ./extracted/

# List archive contents with sizes and compression ratios
python .../archive_ops.py list backup.zip
```

### Supported Formats

| Format | Pack | Unpack |
|--------|------|--------|
| ZIP | Yes | Yes |
| TAR / TAR.GZ / TAR.BZ2 / TAR.XZ | -- | Yes |
| GZ / BZ2 | -- | Yes |

For RAR, 7z, ARJ, LHA, ISO, CAB: install `p7zip-full` and use `7z x archive -o./output/`.

**Full format details:** See `references/archive-formats.md`.

## References

Load these only when needed:

| File | When to read |
|------|-------------|
| `references/multi-rename.md` | Need full placeholder syntax, range variants, counter options, or advanced rename patterns |
| `references/archive-formats.md` | Need format compatibility details or p7zip installation for exotic formats |
| `references/shortcuts.md` | Need TC keyboard shortcuts, button bar config, search syntax, or plugin connection details |

## Assets

The `assets/img/` directory contains TC's UI icons (PNG/GIF) for button bar visualization: copy, delete, select, sort, zip, play, pause, exit, etc.
