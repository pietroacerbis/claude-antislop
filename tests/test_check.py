#!/usr/bin/env python3
"""Tests for the list, the checker and the three hooks. Standard library only.

    python3 tests/test_check.py

Prints one line per failed test and a total, exits 1 on any failure.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "skills" / "deslop" / "scripts"
HOOKS = ROOT / "hooks"
sys.path.insert(0, str(SCRIPTS))
import check  # noqa: E402
import patterns  # noqa: E402

FAILED, PASSED = [], [0]


def ok(name, cond, detail=""):
    if cond:
        PASSED[0] += 1
    else:
        FAILED.append(f"FAIL {name} {detail}")


def ids(text):
    return [h["id"] for h in check.scan(text)]


# 1. every row catches its example and lets the clean one through ------------------
for group, table in patterns.GROUPS:
    for pid, name, sev, rx, fix, hit, clean in table:
        ok(f"{pid} catches its example", pid in ids(hit), repr(hit))
        ok(f"{pid} passes the clean example", ids(clean) == [], f"{clean!r} -> {ids(clean)}")
        ok(f"{pid} severity", sev in ("fail", "flag"))

all_ids = [row[0] for _, t in patterns.GROUPS for row in t]
ok("ids are unique", len(all_ids) == len(set(all_ids)))

# 2. masking: what is not the writer's prose is never reported ----------------------
masked_cases = {
    "fenced code": "```\nThis is robust and crucial.\n```\n",
    "tilde fence": "~~~\nUltimately robust.\n~~~\n",
    "inline code": "Set `robust=true` in the config.",
    "blockquote": "> Most founders delve into this.\n",
    "double quotes": 'He wrote "this is not a tool, but a habit" in the deck.',
    "curly quotes": "He wrote “this is not a tool, but a habit” in the deck.",
    "guillemets": "Ha scritto «non è un tool, è un'abitudine» nella deck.",
    "link target": "Read [the guide](https://example.com/robust-crucial-pivotal).",
    "bare URL": "See https://example.com/delve/crucial for details.",
    "html comment": "Plain line.\n<!-- crucial pivotal robust -->\n",
    "table rule": "| a | b |\n|---|---|\n| one | two |\n",
}
for name, text in masked_cases.items():
    ok(f"mask: {name}", ids(text) == [], f"-> {ids(text)}")

ok("mask keeps length", len(check.mask("a `robust` b")) == len("a `robust` b"))
ok("short quote stays checked", "R14" in ids('We call it "robust" here.'))
ok("prose beside code stays checked", "R14" in ids("A robust plan, see `x`."))
ok("curly apostrophe normalised", "R15" in ids("Here’s the thing about churn."))
ok("en dash in a number range passes", ids("The 2024–2025 plan.") == [])
ok("en dash between words fails", "R13" in ids("The plan – finally – shipped."))
ok("line numbers", [h["line"] for h in check.scan("one\ntwo\nThis is crucial.\n")] == [3])
ok("a few people is a count", ids("A few people asked for the export.") == [])
ok("underscore as a character passes", ids("Use an underscore in file names.") == [])
ok("a concession is not a reframe", ids("It is not cheap, but it works.") == [])
ok("a reframe on a verb is caught", "R1" in ids("We do not sell software, but outcomes."))
ok("a literal migration passes", ids("Migrate from streamObject to streamText.") == [])
ok("a number range passes", ids("Churn went from 41 to 29 accounts.") == [])
ok("one term repeated counts once",
   not check.needs_rewrite(check.scan("Navigate the index. Navigate the folder. Navigate back.")))

# 3. the verdict ---------------------------------------------------------------------
flag2 = "We navigate the landscape."           # two flags
flag3 = "We navigate the landscape and its dynamics."  # three flags
ok("two flags are within the limit", not check.needs_rewrite(check.scan(flag2)))
ok("three flags need a rewrite", check.needs_rewrite(check.scan(flag3)))
ok("one fail needs a rewrite", check.needs_rewrite(check.scan("A crucial step.")))

# 4. BANNED-FORMULAS.md is the printed list ------------------------------------------
doc = ROOT / "BANNED-FORMULAS.md"
ok("BANNED-FORMULAS.md matches check.py --list",
   doc.exists() and doc.read_text(encoding="utf-8") == check.render_list(),
   "print it again: python3 skills/deslop/scripts/check.py --list > BANNED-FORMULAS.md")

# 5. the command line ------------------------------------------------------------------
tmp = Path(tempfile.mkdtemp(prefix="antislop-test-"))


def run(args, stdin="", env=None):
    e = dict(os.environ, **(env or {}))
    return subprocess.run([sys.executable] + args, input=stdin, capture_output=True, text=True, env=e)


(tmp / "clean.md").write_text("The import runs every night at 2:00.\n")
(tmp / "slop.md").write_text("# Post\n\nUltimately, this is a crucial step.\n")
(tmp / "off.md").write_text("<!-- antislop: off -->\nUltimately, crucial.\n")
r = run([str(SCRIPTS / "check.py"), str(tmp / "clean.md")])
ok("cli clean exits 0", r.returncode == 0 and "clean" in r.stdout, r.stdout)
r = run([str(SCRIPTS / "check.py"), str(tmp / "slop.md")])
ok("cli slop exits 1", r.returncode == 1 and ":3: fail" in r.stdout, r.stdout)
r = run([str(SCRIPTS / "check.py"), str(tmp / "off.md")])
ok("cli skips the off mark", r.returncode == 0 and "skipped" in r.stdout, r.stdout)
(tmp / "mention.md").write_text("A file holding the line `<!-- antislop: off -->` is skipped. Ultimately crucial.\n")
r = run([str(SCRIPTS / "check.py"), str(tmp / "mention.md")])
ok("a mention of the off mark does not switch the check off", r.returncode == 1, r.stdout)
r = run([str(SCRIPTS / "check.py"), str(tmp / "missing.md")])
ok("cli missing file exits 2", r.returncode == 2)
r = run([str(SCRIPTS / "check.py"), "-"], stdin="Let's dive in.\n")
ok("cli reads stdin", r.returncode == 1 and "H1" in r.stdout, r.stdout)
r = run([str(SCRIPTS / "check.py"), "--json", str(tmp / "slop.md")])
try:
    j = json.loads(r.stdout)
    ok("cli json", j[0]["needs_rewrite"] and {h["id"] for h in j[0]["hits"]} == {"P1", "R14"}, r.stdout)
except ValueError:
    ok("cli json parses", False, r.stdout)
r = run([str(SCRIPTS / "check.py")])
ok("cli no argument exits 2", r.returncode == 2)

# 6. the file hook -----------------------------------------------------------------------
data_dir = tmp / "plugin-data"
ENV = {"CLAUDE_PLUGIN_DATA": str(data_dir)}


def hook(name, payload, env=None):
    r = run([str(HOOKS / name)], stdin=payload if isinstance(payload, str) else json.dumps(payload),
            env=dict(ENV, **(env or {})))
    try:
        out = json.loads(r.stdout) if r.stdout.strip() else None
    except ValueError:
        out = {"unparsed": r.stdout}
    return r.returncode, out, r.stderr


def write_event(path, tool="Write", **ti):
    return {"session_id": "s1", "hook_event_name": "PostToolUse", "tool_name": tool,
            "tool_input": dict({"file_path": str(path)}, **ti), "tool_response": {}}


post = tmp / "post.md"
post.write_text("# Launch\n\nWe shipped it.\n\nThis is not a pipeline problem, but a systems problem.\n")
code, out, _ = hook("check_write.py", write_event(post, content=post.read_text()))
ok("write: slop is blocked", code == 0 and out and out.get("decision") == "block", str(out))
ok("write: the reason names line and pattern", out and "line 5" in out["reason"] and "R1" in out["reason"], str(out))

post.write_text("# Launch\n\nWe shipped it on Monday.\n")
code, out, _ = hook("check_write.py", write_event(post, content=post.read_text()))
ok("write: clean is silent", code == 0 and out is None, str(out))

py = tmp / "tool.py"
py.write_text("# a crucial, robust helper\n")
code, out, _ = hook("check_write.py", write_event(py, content=py.read_text()))
ok("write: code files are ignored", out is None, str(out))

doc2 = tmp / "notes.md"
doc2.write_text("Ultimately, a crucial and robust plan.\n\nline two\n\nThe import runs at 2:00.\n")
code, out, _ = hook("check_write.py", write_event(doc2, "Edit", old_string="x", new_string="The import runs at 2:00."))
ok("edit: old slop elsewhere in the file is not reported", out is None, str(out))

doc2.write_text("Plain first line.\n\nWe built a robust, holistic framework.\n")
code, out, _ = hook("check_write.py", write_event(doc2, "Edit", old_string="x", new_string="We built a robust, holistic framework."))
ok("edit: slop in the new text is blocked at its line", out and "line 3" in out.get("reason", ""), str(out))

code, out, _ = hook("check_write.py", write_event(doc2, "MultiEdit", edits=[{"old_string": "a", "new_string": "We built a robust, holistic framework."}]))
ok("multiedit: slop is blocked", out and out.get("decision") == "block", str(out))

code, out, _ = hook("check_write.py", write_event(doc2, "Edit", old_string="x", new_string="robust holistic\r\nframework crucial"))
ok("edit not found verbatim: the new text is checked alone", out and out.get("decision") == "block", str(out))

off = tmp / "quoted.md"
off.write_text("<!-- antislop: off -->\nUltimately crucial robust.\n")
code, out, _ = hook("check_write.py", write_event(off, content=off.read_text()))
ok("write: off mark is respected", out is None, str(out))

post.write_text("Ultimately, crucial.\n")
code, out, _ = hook("check_write.py", write_event(post, content=post.read_text()), env={"ANTISLOP_FILES": "off"})
ok("write: ANTISLOP_FILES=off", out is None, str(out))

txt = tmp / "draft.txt"
txt.write_text("Ultimately, crucial.\n")
code, out, _ = hook("check_write.py", write_event(txt, content=txt.read_text()), env={"ANTISLOP_EXTENSIONS": ".md"})
ok("write: ANTISLOP_EXTENSIONS narrows the files", out is None, str(out))

flags = tmp / "flags.md"
flags.write_text(flag2 + "\n")
code, out, _ = hook("check_write.py", write_event(flags, content=flags.read_text()))
ok("write: two flags pass", out is None, str(out))
flags.write_text(flag3 + "\n")
code, out, _ = hook("check_write.py", write_event(flags, content=flags.read_text()))
ok("write: three flags are blocked", out and out.get("decision") == "block", str(out))

code, out, _ = hook("check_write.py", write_event(ROOT / "BANNED-FORMULAS.md", content="x"))
ok("write: the plugin's own files are skipped", out is None, str(out))

code, out, err = hook("check_write.py", "not json")
ok("write: bad input exits 0, silent", code == 0 and out is None, err)

code, out, _ = hook("check_write.py", write_event(tmp / "nope.md", content="x"))
ok("write: a missing file is silent", code == 0 and out is None)

# 7. the reply hooks ----------------------------------------------------------------------


def transcript(*records):
    t = tmp / f"t{len(list(tmp.glob('t*.jsonl')))}.jsonl"
    t.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    return str(t)


def user(text):
    return {"type": "user", "message": {"role": "user", "content": text}}


def assistant(text):
    return {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}


def tool_use():
    return {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "1", "name": "Bash", "input": {}}]}}


def tool_result():
    return {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "1", "content": "ok"}]}}


def stop_event(tp, sid="s2", active=False):
    return {"session_id": sid, "hook_event_name": "Stop", "transcript_path": tp, "stop_hook_active": active}


def prompt_event(sid="s2"):
    return {"session_id": sid, "hook_event_name": "UserPromptSubmit", "prompt": "next"}


slop_reply = "Great question! Ultimately, this is a crucial step. Let me know if you need anything."
tp = transcript(user("old"), assistant("The import runs at 2:00."), user("hi"), assistant(slop_reply))
code, out, _ = hook("check_reply.py", stop_event(tp))
ok("stop: next mode saves, prints nothing", code == 0 and out is None, str(out))
code, out, _ = hook("remind.py", prompt_event())
ctx = (out or {}).get("hookSpecificOutput", {}).get("additionalContext", "")
ok("prompt: the saved hits are named", "P1" in ctx and "R14" in ctx, str(out))
code, out, _ = hook("remind.py", prompt_event())
ok("prompt: each finding is named once", out is None, str(out))

tp = transcript(user("hi"), assistant("The import runs at 2:00."))
hook("check_reply.py", stop_event(tp, sid="s3"))
code, out, _ = hook("remind.py", prompt_event("s3"))
ok("clean reply: nothing named", out is None, str(out))

tp = transcript(user("hi"), assistant("Ultimately, this is crucial."), tool_use(), tool_result(), assistant("Done."))
hook("check_reply.py", stop_event(tp, sid="s4"))
code, out, _ = hook("remind.py", prompt_event("s4"))
ok("stop: the whole turn is read, past tool results", out is not None and "P1" in json.dumps(out), str(out))

tp = transcript(user("Ultimately crucial robust"), assistant("The import runs at 2:00."))
hook("check_reply.py", stop_event(tp, sid="s5"))
code, out, _ = hook("remind.py", prompt_event("s5"))
ok("stop: the user's own words are never checked", out is None, str(out))

tp = transcript(user("hi"), assistant(slop_reply))
code, out, _ = hook("check_reply.py", stop_event(tp, active=True))
ok("stop: stop_hook_active is respected", out is None, str(out))

code, out, _ = hook("check_reply.py", stop_event(tp), env={"ANTISLOP_REPLY": "block"})
ok("stop: block mode asks for the rewrite", out and out.get("decision") == "block" and "P1" in out.get("reason", ""), str(out))

hook("check_reply.py", stop_event(tp, sid="s6"), env={"ANTISLOP_REPLY": "off"})
code, out, _ = hook("remind.py", prompt_event("s6"))
ok("stop: off mode records nothing", out is None, str(out))

code, out, _ = hook("check_reply.py", {"session_id": "s7", "last_assistant_message": slop_reply})
code, out, _ = hook("remind.py", prompt_event("s7"))
ok("stop: last_assistant_message is read when given", out is not None, str(out))

code, out, err = hook("check_reply.py", stop_event(str(tmp / "missing.jsonl"), sid="s8"))
ok("stop: a missing transcript exits 0", code == 0 and out is None, err)

code, out, err = hook("remind.py", "{bad")
ok("prompt: bad input exits 0", code == 0 and out is None, err)

ok("hooks.json parses", isinstance(json.loads((HOOKS / "hooks.json").read_text())["hooks"]["Stop"], list))

for line in FAILED:
    print(line)
print(f"{PASSED[0]} passed, {len(FAILED)} failed")
sys.exit(1 if FAILED else 0)
