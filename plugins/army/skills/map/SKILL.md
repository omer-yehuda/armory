---
name: map
description: Generate the interactive army command-center map (units, playbooks, animated mission story, simulator).
disable-model-invocation: true
---

Run:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/build-map.js" --out ".army/army-map.html"
```

The map is generated from the installed plugin's own files. Tell the user the absolute path of the file. If they ask you to open it, use `open` on macOS, `xdg-open` on Linux, or `start ""` on Windows.

The same map is published at https://omer-yehuda.github.io/plugins/
