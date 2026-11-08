# 11: Test a PC reboot

> **Difficulty:** Light: **suggested model:** Haiku (Claude Code) / claude-4.5-haiku-thinking (Cursor). Suggestion only, use whatever model you have to hand.

> **Gate:** human: reboot the PC, without opening any program that uses Docker, and check that everything came back on its own

**Spec:** ../SPEC.md

**What to build:** Proof that, after the PC starts, warnings work again with no manual action, both in this system and in `homelab-monitoring`.

**Seams:** None

**Blocked by:** 10: Deploy on the PC

Status: ready-for-agent

- [ ] After the reboot, this project's containers and those of `homelab-monitoring` are running with no manual command
- [ ] The stock page opens and keeps the data from before the reboot
- [ ] The log shows the routine ran at startup
- [ ] A test item at a new milestone produces a real Telegram message
- [ ] The day's backup appears in the backup folder
