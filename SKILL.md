# Safe YOLO Agent Skill

AI agent safety layer with allowlist-based permissions to prevent destructive operations.

## Core Principle

**DENY BY DEFAULT** - Only explicitly allowed operations can execute.

## Installation

```bash
git clone https://github.com/godofecht/safe-yolo-agent.git ~/.qwen/skills/safe-yolo
```

## Permission Checks

### Before Shell Commands
```
✓ ALLOWED: ls -la, cat file.txt, git status
✗ BLOCKED: rm -rf /, chmod 777 /etc
⚠ CONFIRM: rm file.txt, sudo apt install
```

### Before File Writes
```
✓ ALLOWED: .md, .py, .js, .json in user directories
✗ BLOCKED: Writing to /etc/, /usr/, /bin/
⚠ CONFIRM: package.json, .bashrc, .zshrc
```

### Before Network Operations
```
✓ ALLOWED: github.com, npmjs.com, pypi.org
✗ BLOCKED: Direct database ports (3306, 5432, 6379)
⚠ CONFIRM: raw.githubusercontent.com
```

## Blocked Operations (Hard Deny)

### Shell Commands
- `rm -rf /` and variants
- `rm -rf /*`, `rm -rf ~`, `rm -rf /home`
- `dd if=/dev/zero`
- Fork bombs: `:(){:|:&};:`
- `chmod 777 /` or `chmod -R 777 /`
- `mkfs`, `fdisk`, `parted`
- Writing to block devices: `> /dev/sda`

### Paths (Read/Write)
- `/etc/`, `/usr/`, `/bin/`, `/sbin/`
- `/lib/`, `/lib64/`, `/proc/`, `/sys/`, `/dev/`, `/boot/`

### Database
- `DROP DATABASE`, `DELETE FROM` without WHERE
- `TRUNCATE TABLE`

## Require Confirmation

| Operation | Reason |
|-----------|--------|
| `rm `, `rmdir ` | File deletion |
| `sudo `, `su ` | Privilege escalation |
| `DROP `, `DELETE `, `TRUNCATE ` | Data destruction |
| `kill -9`, `pkill ` | Process termination |
| `shutdown`, `reboot ` | System state change |
| Writing to config files | Dotfiles, package manifests |

## Rate Limits

| Operation | Limit |
|-----------|-------|
| Shell commands | 30/minute |
| File writes | 20/minute |
| Network requests | 60/minute |
| Concurrent tasks | 3 max |

## Audit Log

All operations are logged to `~/.safe-yolo/audit.log`:

```json
{
  "timestamp": "2026-02-28T16:00:00Z",
  "operation": "run_shell_command",
  "command": "ls -la",
  "result": "ALLOWED",
  "duration_ms": 150
}
```

## Usage Pattern

```python
# Pseudo-code for permission check
def check_permission(operation, params):
    if operation in allowlist.allowed_tools:
        if operation == "run_shell_command":
            return check_shell_allowlist(params.command)
        elif operation == "write_file":
            return check_file_write_rules(params.file_path)
        elif operation == "web_fetch":
            return check_network_rules(params.url)
    return DENY
```

## Integration

Add to Qwen skills directory:
```bash
cp -r ~/.qwen/skills/safe-yolo ~/.qwen/skills/
```

Reference in agent system prompt:
```
You are a safe AI agent. Before any operation:
1. Check if operation is in allowlist
2. Verify path/command is not blocked
3. Request confirmation for sensitive operations
4. Log all actions to audit log
```

## Files

- `README.md` - Project documentation
- `SKILL.md` - This skill definition
- `permissions/allowlist.json` - Permission configuration

## License

MIT
