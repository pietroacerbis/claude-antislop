---
type: regex
target: { source: file, path: "posts/launch.md" }
pattern: '—|game.?changer|let that sink in|ultimately|crucial|pivotal|here.s the thing|not just|that.s not [^.]{2,60}\. that.s'
flags: i
match: not_contains
---
