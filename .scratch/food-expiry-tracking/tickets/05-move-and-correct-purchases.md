# 05: Move and correct purchases

> **Difficulty:** Standard: **suggested model:** Sonnet (Claude Code) / Sonnet (Cursor). Suggestion only, use whatever model you have to hand.

**Spec:** ../SPEC.md

**What to build:** I move a whole purchase or part of it between Pantry and Reserve. I edit any field of a purchase or delete a record made by mistake, without it counting as consumption or waste.

**Seams:**
- Page/API

**Blocked by:** 01: Record a purchase and see it in the list, 04: Removals and history

Status: ready-for-agent

- [ ] Moving a whole purchase changes its group
- [ ] Moving part creates another purchase with the same expiry date in the destination group and reduces the original
- [ ] Moving more than what is available is rejected
- [ ] Editing quantity, expiry date, unit within the same family, or group updates list and totals
- [ ] Deleting a purchase removes it from the list and totals
- [ ] Editing and deleting create no line in the removal history
- [ ] Earlier removals of a deleted purchase stay in the history
- [ ] Code, identifiers, comments, tests, logs, commit messages, documentation, interface text, and Telegram messages are in English, not pt-BR
