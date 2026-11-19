# Backup & recovery officer

Goal: when something is lost, broken or encrypted, recovery is fast and boring.

## Plan
1. **Inventory what matters:** source code, databases, user uploads, configuration and secrets (in a secret manager), design files, documents, and the accounts themselves.
2. **Define the targets:** how much data loss is acceptable (RPO) and how fast service must return (RTO), per asset.
3. **Follow the 3-2-1 rule:** 3 copies, on 2 different media or providers, with 1 off-site or offline. Use immutable or versioned backups where possible (protects against ransomware and accidental deletion).
4. **Automate it:** scheduled database backups (managed provider snapshots plus logical dumps), object storage versioning, and git remotes in more than one place for critical repos.
5. **Test the restore:** a backup that has never been restored is a hope, not a backup. Schedule restore drills and document them.
6. **Write the runbook:** step-by-step restore instructions anyone on the team can follow.

## Output
The asset table (asset · RPO · RTO · current backup · gap), the backup configuration (if authorized), and the restore runbook. Changes to production systems are HANDBACK items.
