# 06: Expiry warnings on Telegram

> **Difficulty:** Standard: **suggested model:** Sonnet (Claude Code) / Sonnet (Cursor). Suggestion only, use whatever model you have to hand.

**Spec:** ../SPEC.md

**What to build:** A single command checks expiry dates and sends a Telegram digest with the purchases that reached a warning milestone. Running the command several times does not repeat warnings. Pantry warns at 7 and 0 days, Reserve at 90, 30, 7, and 0 days.

**Seams:**
- Daily routine

**Blocked by:** 01: Record a purchase and see it in the list, 05: Move and correct purchases

Status: ready-for-agent

- [ ] The digest is a single message, starts with "Stock", and shows the real days left or how many days ago the item expired
- [ ] With no new milestone, nothing is sent
- [ ] Running the command again does not duplicate warnings
- [ ] An item already inside a warning period when recorded enters the next digest once and then follows normal milestones
- [ ] After a long time without running, each item appears only once, with its most recent milestone
- [ ] An item already expired when recorded enters once and then triggers no new warnings
- [ ] An expired item triggers no new warnings after milestone 0
- [ ] Purchases with no expiry date or zero balance trigger no warnings
- [ ] Moving between groups or changing the expiry date recalculates warnings, and a partial removal does not
- [ ] A purchase created by a partial move starts with no warned milestone
- [ ] If sending fails, no milestone is saved, the failure is logged, and the next run tries again
- [ ] Telegram token and chat come from configuration outside version control
- [ ] Code, identifiers, comments, tests, logs, commit messages, documentation, interface text, and Telegram messages are in English, not pt-BR
