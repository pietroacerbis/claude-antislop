#!/usr/bin/env python3
"""Check text for the patterns readers recognise as AI writing.

    python3 check.py FILE [FILE ...]     check files
    python3 check.py -                   check text from stdin
    python3 check.py --json FILE         the hits as JSON
    python3 check.py --list              print the whole list as markdown

Exit 0 when every text is clean or holds at most THRESHOLD flags and no fail.
Exit 1 when one needs a rewrite. Exit 2 on a usage error.

What is not the writer's own prose is masked before the check, so it is never
reported: fenced and inline code, HTML comments, blockquotes, quotations of four
words or more, URLs and link targets. A file holding the line
`<!-- antislop: off -->` is skipped. Standard library only.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import patterns  # noqa: E402

OFF_MARK = "<!-- antislop: off -->"
_OFF = re.compile(r"(?m)^[ \t]*<!--[ \t]*antislop:[ \t]*off\b")


def is_off(text):
    """True when a line of the text opens with the off comment. A mention of it
    elsewhere, in inline code or mid-sentence, does not count."""
    return bool(_OFF.search(text))

_MASKS = [
    re.compile(r"(?ms)^[ \t]*(```|~~~)[^\n]*\n.*?(?:^[ \t]*\1[ \t]*$|\Z)"),  # fenced code
    re.compile(r"(?s)<!--.*?-->"),                                           # HTML comments
    re.compile(r"`[^`\n]+`"),                                                # inline code
    re.compile(r"(?m)^[ \t]*>.*$"),                                          # blockquotes
    re.compile(r"\[\[[^\]\n]*\]\]"),                                         # wiki-links
    re.compile(r"(?<=\])\([^)\n]*\)"),                                       # link targets
    re.compile(r"<https?://[^>\s]+>|https?://\S+"),                          # URLs
    re.compile(r"(?m)^[ \t]*\|?[ \t]*:?-{3,}[-:| \t]*$"),                    # table rules
]
# Quotations on one line: "straight", “curly” and «guillemets». Masked from four words
# up, so a scare quote around one word stays checked. The words are counted in Python:
# a regex that counts them inside the quote backtracks without end on a long line
# with an unclosed quote.
_QUOTES = re.compile(r'"[^"\n]{1,600}"|“[^”\n]{1,600}”|«[^»\n]{1,600}»')


def _blank(m):
    return re.sub(r"[^\n]", " ", m.group(0))


def _blank_quote(m):
    return _blank(m) if len(m.group(0)[1:-1].split()) >= 4 else m.group(0)


def mask(text):
    """The text with everything that is not the writer's prose turned to spaces.
    Same length, same line breaks, so offsets and line numbers still hold."""
    for rx in _MASKS:
        text = rx.sub(_blank, text)
    text = _QUOTES.sub(_blank_quote, text)
    return text.replace("’", "'")


def _compile():
    rows = []
    for group, table in patterns.GROUPS:
        for row in table:
            pid, name, sev, rx, fix = row[:5]
            if isinstance(rx, tuple):
                rx = r"\b(?:" + "|".join(re.escape(w) for w in rx) + r")\b"
            flags = 0 if pid in patterns.CASE_SENSITIVE else re.IGNORECASE
            rows.append((pid, name, sev, re.compile(rx, flags), fix))
    return rows


COMPILED = _compile()


def _excerpt(text, start, end):
    a = max(0, start - 30)
    b = min(len(text), end + 30)
    s = " ".join(text[a:b].split())
    return ("..." if a else "") + s + ("..." if b < len(text) else "")


def scan(text):
    """Every hit in the text: dicts with id, name, severity, line, excerpt, fix."""
    masked = mask(text)
    hits = []
    for pid, name, sev, rx, fix in COMPILED:
        for m in rx.finditer(masked):
            if not m.group(0).strip():
                continue
            hits.append({
                "id": pid, "name": name, "severity": sev,
                "line": masked.count("\n", 0, m.start()) + 1,
                "start": m.start(), "end": m.end(),
                "match": " ".join(text[m.start():m.end()].split()),
                "excerpt": _excerpt(text, m.start(), m.end()),
                "fix": fix,
            })
    hits.sort(key=lambda h: (h["line"], h["start"]))
    return hits


def needs_rewrite(hits):
    """A fail, or more than THRESHOLD distinct flags. The same word flagged three times
    counts once: a repeated literal term ("navigate the index") is a term of art, while
    three different flags in one text are the accumulation the limit is for."""
    fails = sum(1 for h in hits if h["severity"] == "fail")
    flags = len({(h["id"], h["match"].lower()) for h in hits if h["severity"] == "flag"})
    return fails > 0 or flags > patterns.THRESHOLD


def summary(label, hits):
    fails = sum(1 for h in hits if h["severity"] == "fail")
    flags = len(hits) - fails
    if not hits:
        return f"{label}: clean"
    state = "rewrite needed" if needs_rewrite(hits) else f"ok, {flags} flag(s) within the limit of {patterns.THRESHOLD}"
    return f"{label}: {fails} fail, {flags} flag, {state}"


def render(label, hits):
    out = []
    for h in hits:
        out.append(f"{label}:{h['line']}: {h['severity']} {h['id']} {h['name']} \"{h['match']}\" in: {h['excerpt']}")
        out.append(f"    fix: {h['fix']}")
    out.append(summary(label, hits))
    return "\n".join(out)


def render_list():
    """The whole list as markdown, printed into BANNED-FORMULAS.md."""
    total = sum(len(t) for _, t in patterns.GROUPS)
    lines = [
        "# The antislop list",
        "",
        "<!-- antislop: off: this file lists the patterns it checks -->",
        "",
        f"{total} patterns, printed from `skills/deslop/scripts/patterns.py` by `check.py --list`. "
        "Edit the patterns there, then print this file again: `tests/test_check.py` fails when the two differ.",
        "",
        f"- **fail**: the text does not ship with it.",
        f"- **flag**: read in context. One can be fine; more than {patterns.THRESHOLD} different ones in one text mean a rewrite.",
        "",
        "Code, quotations of four words or more, blockquotes, URLs and link targets are never checked. "
        "A file with the line `<!-- antislop: off -->` is skipped.",
    ]
    for group, table in patterns.GROUPS:
        lines += ["", f"## {group}", "", "| Id | Pattern | Severity | Catches | Fix |", "|---|---|---|---|---|"]
        for pid, name, sev, rx, fix, hit, _ in table:
            if isinstance(rx, tuple):
                name = f"{name}: " + ", ".join(rx)
            cell = lambda s: s.replace("|", "\\|")
            lines.append(f"| {pid} | {cell(name)} | {sev} | {cell(hit)} | {cell(fix)} |")
    return "\n".join(lines) + "\n"


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    opts = {a for a in argv if a.startswith("--")}
    if "--list" in opts:
        sys.stdout.write(render_list())
        return 0
    if not args or opts - {"--json"}:
        print(__doc__.strip().split("\n\n")[1], file=sys.stderr)
        return 2
    results, worst = [], 0
    for a in args:
        if a == "-":
            label, text = "stdin", sys.stdin.read()
        else:
            p = Path(a)
            if not p.is_file():
                print(f"{a}: no such file", file=sys.stderr)
                return 2
            label, text = a, p.read_text(encoding="utf-8", errors="replace")
        if is_off(text):
            results.append((label, None))
            continue
        hits = scan(text)
        results.append((label, hits))
        if needs_rewrite(hits):
            worst = 1
    if "--json" in opts:
        print(json.dumps([{"file": l, "skipped": h is None, "needs_rewrite": bool(h) and needs_rewrite(h),
                           "hits": [{k: v for k, v in x.items() if k not in ("start", "end")} for x in (h or [])]}
                          for l, h in results], ensure_ascii=False, indent=1))
    else:
        for label, hits in results:
            print(f"{label}: skipped, it holds {OFF_MARK}" if hits is None else render(label, hits))
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
