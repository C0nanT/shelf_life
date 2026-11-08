# 08: Daily backup

> **Difficulty:** Standard: **suggested model:** Sonnet (Claude Code) / Sonnet (Cursor). Suggestion only, use whatever model you have to hand.

**Spec:** ../SPEC.md

**What to build:** The same daily routine saves a copy of the database in `/home/conan/Desktop/backups/shelf_life/` and keeps only the 7 most recent.

**Seams:**
- Daily routine

**Blocked by:** 06: Expiry warnings on Telegram

Status: ready-for-human

- [x] The copy is consistent even with the service in use and can be opened as a valid database
- [x] There is at most one copy per day, even with several runs in a day
- [x] Only the 7 most recent copies stay in the folder
- [x] Retention does not delete files that are not copies made by the routine
- [x] The backup runs even if sending to Telegram fails
- [x] The destination folder is created if it does not exist
- [x] Code, identifiers, comments, tests, logs, commit messages, documentation, interface text, and Telegram messages are in English, not pt-BR
