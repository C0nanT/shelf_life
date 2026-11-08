# 02: Filtro, busca e aba de totais

> **Difficulty:** Standard: **suggested model:** Sonnet (Claude Code) / Sonnet (Cursor). Suggestion only, use whatever model you have to hand.

**Spec:** ../SPEC.md

**What to build:** Na lista principal, filtro por Armário ou Reserva e busca por nome. Em uma segunda aba, vejo o total de cada alimento e quanto dele está em cada grupo.

**Seams:**
- Página/API

**Blocked by:** 01: Registrar compra e ver na lista

Status: ready-for-agent

- [ ] Filtro mostra só as compras do grupo escolhido, mantendo a ordem da lista
- [ ] Busca encontra alimentos pelo nome, sem diferenciar maiúsculas
- [ ] Aba de totais soma as compras de cada alimento e mostra a separação por grupo
- [ ] Totais somam corretamente compras em medidas da mesma família (g e kg, ml e L), sem erro de arredondamento
