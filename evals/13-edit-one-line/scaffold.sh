#!/bin/bash
set -e
mkdir -p "$(dirname 'notes/update.md')"
cat > 'notes/update.md' <<'FIXTURE_EOF'
# Weekly update

The team closed 4 deals this week, for 62,000 euros in total.

Pipeline coverage sits at 2.8x against a 3x target, so we need about 9,000 euros more in qualified pipeline before Friday.

Marta takes the two stalled deals in the Lisbon segment.

Ultimately, this is a pivotal week, and we are excited to navigate the road ahead.
FIXTURE_EOF
