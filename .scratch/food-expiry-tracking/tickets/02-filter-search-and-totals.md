# 02: Filter, search, and totals tab

> **Difficulty:** Standard: **suggested model:** Sonnet (Claude Code) / Sonnet (Cursor). Suggestion only, use whatever model you have to hand.

**Spec:** ../SPEC.md

**What to build:** On the main list, a filter by Pantry or Reserve and a search by name. In a second tab, I see the total of each food and how much of it is in each group.

**Seams:**
- Page/API

**Blocked by:** 01: Record a purchase and see it in the list

Status: ready-for-agent

- [ ] The filter shows only purchases from the chosen group, keeping the list order
- [ ] Search finds foods by name, case-insensitively
- [ ] The totals tab adds up each food's purchases and shows the split by group
- [ ] Totals add up purchases in units of the same family (g and kg, ml and L) correctly, with no rounding errors
- [ ] Code, identifiers, comments, tests, logs, commit messages, documentation, interface text, and Telegram messages are in English, not pt-BR
