# Proving ground

Goal: a new skill, playbook, automation or tool proves itself before it enters service.

## Test protocol
1. **Trigger tests** (skills): 5 prompts that should trigger it, and 5 similar prompts that should not. Check the description against both sets.
2. **Function tests:** run it on 3 realistic tasks, including one edge case. Compare the output against the expected result or a quality rubric.
3. **Cost check:** how many tokens and tool calls does it use? Is there a cheaper path (smaller model, fewer files loaded)?
4. **Safety check:** could it perform irreversible actions without a handback? Does it handle untrusted input safely?
5. **Validation:** for plugin changes, run `claude plugin validate` and the repository's tests.

## Output
A test report: cases · expected · actual · PASS/FAIL, the cost measurement, the issues found, and a verdict: ready / ready with changes / not ready.
