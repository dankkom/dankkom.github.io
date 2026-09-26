---
name: devlog-quantilica
description: Escrever e publicar a edição mensal do Diário de Desenvolvimento Quantilica no blog Hugo dkko.me. Use ao redigir, revisar ou publicar qualquer post da série Devlog Quantilica.
---

# Devlog Quantilica — Skill de Publicação Mensal

Série mensal em PT-BR, posts longos (1500+ palavras), convenção de pasta
`content/posts/YYYYMMDD-devlog-quantilica-NN-slug-curto/index.md`.
Pilar evergreen: `content/posts/20260925-o-que-e-quantilica/index.md`.

## Passo 1 — Apurar só de fontes públicas

Permitido: `docs.quantilica.com`, GitHub Releases públicas, pacotes no
PyPI/índice Quantilica, o próprio blog.

**Proibido citar, linkar ou descrever:** `planning/`, `knowledge/`,
`infra/` (scripts, crons, logs, `runs.csv`), VPS/servidores, horários de
sincronização, apps privados (versões, codenames de sub-apps, stack,
deploy, healthchecks), processos internos (ADRs, gates, skills, pilots),
contagens internas (nº de planos, notas, fatos), arquivos `.env`/credenciais.

Regra prática: se a informação só existe dentro de um repositório privado,
ela não entra no post — mesmo que seja verdadeira.

## Passo 2 — Escrever no archetype

Criar a pasta do mês a partir de `archetypes/devlog.md`:

```bash
hugo new --kind devlog posts/YYYYMMDD-devlog-quantilica-NN-slug-curto/index.md
```

Estrutura obrigatória: `O que mudou` (releases públicos com versões) ·
`O que aprendi` (decisões e trade-offs, sem jargão interno) ·
`Próximo mês` (gancho). Terminar atualizando a seção `Nesta série`
neste post (a lista cresce a cada edição).

Todo devlog linka o pilar na abertura:
`[O que é a Quantilica](/posts/o-que-e-quantilica)`.

## Passo 3 — Self-review de vazamento

Antes do build, rodar contra o arquivo novo (adicionar termos se surgirem
novos codenames internos):

```bash
grep -rniE '\b(planning|knowledge|VPS|crontab|cron|runs\.csv|AGENTS|bootstrap|doctor|systemd|gunicorn|venv|Flamingo|Alpaca|Fish|Hedgehog|Sloth|deploy\.sh|APP_VERSION|Telegram|Umami|fetch\.toml|manifest\.toml|Cloudflare|WASM|workspace)\b' content/posts/<pasta-nova>/index.md || echo LIMPO
```

Qualquer match precisa ser reescrito em termos públicos ou removido.
Atenção a falsos positivos (`cron` em "sincronizadas") — julgar cada linha.

## Passo 4 — Build

```bash
hugo --gc --minify
```

Armadilha conhecida: `date` no futuro (fuso UTC) faz o Hugo **excluir** o
post do build sem erro. Se a pasta não aparecer em `public/posts/`,
rebuildar com `--buildFuture` para confirmar o diagnóstico e então corrigir
a data para um horário já passado (ex. `09:00:00-03:00`).

## Passo 5 — Commit seletivo + push

O repo costuma ter posts untracked alheios. **Nunca `git add -A`.**

```bash
git add content/posts/<pasta-nova>/
git commit -m "feat: Devlog Quantilica #NN — <tema do mês>"
git push origin main
```

O deploy é automático via `.github/workflows/hugo.yaml` (Pages).
Confirmar com `gh run list --limit 1` e a URL final
`https://dkko.me/posts/<slug>`.
