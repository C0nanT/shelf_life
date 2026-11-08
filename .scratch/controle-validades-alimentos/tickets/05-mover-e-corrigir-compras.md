# 05: Mover e corrigir compras

> **Difficulty:** Standard: **suggested model:** Sonnet (Claude Code) / Sonnet (Cursor). Suggestion only, use whatever model you have to hand.

**Spec:** ../SPEC.md

**What to build:** Movo uma compra inteira ou parte dela entre Armário e Reserva. Edito qualquer campo de uma compra ou apago um registro feito por engano, sem que isso conte como consumo ou desperdício.

**Seams:**
- Página/API

**Blocked by:** 01: Registrar compra e ver na lista, 04: Dar baixa e histórico

Status: ready-for-agent

- [ ] Mover a compra inteira troca o grupo dela
- [ ] Mover parte cria outra compra com a mesma validade no grupo de destino e reduz a original
- [ ] Mover mais que o disponível é rejeitado
- [ ] Editar quantidade, validade, medida da mesma família ou grupo atualiza lista e totais
- [ ] Apagar compra remove ela da lista e dos totais
- [ ] Editar e apagar não geram linha no histórico de baixas
- [ ] Baixas anteriores de uma compra apagada continuam no histórico
