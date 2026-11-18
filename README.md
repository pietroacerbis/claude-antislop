# Claude antislop

Keeps the tells of AI writing out of what Claude writes for you: in the files it writes, in the replies it sends, and in any draft you hand it.

- **The list**: 61 patterns in English and Italian, each with its fix, in [BANNED-FORMULAS.md](BANNED-FORMULAS.md).
- **Three hooks** that check every markdown or text file Claude writes, and every reply it sends, without being asked.
- **deslop**, a skill: give it a draft or a file, and it rewrites the flagged sentences and the tells no pattern catches, keeps every fact, and checks again until the text is clean.

```
/plugin marketplace add pietroacerbis/claude-antislop
/plugin install antislop@claude-antislop
```

It needs Python 3.8 or later, as `python3` on your PATH. It adds about 170 tokens to every session, measured with `claude plugin details antislop`. The hooks add nothing to the context until they find something.

---

## What happens once it is installed

| When | What runs | What you see |
|---|---|---|
| Claude writes or edits a `.md`, `.mdx` or `.txt` file | `hooks/check_write.py`, after the write | Nothing, when the lines it wrote are clean. Otherwise Claude gets each line, its pattern and the fix, and rewrites those sentences in the same turn |
| Claude ends a reply | `hooks/check_reply.py` | Nothing on screen: a reply with slop is noted |
| You send your next prompt | `hooks/remind.py` | Nothing on screen: Claude is told which patterns its last reply carried, and writes this one without them |
| You write "deslop this", "make this sound human", "togli lo slop" | the `deslop` skill | The rewrite, five lines on what changed, and the check's last line |

A write is judged on the lines it touched, so an edit to an old document never drags in the old sentences around it. When you ask Claude for a phrase on purpose, it keeps it and tells you the check flagged it.

## The check

Every pattern is `fail`, the text does not ship with it, or `flag`, fine once. More than two different flags in one text means a rewrite.

Never checked: code blocks, inline code, quotations of four words or more, blockquotes, URLs, link targets and HTML comments. A file holding the line `<!-- antislop: off -->` is skipped.

From a clone of this repository, run it on any file:

```
python3 skills/deslop/scripts/check.py post.md
```

```
post.md:5: fail R1 not-x-but-y "not a pipeline problem, but" in: ...unch We shipped it. This is not a pipeline problem, but a systems problem.
    fix: Say the thing directly. Keep a contrast only when the reader really holds the belief you correct.
post.md: 1 fail, 0 flag, rewrite needed
```

It exits with 1 when a text needs a rewrite, so it also runs in CI or in a pre-commit hook. `--json` prints the hits as JSON, and `-` reads from standard input.

## Settings

Environment variables, in the `env` block of your `settings.json`:

| Variable | Values | Default |
|---|---|---|
| `ANTISLOP_FILES` | `on`, `off` | `on` |
| `ANTISLOP_REPLY` | `next`: named at your next prompt. `block`: Claude sends the reply again at once, rewritten. `off` | `next` |
| `ANTISLOP_EXTENSIONS` | the file types checked, comma-separated | `.md,.mdx,.markdown,.txt` |

```json
{ "env": { "ANTISLOP_REPLY": "block" } }
```

## Add your own patterns

Each pattern is one row in [skills/deslop/scripts/patterns.py](skills/deslop/scripts/patterns.py): an id, a name, the severity, the regex, the fix, one sentence it must catch and one it must let through. After an edit:

```
python3 skills/deslop/scripts/check.py --list > BANNED-FORMULAS.md
python3 tests/test_check.py
```

The test runs both sentences of every row, the masks, the command line and the three hooks.

## How it was tested

- **[tests/test_check.py](tests/test_check.py)**: 250 checks, standard library only.
- **14 eval cases in [evals/](evals/)**, run with `claude plugin eval` on Sonnet, two runs each: 28 of 28 passed with the plugin. On the same cases without it, Sonnet invented a figure for a vague claim once, missed the user's voice sample once, and left a banned pattern in a launch post once.
- **The hooks, live in Claude Code 2.1.327.** A reply with `Ultimately` and `seamless` was blocked and sent again without them. In `next` mode, the note reached the following prompt and the next reply came out clean.

The evals sit at the plugin root because `claude plugin eval` refuses an eval folder inside `skills/`, and these cases test the skill and the hooks together.

## Credits

- The patterns come from the writing rules we run at [gaja](https://trygaja.com) on every post and every reply.
- [humanizer](https://github.com/blader/humanizer) by blader, MIT, shaped the judgment pass of deslop and several patterns: the staged opener, the defence against an objection nobody raised, the contrast split across two sentences. Humanizer builds on Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing). For a rewrite skill with no hooks, install humanizer.
- This plugin edits for human readers. It does not try to get text past AI detectors.

## The Skill kit

This repository is one of four:

- [How to build a skill](https://github.com/pietroacerbis/how-to-build-a-skill): the guide, the format, a template, and two skills that create and review skills.
- [Claude personal memory](https://github.com/pietroacerbis/claude-personal-memory): a small personal brain in plain files you own. Claude remembers who you are, your goals and what you corrected.
- [Claude Code daily](https://github.com/pietroacerbis/claude-code-daily): the Claude Code tools I use every day, by category.
- Claude antislop: this one.

<!-- CTA -->
---

## Want this list built on your own voice, for your whole team?

At gaja we build two things for go-to-market teams:

- **The knowledge your Claude reads**: your ICP, your deal stages, your objections, your voice, built from your calls, docs, tools and team.
- **The shared skills your team runs**: written on the processes you already follow, deployed to the whole team, all reading the same knowledge.

Get in touch:

- Pietro Acerbis, Founder at gaja: pietro@trygaja.com, [LinkedIn](https://www.linkedin.com/in/pietroacerbis-gaja/)
- gaja: [trygaja.com](https://trygaja.com), [LinkedIn](https://www.linkedin.com/company/gaja-brain/)

MIT licence.
