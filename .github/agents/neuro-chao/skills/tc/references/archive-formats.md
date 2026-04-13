# Archive Format Reference

## Supported Formats

| Format | Read | Write | Library | Notes |
|--------|------|-------|---------|-------|
| ZIP | Yes | Yes | Built-in | Full compatibility, deflate compression |
| RAR | Yes | No | 7zip | Requires `unrar` or `p7zip` on Linux |
| 7z | Yes | No | 7zip | High compression ratio |
| TAR | Yes | Yes | Built-in | No compression, container only |
| GZ / TGZ | Yes | Yes | Built-in | Gzip, often wraps TAR |
| BZ2 / TBZ | Yes | Yes | Built-in | Bzip2, higher ratio than gzip |
| XZ | Yes | Yes | Built-in | LZMA2, best ratio for text |
| Z / TZ | Yes | No | — | Legacy Unix compress |
| ARJ | Yes | No | 7zip | Legacy DOS archiver |
| LHA / LZH | Yes | No | 7zip | Lempel-Ziv-Huffman |
| ISO / IMG | Yes | No | 7zip | Disc images |
| CAB | Yes | No | 7zip | Microsoft Cabinet |

## Python Standard Library Support

These formats can be handled without external dependencies:

```python
import zipfile    # ZIP read/write
import tarfile    # TAR, TAR.GZ, TAR.BZ2, TAR.XZ read/write
import gzip       # GZ read/write
import bz2        # BZ2 read/write
import lzma       # XZ read/write
```

For RAR, 7z, ARJ, LHA, ISO, CAB — install `p7zip-full`:
```bash
sudo apt-get install -y p7zip-full
# Then use: 7z x archive.rar -o./output/
```

## archive_ops.py Quick Reference

```bash
# Pack files into ZIP
python scripts/archive_ops.py pack "./docs/*.pdf" backup.zip
python scripts/archive_ops.py pack ./project/ project.zip --level 9

# Unpack any supported format
python scripts/archive_ops.py unpack archive.zip ./output/
python scripts/archive_ops.py unpack data.tar.gz ./extracted/

# List archive contents
python scripts/archive_ops.py list backup.zip
```
