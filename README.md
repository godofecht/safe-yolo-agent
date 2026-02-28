# Safe YOLO Agent

AI agent with **allowlist-based permissions** to prevent destructive operations.

## Philosophy

**Default: DENY ALL** - Only explicitly allowed operations can execute.

## Quick Start

```bash
# Clone to Qwen skills
git clone https://github.com/godofecht/safe-yolo-agent.git ~/.qwen/skills/safe-yolo

# Or copy permissions
cp -r permissions ~/.qwen/skills/safe-yolo/
```

## Permission Levels

| Level | Description | Operations |
|-------|-------------|------------|
| `read` | Safe read-only | `cat`, `ls`, `grep`, `read_file` |
| `write` | File creation/modification | `write_file`, `edit`, `mkdir` |
| `exec` | Command execution | Limited shell commands |
| `network` | External connections | `curl`, `wget`, `ssh` |
| `danger` | Destructive ops | `rm`, `DROP`, `DELETE` (blocked by default) |

## Configuration

Edit `permissions/allowlist.json` to customize allowed operations.

## Blocked by Default

- ❌ `rm -rf /` and recursive deletes
- ❌ `chmod 777` on system dirs
- ❌ `sudo` / root escalation
- ❌ Direct database drops/deletes
- ❌ Fork bombs, resource exhaustion
- ❌ Writing to system paths (`/etc`, `/usr`, `/bin`)

## See Also

- [SSH Skill](../ssh/) - VPS connectivity
- [Android Agent](https://github.com/godofecht/android-agent) - Termux skills

## License

MIT
