# Observability

Goal: know about problems before users report them, and be able to diagnose them quickly.

## Minimum viable observability
- **Error tracking:** Sentry or an equivalent on the front end and back end, with source maps uploaded in CI, release tagging, and personal data scrubbing on.
- **Structured logs:** JSON logs with level, timestamp, request ID and user ID (hashed/internal ID only). No secrets or personal data. Pino for Node, structlog or the standard logging module with a JSON formatter for Python.
- **Health and uptime:** a `/health` endpoint, and an external uptime monitor with alerts.
- **Key metrics:** request rate, error rate, latency (p50/p95/p99), saturation (CPU/memory/DB connections), and business metrics (sign-ups, core actions, payments).
- **Alerts:** few and actionable (error spike, downtime, latency SLO breach), each with a short runbook link. Avoid alert fatigue.
- **Tracing** (when there are multiple services): OpenTelemetry.

## Output
The instrumentation plan, the code/config changes (if authorized), the alert list with thresholds, and a dashboard outline.
