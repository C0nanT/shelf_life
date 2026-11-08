# Food expiry tracking

Status: ready-for-agent

## Problem Statement

I am building a food stock at home, split between what stays in the pantry and gets eaten day to day and a long-term reserve for emergencies. I need to know how much I have of each food (in units, weight, or volume) and when each purchase expires, and I need a warning before anything expires.

I tried Grocy and it does far more than I need: registering items is heavy and it does not warn me on Telegram. A plain text list would be too simple, because it cannot track quantity or partial removals.

## Solution

A local page, used in the PC's browser, where I record each purchase with a few fields: name, quantity, unit, expiry date, and group (Pantry or Reserve). The main screen shows everything by nearest expiry. When I use or throw something away, I enter how much left and the system deducts it from the purchase that expires first.

A daily routine checks expiry dates and sends at most one Telegram message per day, only when an item reaches a warning milestone. The same routine makes a backup of the database.

## User Stories

### Recording purchases

1. As the stock owner, I want to record a purchase with only name, quantity, unit, expiry date, and group, so that I do not waste time on detailed registration.
2. As the stock owner, I want a new food to be created automatically on the first purchase of that name, so that I do not have to go through a registration screen first.
3. As the stock owner, I want the name to autocomplete and the unit to be filled in on later purchases, so that I type less.
4. As the stock owner, I want "Rice" and "rice" to be the same food, so that capitalization does not create duplicates.
5. As the stock owner, I want a "save and add another" button, so that I can quickly enter my whole current stock.
6. As the stock owner, I want the same food recorded as separate purchases, each with its own quantity and expiry date, so that expiry stays correct when purchases get mixed.
7. As the stock owner, I want to choose between unit, g, kg, ml, and L, so that I can track any kind of food.
8. As the stock owner, I want to enter decimal quantities, such as 0.5 kg, so that I record the real amount.
9. As the stock owner, I want to enter an expiry date with day, month, and year, so that I record what is on the package.
10. As the stock owner, I want to enter an expiry date with only month and year, valid through the last day of the month, because many long-life foods only show that.
11. As the stock owner, I want to leave the expiry date blank, so that I can record items such as salt, which never trigger warnings.
12. As the stock owner, I want to set whether each purchase belongs to the Pantry or the Reserve, so that the same food can be in both groups.

### Viewing the stock

13. As the stock owner, I want a single list sorted by nearest expiry, so that I see first what needs attention.
14. As the stock owner, I want expired items at the top and highlighted, so that I do not miss them.
15. As the stock owner, I want to filter the list by Pantry or Reserve, so that I can look at each group separately.
16. As the stock owner, I want to search by name, so that I can find a food quickly.
17. As the stock owner, I want a tab with the total of each food and its split by group, so that I know how much I have overall.

### Recording removals

18. As the stock owner, I want to enter how much of a food left, so that I can record partial consumption.
19. As the stock owner, I want a removal to deduct first from the purchase that expires first, so that food is consumed in the right order without me thinking about it.
20. As the stock owner, I want to be able to choose another purchase to deduct from, for when I actually take a different package.
21. As the stock owner, I want to enter a removal in g or kg (or ml or L) regardless of the food's unit, as long as it is in the same family, so that I can use the most practical unit.
22. As the stock owner, I want to mark the reason as "used" or "discarded", so that I can distinguish consumption from waste.
23. As the stock owner, I want a removal larger than what is available to be blocked, so that stock never goes negative.
24. As the stock owner, I want a purchase that reaches zero to leave the main list and stay in the history, so that the list only shows what exists.
25. As the stock owner, I want a simple history with date, food, quantity, and reason, so that I can check what left.

### Moving and correcting

26. As the stock owner, I want to move a whole purchase or part of it between Pantry and Reserve, so that I can rotate the reserve before it expires.
27. As the stock owner, I want to edit any field of a purchase, so that I can fix typing or counting mistakes.
28. As the stock owner, I want to edit a purchase's expiry date manually, so that I can adjust it when I open something that spoils faster.
29. As the stock owner, I want to delete a purchase recorded by mistake, so that I can correct the stock.
30. As the stock owner, I want corrections and deletions not to count as "used" or "discarded", so that consumption and waste numbers stay clean.

### Managing foods

31. As the stock owner, I want a simple "Foods" page, so that I can rename a food and set exceptions.
32. As the stock owner, I want to rename a food to an existing name and merge the two after confirming, so that I can fix cases such as "Riice" and "Rice" without losing records.
33. As the stock owner, I want a merge to be blocked when units belong to different families, so that weight is not added to volume or units.
34. As the stock owner, I want changing a food's unit family to be blocked while it has recorded purchases, so that existing quantities are not invalidated.
35. As the stock owner, I want to set a food's own warning milestones, so that I can handle cases that do not fit the group's rule.

### Receiving warnings

36. As the stock owner, I want to be warned 7 days before and on the expiry day for Pantry items, because they are consumed quickly.
37. As the stock owner, I want to be warned 30 and 7 days before and on the expiry day for Reserve items, so that I have time to eat them day to day before they expire.
38. As the stock owner, I want at most one Telegram message per day combining all items, so that I am not bothered.
39. As the stock owner, I want no message on days without a new milestone, so that warnings stay relevant.
40. As the stock owner, I want messages to come from the bot I already use and start with "Stock", so that I can tell them apart from site alerts.
41. As the stock owner, I want the check to run when the PC starts and every day at 9:00 without duplicate warnings, so that nothing is missed even when I turn the PC on at varying times.
42. As the stock owner, I want an item recorded already inside a warning period to appear once in the next digest with the real days left, so that I am not warned only on the expiry day.
43. As the stock owner, I want to see only each item's most recent milestone after a long time with the PC off, so that I do not get repeated late warnings.
44. As the stock owner, I want moving a purchase or changing its expiry date to recalculate warnings, so that milestones match the new situation.
45. As the stock owner, I want warnings for an item to stop after it expires, while it stays highlighted in the list until I record a removal, so that I am not nagged every day.

### Running and protecting the data

46. As the stock owner, I want the system to start on its own when the PC starts, so that I do not have to remember to launch it.
47. As the stock owner, I want the system to be reachable only from this PC and to open without a login, so that it is frictionless and the data is not exposed.
48. As the stock owner, I want a daily database backup in `/home/conan/Desktop/backups/shelf_life/`, so that I can recover the stock after a mistake or a corrupted database.
49. As the stock owner, I want to keep only the 7 most recent backups, so that the folder does not grow without limit.

## Implementation Decisions

### Technology and deployment

- A new, small project, separate from `price_trail` and `homelab-monitoring`. Same technologies as `price_trail`: Python, Flask, and SQLite.
- The reason for the separation: stock data is typed by hand and has no other source, while `price_trail` data can be reimported from PDFs.
- The service listens only on the PC's local address, without a login. Phone access is future work and will require deciding on access and authentication.
- Everything in the project is in English, with no pt-BR: code, identifiers (modules, functions, tables, columns, routes), comments, tests, logs, commit messages, documentation including the README, interface text, and Telegram messages.
- The service starts on its own when the PC starts, running in Docker.
- It uses the same Telegram bot and chat as the site alerts. The token and chat identifier are configuration for the new project, kept out of version control.

### Modules

- **Stock**: rules for foods, purchases, removals, moves, corrections, and merges. All business rules live here, independent of the web layer.
- **Units**: unit families, conversion, and quantity normalization.
- **Warnings**: given the stock state and the current date, decides which purchases enter the digest and builds the text. No network access.
- **Telegram sender**: sends the digest. Replaceable in tests.
- **Backup**: copies the database safely, even while the service is in use, and applies retention.
- **Daily routine**: a single command that runs the check, send, and backup, receiving the date, sender, and destination folder from outside.
- **Web**: pages and API. Only translates requests into calls to the Stock module.

### Data model

- **Food**: display name, unique normalized name (trimmed and case-insensitive), unit, and optional exception warning milestones.
- **Purchase**: food, remaining quantity, optional expiry date, expiry precision (day or month), group (Pantry or Reserve), recorded date, and last warned milestone.
- **Removal**: date, food, source purchase, quantity, and reason (used or discarded). Removals stay in the history even if the purchase reaches zero or is deleted.
- Quantities are stored exactly, with no floating-point rounding errors.

### Units

- Allowed units: unit, g, kg, ml, and L.
- Families: weight (g, kg), volume (ml, L), and unit. Conversion only happens within a family (1000 g = 1 kg, 1000 ml = 1 L).
- There is no conversion such as "1 package = 500 g".
- Each food belongs to one family, set on its first purchase. Changing family is blocked while purchases are recorded.

### Expiry

- An expiry date with month and year is valid through the last day of the month, and keeps being displayed as month and year.
- Purchases without an expiry date never trigger warnings and appear after those with an expiry date in the list.

### Removal rules

- With no purchase chosen, a removal deducts from the nearest expiry and continues into the next purchases if needed. Purchases without an expiry date come last.
- A removal that spans several purchases creates one history line per purchase.
- A removal larger than what is available is rejected entirely, with no partial deduction.
- A purchase that reaches zero leaves the main list.

### Moves and corrections

- Moving part of a purchase creates another purchase with the same expiry date in the destination group.
- Editing and deleting purchases does not create removals.
- Opening a package has no special handling. If it spoils faster, the expiry date is edited by hand.

### Merging foods

- Renaming to an existing name asks for confirmation and moves purchases and history to the destination food.
- A merge between different unit families is blocked.

### Warnings

- Default milestones: Pantry at 7 and 0 days; Reserve at 30, 7, and 0 days. A food's exception replaces its group's milestones.
- For each purchase with a balance and an expiry date, with `d` days left, the **current milestone** is the smallest milestone greater than or equal to `d`. A purchase with negative `d` uses milestone 0.
- A purchase enters the digest when it has a current milestone and it differs from the last warned milestone. The digest shows the real days left (or how many days ago it expired).
- After sending, the current milestone is saved as the last warned milestone of each included purchase. After milestone 0, the purchase triggers no new warnings.
- Moving a purchase between groups, changing its expiry date, or changing the food's milestones clears the last warned milestone. A purchase created by a partial move starts with no warned milestone.
- A partial removal does not change milestones.
- With no purchase to warn about, nothing is sent.
- The routine runs when the PC starts and every day at 9:00 local time. Running several times on the same day does not duplicate warnings, because control is per warned milestone.

### Backup

- The daily routine saves one copy of the database per day in `/home/conan/Desktop/backups/shelf_life/` and keeps the 7 most recent.
- That folder is on the same PC, so the copy protects against mistakes and a corrupted database, but not against disk failure or loss of the PC. This risk is accepted for now.

### Screens

- **Main list**: purchases with a balance by nearest expiry, expired ones at the top and highlighted, group filter, and name search. Actions to record a removal, move, edit, and delete.
- **Totals**: total per food, with the split by group.
- **New purchase**: form with name autocomplete and a "save and add another" button.
- **History**: list of removals with date, food, quantity, and reason, with no charts.
- **Foods**: rename, merge, and set exception milestones. No required fields beyond name and unit.

## Testing Decisions

A good test checks behavior visible from outside: what the API returns, what appears in lists, what would be sent to Telegram, and the files produced. It does not test tables, internal functions, or implementation details.

Agreed seams:

- **Page/API**: HTTP requests to the Flask application, with a temporary database. Covers purchases, removals, moves, corrections, food merges, totals, history, and validations.
- **Daily routine**: a call to the single check-and-backup command, with a simulated date, fake Telegram sender, and temporary folder. Covers milestones, single digest, no duplicate warnings, long periods with the PC off, recalculation after moves or edits, and retention of 7 backups.

Modules covered: Stock, Units, Warnings, and Backup are exercised through these two seams, with no direct tests. There are no browser tests.

Prior art: the `price_trail` tests follow this pattern, with a base API test case using the Flask test client and dedicated backup tests.

## Out of Scope

- Barcodes.
- Prices.
- Shopping list.
- Minimum stock.
- Recipes.
- Importing `price_trail` receipts.
- Marking a package as opened with its own expiry.
- Calculating reserve autonomy (days for a number of people).
- Conversion between unit families or between package and weight.
- Phone access and login.
- Consumption or waste charts.
- Backups outside the PC.
- Integration with Grafana or Prometheus.

## Further Notes

Decisions not explicitly discussed, assumed in this spec and easy to change:

- If sending to Telegram fails, no milestone is saved as warned and the next run tries again. The failure is logged. The backup runs even if sending fails.
- A food's exception milestones apply to that food in any group.
- A purchase recorded already expired enters the next digest once, stating how many days ago it expired, following the same rule as an item already inside a warning period.
- When merging foods, the destination food's exception milestones are kept.
- "Jalapeño" and "jalapeno" count as different foods, and a merge resolves that case.
- If expiry dates tie in an automatic removal, the purchase recorded earliest is deducted first.

The Docker service was enabled at PC startup on 2026-11-08. A real reboot still has to confirm that everything comes back on its own.
