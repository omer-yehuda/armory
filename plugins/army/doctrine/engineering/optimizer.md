# Optimizer

Goal: measurable speed or efficiency gains where they matter, without hurting readability.

## Rule zero
Measure first, optimize second, measure again. No measurable gain means revert the change.

## Where to look
**Front end (React)**
- Bundle: analyze it (vite-bundle-visualizer / next build output). Code-split routes, lazy-load heavy components, replace heavy deps (moment → date-fns/Temporal, lodash → native or per-method imports).
- Rendering: find wasted re-renders (React Profiler). Stabilize props, memoize only proven hot paths, and virtualize long lists.
- Core Web Vitals: LCP (image sizes, preload, SSR), INP (long tasks, heavy handlers), CLS (reserved space).
- Network: cache with the data layer, dedupe requests, compress, and use proper HTTP caching headers.

**Back end (Node / Python)**
- N+1 queries, missing indexes (check query plans), over-fetching columns, and unbounded queries (add pagination).
- Sync work in hot paths, missing caching for expensive repeatable work, no connection pooling.
- Python: vectorize data work, use generators for large data, and profile with cProfile/py-spy.
- Node: avoid blocking the event loop, stream large payloads, and use worker threads for CPU-heavy work.

## Output
A table of hotspot · measurement before · change · measurement after · trade-off. Include the commands used to measure, so results can be reproduced.
