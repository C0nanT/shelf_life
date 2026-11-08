# 01: Registrar compra e ver na lista

> **Difficulty:** Standard: **suggested model:** Sonnet (Claude Code) / Sonnet (Cursor). Suggestion only, use whatever model you have to hand.

**Spec:** ../SPEC.md

**What to build:** Primeira fatia completa do projeto novo. Em uma página local, registro uma compra com nome, quantidade, medida, validade e grupo (Armário ou Reserva). O alimento nasce sozinho na primeira compra daquele nome. A compra aparece na lista principal, ordenada pela validade mais próxima, com vencidos no topo e em destaque.

**Seams:**
- Página/API

**Blocked by:** None (can start immediately)

Status: ready-for-agent

- [ ] Projeto novo criado com Python, Flask e SQLite, com o padrão de testes da spec funcionando
- [ ] Registrar compra aceita unidade, g, kg, ml e L, com decimais
- [ ] Validade aceita data completa, só mês e ano (vale até o último dia do mês e é exibida como mês e ano) ou vazio
- [ ] Primeira compra de um nome novo cria o alimento com sua medida
- [ ] "Arroz" e "arroz" contam como o mesmo alimento
- [ ] Compra de medida de família diferente da do alimento é rejeitada
- [ ] Cada compra é um registro próprio, com quantidade, validade e grupo
- [ ] Lista mostra vencidos no topo e em destaque, depois validade mais próxima, e por último compras sem validade
