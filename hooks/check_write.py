#!/usr/bin/env python3
"""PostToolUse on Write, Edit and MultiEdit: check the prose Claude just wrote to a file.

Only the lines this write touched are reported, so an old file is never re-litigated
on every edit. When they need a rewrite, Claude is told which lines, which pattern
and the fix, and rewrites them in the same turn. Silent otherwise. Never fails the
tool call: any error here exits 0.
"""
import sys

from _common import check, describe, emit, read_input, setting, PLUGIN_ROOT
from pathlib import Path


def written_pieces(tool, ti):
    if tool == "Write":
        return None  # the whole file
    if tool == "Edit":
        return [ti.get("new_string") or ""]
    if tool == "MultiEdit":
        return [e.get("new_string") or "" for e in ti.get("edits") or []]
    return []


def line_span(text, piece):
    """1-based first and last line of piece inside text, or None when it is not there."""
    i = text.find(piece)
    if i < 0 or not piece.strip():
        return None
    first = text.count("\n", 0, i) + 1
    return first, first + piece.count("\n")


def main():
    if setting("ANTISLOP_FILES", "on") == "off":
        return
    data = read_input()
    tool = data.get("tool_name") or ""
    ti = data.get("tool_input") or {}
    path = ti.get("file_path") or ""
    exts = [e.strip() for e in setting("ANTISLOP_EXTENSIONS", ".md,.mdx,.markdown,.txt").split(",") if e.strip()]
    p = Path(path)
    if not path or p.suffix.lower() not in exts or not p.is_file():
        return
    try:
        p.resolve().relative_to(PLUGIN_ROOT)
        return  # the plugin's own files hold the patterns on purpose
    except ValueError:
        pass
    text = p.read_text(encoding="utf-8", errors="replace")
    if check.is_off(text):
        return

    hits = check.scan(text)
    pieces = written_pieces(tool, ti)
    if pieces is not None:
        spans = [line_span(text, piece) for piece in pieces]
        if any(s is None for s in spans):
            # The edit is not findable verbatim (a replace_all, a normalised line ending):
            # check the new text on its own instead.
            hits = [h for piece in pieces for h in check.scan(piece)]
            for h in hits:
                h["line"] = None
        else:
            hits = [h for h in hits if any(a <= h["line"] <= b for a, b in spans)]
    if not hits or not check.needs_rewrite(hits):
        return
    emit({
        "decision": "block",
        "reason": (
            f"antislop: the text you just wrote to {path} carries patterns readers recognise as AI writing.\n"
            f"{describe(hits)}\n"
            "Rewrite those sentences in the file now. Keep every fact, number, name and link; add none. "
            "Leave a hit only when it is a quotation or a term of art, and say which one and why."
        ),
    })


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # a checker bug must never break the user's write
        print(f"antislop: check skipped ({e.__class__.__name__}: {e})", file=sys.stderr)
    sys.exit(0)
