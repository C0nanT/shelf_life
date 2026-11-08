# 07: Página Alimentos

> **Difficulty:** Standard: **suggested model:** Sonnet (Claude Code) / Sonnet (Cursor). Suggestion only, use whatever model you have to hand.

**Spec:** ../SPEC.md

**What to build:** Uma página simples para renomear alimentos, juntar duplicados como "Arrroz" e "Arroz", e definir prazos de aviso próprios para um alimento.

**Seams:**
- Página/API
- Rotina diária

**Blocked by:** 04: Dar baixa e histórico, 06: Avisos de validade no Telegram

Status: ready-for-agent

- [ ] Renomear para nome livre só muda o nome
- [ ] Renomear para nome existente pede confirmação e, confirmado, move compras e histórico para o alimento de destino
- [ ] Junção mantém os prazos de exceção do alimento de destino
- [ ] Junção entre famílias de medida diferentes é bloqueada
- [ ] Trocar a família de medida é bloqueado enquanto houver compras registradas
- [ ] Prazos de exceção substituem os do grupo para esse alimento, em qualquer grupo
- [ ] Alterar os prazos de exceção recalcula os avisos das compras do alimento
- [ ] Nenhum campo é obrigatório além de nome e medida
