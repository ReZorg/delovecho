# Multi-Rename Placeholder Reference

## Table of Contents

1. [Name Placeholders](#name-placeholders)
2. [Counter Placeholders](#counter-placeholders)
3. [Date/Time Placeholders](#datetime-placeholders)
4. [Case Modifiers](#case-modifiers)
5. [Special Placeholders](#special-placeholders)
6. [Common Patterns](#common-patterns)

## Name Placeholders

| Placeholder | Description | Example Input → Output |
|-------------|-------------|----------------------|
| `[N]` | Name without extension | `photo.jpg` → `photo` |
| `[N1]` | First character | `photo.jpg` → `p` |
| `[N2-5]` | Characters 2 to 5 | `photo_001.jpg` → `hoto` |
| `[N2,5]` | 5 chars starting at position 2 | `photo_001.jpg` → `hoto_` |
| `[N2-]` | All from position 2 | `photo_001.jpg` → `hoto_001` |
| `[N-5-]` | From 5th-last to end | `photo_001.jpg` → `e_001` |
| `[N-8,5]` | 5 chars starting at 8th-last | varies |
| `[N-8-5]` | From 8th-last to 5th-last | varies |
| `[N2--5]` | From 2nd to 5th-last | varies |
| `[N02-9]` | Chars 2-9, zero-padded left | `abc` → `000000bc` |
| `[N 2-9]` | Chars 2-9, space-padded left | `abc` → `      bc` |
| `[A]` | Full name WITH extension | `photo.jpg` → `photo.jpg` |
| `[E]` | Extension only | `photo.jpg` → `jpg` |
| `[E1-2]` | Chars 1-2 of extension | `photo.jpeg` → `jp` |
| `[P]` | Parent directory name | `/pics/photo.jpg` → `pics` |
| `[G]` | Grandparent directory name | `/home/pics/photo.jpg` → `home` |

All range variants (`[X1-3]`, `[X2,5]`, `[X-5-]`, etc.) work with `[N]`, `[A]`, `[E]`, `[P]`, `[G]`.

## Counter Placeholders

| Placeholder | Description |
|-------------|-------------|
| `[C]` | Counter: start=1, step=1, no fixed width |
| `[C:3]` | Counter with 3-digit width: `001`, `002`, ... |
| `[C:a]` | Counter with auto-width based on file count |
| `[C10]` | Start at 10 |
| `[C+5]` | Step by 5 |
| `[C10+5:3]` | Start=10, step=5, width=3: `010`, `015`, `020` |
| `[Caa+1]` | Letter counter: `aa`, `ab`, `ac`, ... |
| `[C+1/100]` | Increment every 100 files (for folder distribution) |

**Folder distribution example:** `[C+1/3]/[N].[E]` puts 3 files per subfolder.

## Date/Time Placeholders

Time source switches (no output, just change the source for subsequent fields):

| Switch | Source |
|--------|--------|
| `[T1]` | File modification date (default) |
| `[T2]` | Current date (when dialog opened) |
| `[T3]` | Current date (when options last changed) |
| `[T4]` | EXIF date/time |

Date/time fields:

| Placeholder | Output | Format |
|-------------|--------|--------|
| `[d]` | Date in locale format | `2025-01-15` (/ → -) |
| `[Y]` | Year, 4 digits | `2025` |
| `[y]` | Year, 2 digits | `25` |
| `[M]` | Month, 2 digits | `01` |
| `[D]` | Day, 2 digits | `15` |
| `[t]` | Time in locale format | `14.30.00` (: → .) |
| `[h]` | Hours, 24h, 2 digits | `14` |
| `[H]` | Hours, 12h, 2 digits | `02` |
| `[m]` | Minutes, 2 digits | `30` |
| `[s]` | Seconds, 2 digits | `00` |
| `[i]` | am/pm indicator | `pm` |
| `[i1]` | a/p indicator | `p` |

## Case Modifiers

| Placeholder | Effect |
|-------------|--------|
| `[U]` | UPPERCASE from this position onward |
| `[L]` | lowercase from this position onward |
| `[F]` | Title Case from this position onward |
| `[f]` | Title Case (English rules: a, in, the, ... stay lowercase) |
| `[n]` | Original case from this position onward |

## Special Placeholders

| Placeholder | Description |
|-------------|-------------|
| `[S]` | File size in bytes |
| `[R]` | Random number, 1-6 digits |
| `[R5]` | Random number, exactly 5 digits |
| `[%VAR%]` | Environment variable |
| `[[]` | Literal `[` |
| `[]]` | Literal `]` |

## Common Patterns

**Photo organization:**
```
[T1][Y]-[M]-[D]_[h][m][s].[E]           → 2025-01-15_143000.jpg
Vacation_[Y][M][D]_[C:3].[E]            → Vacation_20250115_001.jpg
```

**Batch numbering:**
```
[N]_[C:3].[E]                           → photo_001.jpg
Chapter_[C:2] - [N].[E]                 → Chapter_01 - Introduction.pdf
```

**Case normalization:**
```
[L][N].[E]                               → my_document.pdf
[U][N].[E]                               → MY_DOCUMENT.PDF
[F][N].[E]                               → My Document.Pdf
```

**Folder distribution (100 files per folder):**
```
batch_[C+1/100]/[N].[E]                 → batch_1/file.jpg (files 1-100)
                                          → batch_2/file.jpg (files 101-200)
```
