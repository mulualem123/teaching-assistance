# Git history cleanup plan

This document contains a safe, step-by-step plan to remove sensitive files (credentials, DBs, tokens) from the repository history. This is a destructive operation for published history and requires coordination.

SUMMARY
- Goal: remove previously committed sensitive files (for example `flask_package/__init__.py` hard-coded tokens, `instance/site.db`, any `.env` with secrets) from git history and force-push a cleaned history to remote.
- Note: After history rewrite, all collaborators must re-clone or reset their local clones. Old refs and tags referencing removed data will be lost.

PREPARE
1. Backup current repo (local copy):
   - Create a full filesystem copy of the repository directory (outside the repo) or ensure you have an alternative clone:
     - e.g. `cp -r teaching-assistance teaching-assistance-backup-$(date +%Y%m%d)` (or copy in Explorer on Windows).
2. Export a list of suspected sensitive paths (examples found in repo):
   - `flask_package/instance/site.db`
   - `flask_package/__init__.py` (contains SECRET_KEY, SALT, TELEGRAM token, MAIL_USERNAME)
   - `flask_package/__init__ 3-4-25.py` (duplicate with secrets)
   - any other files you identify with secrets
   Save this list to `sensitive-paths.txt`.

IDENTIFY
3. Double-check whether these are currently present on remote (they may already be removed). Run:
   - `git log --all --pretty=format:"%H %ae %s" -- <path>` for each path to see which commits reference it.

CLEANUP OPTIONS
- Recommended: use `git filter-repo` (fast, robust) if available.
- Alternative: use BFG Repo-Cleaner (simpler if you only need to remove files or replace text tokens).

A. Cleanup with git filter-repo (recommended)
1) Install filter-repo (if not installed):
   - `pip install git-filter-repo` (or platform packaging).
2) Make a fresh clone (bare) to operate on:
   - `git clone --mirror https://github.com/<user>/teaching-assistance.git repo-mirror.git`
   - `cd repo-mirror.git`
3) Run filter-repo to remove files or match patterns:
   - Remove paths listed in a file:
     - `git filter-repo --paths-from-file ../sensitive-paths.txt --invert-paths`
     (the file lists the paths to remove, one per line)
   - Or remove by pattern (example for keys):
     - `git filter-repo --replace-text replace-rules.txt`
     where `replace-rules.txt` contains patterns to replace.
4) Verify the new history locally (inspect refs and logs).
5) Force push cleaned mirror to remote:
   - `git push --force --all origin`
   - `git push --force --tags origin`

B. Cleanup with BFG (simpler for files)
1) Download BFG jar.
2) Mirror clone:
   - `git clone --mirror https://github.com/<user>/teaching-assistance.git`
3) Remove files:
   - `java -jar bfg.jar --delete-files sensitive-filenames.txt repo.git`
4) Follow BFG instructions (run `git reflog expire --expire=now --all && git gc --prune=now --aggressive`).
5) Force push:
   - `git push --force --all origin`
   - `git push --force --tags origin`

IMPORTANT CHECKLIST BEFORE RUNNING
- [ ] Confirm the exact list of files/paths that must be removed.
- [ ] Rotate any leaked credentials immediately (Telegram token, any API keys, email passwords) — even if history is rewritten, assume leak occurred.
- [ ] Notify collaborators and schedule a freeze window (no pushes during rewrite).
- [ ] Make a backup clone (outside the repo folder).
- [ ] Ensure you have push rights on remote and are prepared to force-push.

AFTER CLEANUP
1. Run garbage collection and expiry steps (BFG/git-filter-repo will suggest commands):
   - `git for-each-ref --format='delete %(refname)' refs/original | xargs -r git update-ref --stdin`
   - `git reflog expire --expire=now --all`
   - `git gc --prune=now --aggressive`
2. Force-push cleaned refs to remote (see above).
3. Ask all collaborators to re-clone the repository (or to reset local branches):
   - `git fetch origin --prune`
   - Or simpler: delete local clone and re-clone fresh.
4. Verify remote no longer contains the sensitive blobs:
   - Use `git log --all -- <path>` to confirm removal.

ROLLBACK PLAN
- If anything goes wrong, use the backup clone to restore the prior state and push it (if necessary), then investigate.

SECURITY FOLLOW-UP
- Rotate any keys/secrets and update the apps to read from environment variables.
- Consider using a secrets manager for production (Vault, AWS Secrets Manager, etc.).

If you want, I can:
- Prepare `sensitive-paths.txt` from the files I found and place it in the repo for review.
- Run the mirror + `git filter-repo` steps locally (I will NOT force-push without explicit confirmation).
- Or, if you'd prefer BFG, I can prepare the exact commands and help execute them after your approval.

---
Created by the repository maintenance workflow. If you want me to proceed with an actual history rewrite, reply with explicit confirmation and the files you want removed (or say "use my detected list").
