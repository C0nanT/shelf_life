# 04: Dar baixa e histórico

> **Difficulty:** Standard: **suggested model:** Sonnet (Claude Code) / Sonnet (Cursor). Suggestion only, use whatever model you have to hand.

**Spec:** ../SPEC.md

**What to build:** Informo quanto saiu de um alimento e o motivo ("usado" ou "jogado fora"). O sistema desconta da compra que vence antes, ou de uma compra que eu escolher. As baixas aparecem em um histórico simples.

**Seams:**
- Página/API

**Blocked by:** 01: Registrar compra e ver na lista

Status: ready-for-agent

- [ ] Sem compra escolhida, desconta da validade mais próxima e continua nas seguintes se precisar
- [ ] Compras sem validade são as últimas, e empates descontam primeiro a compra registrada há mais tempo
- [ ] É possível escolher a compra de onde descontar
- [ ] Baixa aceita g ou kg (ou ml ou L) dentro da família do alimento, com decimais
- [ ] Baixa maior que o disponível é rejeitada por inteiro, sem desconto parcial
- [ ] Compra zerada sai da lista principal e as baixas dela continuam no histórico
- [ ] Baixa que atravessa várias compras gera uma linha de histórico por compra
- [ ] Histórico mostra data, alimento, quantidade e motivo
