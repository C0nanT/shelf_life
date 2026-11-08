# 10: Implantar no PC

> **Difficulty:** Heavy: **suggested model:** Opus (Claude Code) / Opus or the strongest reasoning model available (Cursor). Suggestion only, use whatever model you have to hand.

**Spec:** ../SPEC.md

**What to build:** O sistema roda em Docker no PC, acessível só nele e sem login. Sobe sozinho quando o Docker inicia. A rotina diária roda ao ligar e todo dia às 9h no fuso local.

**Seams:** None

**Blocked by:** 06: Avisos de validade no Telegram, 08: Backup diário, 09: Ligar o Docker ao iniciar o PC

Status: ready-for-agent

- [ ] Página escuta só no endereço local do PC, em porta sem conflito com os serviços existentes
- [ ] Container usa `restart: unless-stopped` e tem limite de memória
- [ ] Banco fica em armazenamento persistente e sobrevive à recriação do container
- [ ] Pasta de backups do PC é gravável pelo container, com arquivos no dono do usuário
- [ ] Rotina roda na subida do serviço e todo dia às 9h em `America/Sao_Paulo`
- [ ] Rotina não fica duas vezes em execução ao mesmo tempo
- [ ] Credenciais do Telegram entram por configuração fora do controle de versão, com arquivo de exemplo documentado
- [ ] Mensagem real de teste chega na conversa do Telegram
- [ ] README explica como subir, onde ficam os dados e como restaurar um backup
