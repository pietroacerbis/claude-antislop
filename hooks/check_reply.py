#!/usr/bin/env python3
"""Stop: check the reply Claude just sent in the chat.

The reply is already on screen when this runs. With ANTISLOP_REPLY=next (the
default) the hits are saved, and remind.py names them at the top of your next
prompt, so the next reply is written knowing them. With ANTISLOP_REPLY=block,
Claude is asked to rewrite the reply at once, in a second message. Runs once per
turn: stop_hook_active is the guard against a loop.
"""
import json
import sys

from _common import check, describe, emit, read_input, setting, state_file


def last_reply(data):
    if data.get("last_assistant_message"):
        return data["last_assistant_message"]
    tp = data.get("transcript_path")
    if not tp:
        return ""
    try:
        lines = open(tp, encoding="utf-8").readlines()
    except OSError:
        return ""
    parts = []
    for raw in reversed(lines):
        try:
            rec = json.loads(raw)
        except ValueError:
            continue
        msg = rec.get("message") or {}
        role = msg.get("role") or rec.get("type")
        if role == "user":
            content = msg.get("content")
            # a tool result travels as a user record: keep walking back past it
            if isinstance(content, list) and content and all(
                    isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
                continue
            break
        if role == "assistant":
            for block in msg.get("content") or []:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(block.get("text", ""))
    return "\n\n".join(reversed(parts))


def main():
    mode = setting("ANTISLOP_REPLY", "next")
    data = read_input()
    if mode == "off" or data.get("stop_hook_active"):
        return
    text = last_reply(data)
    if not text.strip():
        return
    hits = check.scan(text)
    if not hits or not check.needs_rewrite(hits):
        return
    for h in hits:
        h["line"] = None
    if mode == "block":
        emit({"decision": "block",
              "reason": "antislop: your last reply carries patterns readers recognise as AI writing.\n"
                        f"{describe(hits)}\n"
                        "Send the reply again without them, same content, no preamble about the rewrite."})
        return
    state_file(data.get("session_id")).write_text(
        json.dumps([{k: h[k] for k in ("id", "name", "severity", "match", "fix")} for h in hits]),
        encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"antislop: reply check skipped ({e.__class__.__name__}: {e})", file=sys.stderr)
    sys.exit(0)
