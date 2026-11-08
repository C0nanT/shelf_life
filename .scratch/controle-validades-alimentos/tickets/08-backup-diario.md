# 08: Backup diário

> **Difficulty:** Standard: **suggested model:** Sonnet (Claude Code) / Sonnet (Cursor). Suggestion only, use whatever model you have to hand.

**Spec:** ../SPEC.md

**What to build:** A mesma rotina diária grava uma cópia do banco em `/home/conan/Desktop/backups/estoque/` e mantém só as 7 mais recentes.

**Seams:**
- Rotina diária

**Blocked by:** 06: Avisos de validade no Telegram

Status: ready-for-agent

- [ ] Cópia é consistente mesmo com o serviço em uso e pode ser aberta como banco válido
- [ ] Há no máximo uma cópia por dia, mesmo com várias execuções no dia
- [ ] Só as 7 cópias mais recentes ficam na pasta
- [ ] Retenção não apaga arquivos que não sejam cópias geradas pela rotina
- [ ] Backup roda mesmo se o envio ao Telegram falhar
- [ ] Pasta de destino é criada se não existir
