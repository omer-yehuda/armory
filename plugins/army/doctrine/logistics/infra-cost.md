# Infrastructure & cost

Goal: infrastructure that fits the load and the budget, with no surprises on the bill.

## Steps
1. Estimate the load: users, requests per second at peak, storage growth, bandwidth, background jobs, AI/API calls.
2. Size the components for current load with 2-3x headroom. Note what triggers the next tier.
3. Price each component at low, expected and high load using current pricing pages (verify and date them). Include free-tier limits and what happens when they're exceeded.
4. Identify the cost traps: egress bandwidth, per-seat pricing, serverless at sustained load, log and metric ingestion, managed database minimums, idle preview environments, uncapped AI API usage.
5. Recommend guardrails: budget alerts, spending caps, rate limits on expensive endpoints, autoscaling limits.

## Output
Architecture-to-cost table · monthly estimate in three scenarios · cost traps · guardrails. Hand the deeper business economics to treasury.
