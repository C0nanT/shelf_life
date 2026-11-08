# 04: Removals and history

> **Difficulty:** Standard: **suggested model:** Sonnet (Claude Code) / Sonnet (Cursor). Suggestion only, use whatever model you have to hand.

**Spec:** ../SPEC.md

**What to build:** I enter how much of a food left and the reason ("used" or "discarded"). The system deducts from the purchase that expires first, or from a purchase I choose. Removals appear in a simple history.

**Seams:**
- Page/API

**Blocked by:** 01: Record a purchase and see it in the list

Status: ready-for-agent

- [ ] With no purchase chosen, it deducts from the nearest expiry and continues into the next ones if needed
- [ ] Purchases without an expiry date come last, and ties deduct the purchase recorded earliest first
- [ ] It is possible to choose the purchase to deduct from
- [ ] A removal accepts g or kg (or ml or L) within the food's family, with decimals
- [ ] A removal larger than what is available is rejected entirely, with no partial deduction
- [ ] A purchase that reaches zero leaves the main list and its removals stay in the history
- [ ] A removal spanning several purchases creates one history line per purchase
- [ ] History shows date, food, quantity, and reason
- [ ] Code, identifiers, comments, tests, logs, commit messages, documentation, interface text, and Telegram messages are in English, not pt-BR
