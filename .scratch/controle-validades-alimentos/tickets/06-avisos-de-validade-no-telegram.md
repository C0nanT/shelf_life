# 06: Avisos de validade no Telegram

> **Difficulty:** Standard: **suggested model:** Sonnet (Claude Code) / Sonnet (Cursor). Suggestion only, use whatever model you have to hand.

**Spec:** ../SPEC.md

**What to build:** Um comando único olha as validades e manda no Telegram um resumo com as compras que chegaram a um marco de aviso. Rodar o comando várias vezes não repete aviso. Armário avisa em 7 e 0 dias, Reserva em 90, 30, 7 e 0 dias.

**Seams:**
- Rotina diária

**Blocked by:** 01: Registrar compra e ver na lista, 05: Mover e corrigir compras

Status: ready-for-agent

- [ ] Resumo é uma mensagem única, começa com "Estoque" e mostra os dias reais restantes ou há quantos dias venceu
- [ ] Sem marco novo, nada é enviado
- [ ] Rodar o comando de novo não duplica aviso
- [ ] Item já dentro de um prazo ao ser cadastrado entra uma vez no próximo resumo e depois segue os marcos normais
- [ ] Depois de muito tempo sem rodar, cada item aparece só uma vez, com o marco mais recente
- [ ] Item já vencido ao cadastrar entra uma vez e depois não gera novos avisos
- [ ] Item vencido não gera novos avisos depois do marco 0
- [ ] Compras sem validade ou zeradas não geram aviso
- [ ] Mover de grupo ou mudar validade recalcula os avisos, e baixa parcial não recalcula
- [ ] Compra criada ao mover parte começa sem marco avisado
- [ ] Se o envio falhar, nenhum marco é gravado, a falha fica em log e a próxima execução tenta de novo
- [ ] Token e conversa do Telegram vêm de configuração fora do controle de versão
