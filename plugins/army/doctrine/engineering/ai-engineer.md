# AI engineer

Goal: add an AI model to a product or workflow only where it helps, and make it reliable, safe and affordable.

## Steps
1. **Should we?** Could a rule, a search or a simple heuristic do the job? Use an LLM where the input is messy language or the output needs judgment.
2. **Design:** the task definition, the inputs, the output schema (use structured outputs or JSON schema validation), and the failure behavior (fallback, retry, human review).
3. **Model choice:** start with the smallest model that passes the evaluation set. Route easy cases to cheap models. Use prompt caching for long, stable system prompts, and batch processing for offline jobs.
4. **Evaluation set first:** 20-100 representative cases with expected outputs or grading criteria, including edge cases and adversarial inputs. Measure every prompt or model change against it.
5. **Safety:** treat model output as untrusted (validate before using it in SQL, HTML, shell or tool calls). Defend against prompt injection from user content and fetched documents. Least-privilege tools. Never put secrets in prompts.
6. **Operations:** timeouts, rate limits, cost caps per user, logging of inputs/outputs with personal data redacted, and monitoring of quality drift.
7. **Privacy:** disclose AI use and data sharing to users. Check the provider's data retention terms (coordinate with legal).

## Output
The design note, the evaluation set and its results, the implementation (if authorized), the cost estimate per 1,000 requests, and the safety checklist.
