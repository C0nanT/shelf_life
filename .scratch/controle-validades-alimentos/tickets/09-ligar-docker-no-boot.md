# 09: Ligar o Docker ao iniciar o PC

> **Difficulty:** Light: **suggested model:** Haiku (Claude Code) / claude-4.5-haiku-thinking (Cursor). Suggestion only, use whatever model you have to hand.

> **Gate:** human: rodar, com sudo, o comando abaixo no PC para o Docker iniciar junto com o sistema

**Spec:** ../SPEC.md

**What to build:** Hoje o Docker só inicia quando algo acessa o socket dele. Por isso, depois de ligar o PC, os containers com `restart: unless-stopped` só voltam se alguém usar o Docker antes. Isso afeta os alertas do `homelab-monitoring` e os avisos deste projeto. Com o serviço habilitado no boot, tudo volta sozinho.

Estado encontrado em 2026-11-08: `docker.service` e `containerd.service` desabilitados, `docker.socket` habilitado. Os containers do `homelab-monitoring` já têm `restart: unless-stopped`.

```bash
sudo systemctl enable --now containerd.service docker.service
```

**Seams:** None

**Blocked by:** None (can start immediately)

Status: done

- [x] `systemctl is-enabled docker.service` responde `enabled`
- [x] `systemctl is-enabled containerd.service` responde `enabled`
