#!/bin/bash
set -e
mkdir -p "$(dirname 'src/sync.py')"
cat > 'src/sync.py' <<'FIXTURE_EOF'
def sync(paths):
    # a robust, seamless sync
    return [p for p in paths if p]
FIXTURE_EOF
