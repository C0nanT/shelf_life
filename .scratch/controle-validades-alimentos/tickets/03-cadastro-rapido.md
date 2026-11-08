# 03: Cadastro rápido

> **Difficulty:** Standard: **suggested model:** Sonnet (Claude Code) / Sonnet (Cursor). Suggestion only, use whatever model you have to hand.

**Spec:** ../SPEC.md

**What to build:** Digitar todo o estoque atual sem atrito. O nome autocompleta com alimentos já existentes, a medida vem preenchida e o botão "salvar e adicionar outro" mantém o formulário aberto para a próxima compra.

**Seams:**
- Página/API

**Blocked by:** 01: Registrar compra e ver na lista

Status: ready-for-agent

- [ ] Digitar parte do nome sugere alimentos já existentes
- [ ] Escolher um alimento existente preenche a medida dele
- [ ] "Salvar e adicionar outro" registra a compra e deixa o formulário pronto para a próxima
- [ ] Além de nome, quantidade, medida e grupo, nenhum campo é obrigatório
