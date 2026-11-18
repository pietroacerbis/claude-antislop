#!/bin/bash
set -e
mkdir -p "$(dirname 'notes/release.md')"
cat > 'notes/release.md' <<'FIXTURE_EOF'
# Release 2.4

The export now runs in the background. On a 50,000-row table it finished in 41 seconds, against 3 minutes in 2.3.

Two settings moved to the Team page: the default currency and the fiscal year start.
FIXTURE_EOF
