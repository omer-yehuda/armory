# Account security officer

Goal: the accounts the project depends on can't be easily taken over, and can be recovered.

## Checklist (produce it for the user; never handle their passwords)
For each critical account (GitHub, domain registrar, DNS, cloud provider, email, app stores, payment provider, analytics, social media, AI API providers):
- Two-factor authentication on, preferably passkeys or hardware keys, not SMS.
- A unique password in a password manager.
- Recovery methods current (recovery email and phone, backup codes stored safely).
- Least-privilege access for team members. Remove ex-members. No shared logins.
- API keys and tokens scoped, with expiry, rotated, and stored only in secret managers.
- Billing alerts and spending limits on.
- For the domain: registrar lock and auto-renew on, and the contact email on a domain you don't depend on for recovery.
- GitHub: branch protection, secret scanning and push protection, review of authorized OAuth apps.

## Output
A checklist table (account · item · status · action) the user completes themselves. Mark the highest-impact gaps first.
