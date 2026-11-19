---
name: map
description: Generate the interactive army map (an HTML page with every unit, specialist playbook, model routing, a mission simulator and the commands). Use only when the user explicitly asks to see or generate the army map, or runs /army:map.
---

Run:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/build-map.js" --out ".army/army-map.html"
```

The map is generated from the plugin's own files, so it always reflects the installed version.

Then tell the user where the file is (an absolute path) and how to open it in a browser. If the user asks you to open it, use the platform's opener: `open` on macOS, `xdg-open` on Linux, or `start ""` on Windows.

The same map is also published online: https://omer-yehuda.github.io/plugins/
