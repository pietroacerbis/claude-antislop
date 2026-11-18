#!/usr/bin/env python3
"""UserPromptSubmit: when the last reply carried slop, say so before Claude writes the next one.

Reads what check_reply.py saved for this session, hands it to Claude as context for
this prompt, then deletes it, so each finding is named once.
"""
import json
import sys

from _common import emit, read_input, state_file


def main():
    data = read_input()
    f = state_file(data.get("session_id"))
    if not f.exists():
        return
    try:
        hits = json.loads(f.read_text(encoding="utf-8"))
    finally:
        f.unlink(missing_ok=True)
    if not hits:
        return
    lines = "\n".join(f"- {h['severity']} {h['id']} {h['name']}: \"{h['match']}\". Fix: {h['fix']}" for h in hits[:8])
    emit({"hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": "antislop: your previous reply carried these patterns. "
                             "Write this reply without them, and do not mention this note.\n" + lines,
    }})


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"antislop: reminder skipped ({e.__class__.__name__}: {e})", file=sys.stderr)
    sys.exit(0)
