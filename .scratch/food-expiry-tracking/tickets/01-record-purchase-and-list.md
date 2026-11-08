# 01: Record a purchase and see it in the list

> **Difficulty:** Standard: **suggested model:** Sonnet (Claude Code) / Sonnet (Cursor). Suggestion only, use whatever model you have to hand.

**Spec:** ../SPEC.md

**What to build:** The first complete slice of the new project. On a local page, I record a purchase with name, quantity, unit, expiry date, and group (Pantry or Reserve). The food is created automatically on the first purchase of that name. The purchase appears in the main list, sorted by nearest expiry, with expired items at the top and highlighted.

**Seams:**
- Page/API

**Blocked by:** None (can start immediately)

Status: ready-for-human

- [x] New project created with Python, Flask, and SQLite, with the spec's test pattern working
- [x] Recording a purchase accepts unit, g, kg, ml, and L, with decimals
- [x] Expiry accepts a full date, month and year only (valid through the last day of the month and displayed as month and year), or blank
- [x] The first purchase of a new name creates the food with its unit
- [x] "Rice" and "rice" count as the same food
- [x] A purchase in a different unit family from the food's is rejected
- [x] Each purchase is its own record, with quantity, expiry date, and group
- [x] The list shows expired items at the top and highlighted, then nearest expiry, and purchases without an expiry date last
- [x] Code, identifiers, comments, tests, logs, commit messages, documentation, interface text, and Telegram messages are in English, not pt-BR
