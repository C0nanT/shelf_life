# 10: Deploy on the PC

> **Difficulty:** Heavy: **suggested model:** Opus (Claude Code) / Opus or the strongest reasoning model available (Cursor). Suggestion only, use whatever model you have to hand.

**Spec:** ../SPEC.md

**What to build:** The system runs in Docker on the PC, reachable only from it and without a login. It starts on its own when Docker starts. The daily routine runs at startup and every day at 9:00 local time.

**Seams:** None

**Blocked by:** 06: Expiry warnings on Telegram, 08: Daily backup, 09: Start Docker when the PC boots

Status: ready-for-agent

- [ ] The page listens only on the PC's local address, on a port that does not conflict with existing services
- [ ] The container uses `restart: unless-stopped` and has a memory limit
- [ ] The database is in persistent storage and survives recreating the container
- [ ] The PC's backup folder is writable by the container, with files owned by the user
- [ ] The routine runs at service startup and every day at 9:00 in `America/Sao_Paulo`
- [ ] The routine never runs twice at the same time
- [ ] Telegram credentials come from configuration outside version control, with a documented example file
- [ ] A real test message reaches the Telegram chat
- [ ] The README explains how to start the system, where the data lives, and how to restore a backup
- [ ] Code, identifiers, comments, tests, logs, commit messages, documentation, interface text, and Telegram messages are in English, not pt-BR
