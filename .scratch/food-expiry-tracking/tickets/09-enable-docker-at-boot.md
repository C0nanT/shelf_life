# 09: Start Docker when the PC boots

> **Difficulty:** Light: **suggested model:** Haiku (Claude Code) / claude-4.5-haiku-thinking (Cursor). Suggestion only, use whatever model you have to hand.

> **Gate:** human: run the command below with sudo on the PC so that Docker starts with the system

**Spec:** ../SPEC.md

**What to build:** Docker used to start only when something accessed its socket. Because of that, after the PC started, containers with `restart: unless-stopped` only came back if someone used Docker first. This affected `homelab-monitoring` alerts and this project's warnings. With the service enabled at boot, everything comes back on its own.

State found on 2026-11-08: `docker.service` and `containerd.service` disabled, `docker.socket` enabled. The `homelab-monitoring` containers already have `restart: unless-stopped`.

```bash
sudo systemctl enable --now containerd.service docker.service
```

**Seams:** None

**Blocked by:** None (can start immediately)

Status: done

- [x] `systemctl is-enabled docker.service` returns `enabled`
- [x] `systemctl is-enabled containerd.service` returns `enabled`
