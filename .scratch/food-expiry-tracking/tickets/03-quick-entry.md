# 03: Quick entry

> **Difficulty:** Standard: **suggested model:** Sonnet (Claude Code) / Sonnet (Cursor). Suggestion only, use whatever model you have to hand.

**Spec:** ../SPEC.md

**What to build:** Entering the whole current stock without friction. The name autocompletes from existing foods, the unit comes filled in, and the "save and add another" button keeps the form open for the next purchase.

**Seams:**
- Page/API

**Blocked by:** 01: Record a purchase and see it in the list

Status: ready-for-human

- [x] Typing part of a name suggests existing foods
- [x] Choosing an existing food fills in its unit
- [x] "Save and add another" records the purchase and leaves the form ready for the next one
- [x] Beyond name, quantity, unit, and group, no field is required
- [x] Code, identifiers, comments, tests, logs, commit messages, documentation, interface text, and Telegram messages are in English, not pt-BR
