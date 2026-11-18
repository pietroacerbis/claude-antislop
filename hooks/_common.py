"""Shared by the three hooks: the checker, the settings, the state between two turns.

Settings are environment variables, set in the "env" block of a settings.json:

    ANTISLOP_FILES        on (default) | off      check the files Claude writes
    ANTISLOP_REPLY        next (default) | block | off
                          next: a reply with slop is named at the top of your next prompt
                          block: Claude rewrites the reply at once, in a second message
    ANTISLOP_EXTENSIONS   .md,.mdx,.markdown,.txt (default)   the files that are checked
"""
import json
import os
import re
import sys
import tempfile
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "skills" / "deslop" / "scripts"))
import check  # noqa: E402
import patterns  # noqa: E402


def setting(name, default):
    return (os.environ.get(name) or default).strip().lower()


def read_input():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def state_file(session_id):
    base = Path(os.environ.get("CLAUDE_PLUGIN_DATA") or Path(tempfile.gettempdir()) / "claude-antislop")
    base.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_-]", "", session_id or "") or "default"
    return base / f"{safe}.json"


def describe(hits, limit=8):
    """The hits as short lines a model can act on: where, what, the fix."""
    lines = []
    for h in hits[:limit]:
        where = f"line {h['line']}, " if h.get("line") else ""
        lines.append(f"- {where}{h['severity']} {h['id']} {h['name']}: \"{h['match']}\". Fix: {h['fix']}")
    if len(hits) > limit:
        lines.append(f"- and {len(hits) - limit} more of the same kinds")
    return "\n".join(lines)


def emit(obj):
    sys.stdout.write(json.dumps(obj))
