# 11: Testar reinício do PC

> **Difficulty:** Light: **suggested model:** Haiku (Claude Code) / claude-4.5-haiku-thinking (Cursor). Suggestion only, use whatever model you have to hand.

> **Gate:** human: reiniciar o PC, sem abrir nenhum programa que use Docker, e conferir que tudo voltou sozinho

**Spec:** ../SPEC.md

**What to build:** Prova de que, depois de ligar o PC, os avisos voltam a funcionar sem nenhuma ação manual, tanto neste sistema quanto no `homelab-monitoring`.

**Seams:** None

**Blocked by:** 10: Implantar no PC

Status: ready-for-agent

- [ ] Depois do reinício, os containers deste projeto e do `homelab-monitoring` estão rodando sem nenhum comando manual
- [ ] Página do estoque abre e mantém os dados de antes do reinício
- [ ] Log mostra que a rotina rodou na subida
- [ ] Item de teste num marco novo gera mensagem real no Telegram
- [ ] Cópia do dia aparece na pasta de backups
