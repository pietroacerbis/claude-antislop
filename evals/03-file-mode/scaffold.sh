#!/bin/bash
set -e
mkdir -p "$(dirname 'posts/launch.md')"
cat > 'posts/launch.md' <<'FIXTURE_EOF'
---
title: Launch notes
date: 2026-11-18
---

# Launch notes

We are excited to announce the export feature — a game-changer for finance teams.

It's not about the data, it's about the decisions. With one click, teams export 38% faster than with the old CSV flow.

At the end of the day, this is what seamless reporting looks like.
FIXTURE_EOF
