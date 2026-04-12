# TC Quick Reference

## Keyboard Shortcuts (Android with physical keyboard)

| Key | Action | Key | Action |
|-----|--------|-----|--------|
| 1 | Page Up | 0 | Page Down |
| 2 | Rename | SPACE | Select file |
| 4 | Edit | + | Select dialog (add) |
| 5 | Copy | - | Select dialog (remove) |
| 6 | Move | * | Reverse selection |
| 7 | New folder | ENTER | Open file/folder |
| 8 | Delete | # / @ | Properties |
| 9 | Sort list | ESC/Backspace | Go up one level |

## Button Bar Function Types

| Type | Description | Command Field |
|------|-------------|---------------|
| Change directory | Navigate to path | Directory path |
| Internal command | TC built-in command | Command name |
| Launch app | Start application | Package name |
| View file with app | Open file in viewer | Package name |
| Send to app | Share file with app | Package name |
| Send shell command | Execute shell | `sh` or `su` |

## Shell Command Parameter Prefixes

| Prefix | Effect |
|--------|--------|
| `?` | Opens dialog to edit command before running |
| `*` | Shows results in dialog box (copyable) |
| `*10*` | Shows results with font size 10 |
| `&` | Re-reads current directory after execution |

## Button Parameter Formats

| Format | Description |
|--------|-------------|
| `file:/path/name` | Send file as URL |
| `url:https://...` | Send any URL |
| `stream:/path/name` | Send as STREAM extra |
| `type:text/plain` | Set explicit MIME type |
| `extra:NAME:data` | Set android.intent.extra.NAME |
| `extra0:NAME:data` | Set extra with raw NAME |
| `action:action.NAME` | Set explicit intent action |
| `broadcast:action.NAME` | Send broadcast instead of activity |

## Search Syntax

| Syntax | Meaning |
|--------|---------|
| `*.pdf` | Wildcard match |
| `report_202?` | Single character wildcard |
| `* \| *.log temp/` | Exclude patterns (after pipe) |
| `D:2 *.txt` | Limit search depth to 2 levels |

## Plugin Connections

| Plugin | Protocol | Default Port |
|--------|----------|-------------|
| FTP | ftp:// | 21 |
| SFTP | sftp:// | 22 |
| LAN (SMB) | smb:// | 445 |
| WebDAV | https:// | 443 / 2078 (CPanel) |
| WiFi Transfer | http:// | (dynamic) |
