# 07: Foods page

> **Difficulty:** Standard: **suggested model:** Sonnet (Claude Code) / Sonnet (Cursor). Suggestion only, use whatever model you have to hand.

**Spec:** ../SPEC.md

**What to build:** A simple page to rename foods, merge duplicates such as "Riice" and "Rice", and set a food's own warning milestones.

**Seams:**
- Page/API
- Daily routine

**Blocked by:** 04: Removals and history, 06: Expiry warnings on Telegram

Status: ready-for-human

- [x] Renaming to an unused name only changes the name
- [x] Renaming to an existing name asks for confirmation and, once confirmed, moves purchases and history to the destination food
- [x] A merge keeps the destination food's exception milestones
- [x] A merge between different unit families is blocked
- [x] Changing the unit family is blocked while purchases are recorded
- [x] Exception milestones replace the group's for that food, in any group
- [x] Changing exception milestones recalculates warnings for the food's purchases
- [x] No field is required beyond name and unit
- [x] Code, identifiers, comments, tests, logs, commit messages, documentation, interface text, and Telegram messages are in English, not pt-BR
