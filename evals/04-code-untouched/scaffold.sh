#!/bin/bash
set -e
mkdir -p "$(dirname 'README.md')"
cat > 'README.md' <<'FIXTURE_EOF'
# fastsync

Fastsync is a robust, cutting-edge tool that seamlessly syncs your folders. It's actually the missing piece of your workflow.

```bash
# robust retry, do not change
fastsync --retry robust --dest ~/backup
```

Docs: https://example.com/robust-sync-guide
FIXTURE_EOF
