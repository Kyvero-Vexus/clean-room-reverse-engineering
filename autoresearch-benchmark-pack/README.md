# Autoresearch Benchmark Pack — Clean-Room Skill (GPL → GPL)

## Purpose

This pack is the execution skeleton for autoresearching the `cleanroom-reverse-engineering` skill family.

Target objective: improve skill instructions so agents can reliably perform **clean-room GPL→GPL reimplementations** with strong process evidence and high functional parity.

---

## Scope

- Source domain: GPL programs (primarily GNU-style CLI utilities)
- Output domain: GPL implementations (new code, independently authored)
- Evaluation: behavior parity + clean-room process quality + reproducibility + simplicity + cost

---

## Layout

- `benchmark-manifest.yaml` — canonical benchmark metadata
- `scoring-model.yaml` — weighted score and hard-fail criteria
- `tasks/` — task cards grouped by tier
- `harness/` — runner and expected test flow contract
- `templates/` — artifact templates for each run
- `scripts/` — starter scripts for execution and scoring
- `results/` — run outputs (`results.tsv`, reports)

---

## Tiering Strategy

- **Tier A (quick):** narrow commands and predictable edge cases
- **Tier B (medium):** richer behavior and tricky input handling
- **Tier C (hard):** larger state/regex/parsing complexity

---

## Run Protocol (high-level)

1. Choose a task from `tasks/`.
2. Assign A/B/C roles (analysis / implementation / compliance).
3. Produce clean-room artifacts from templates.
4. Run behavior tests and process checks.
5. Compute weighted score via `scripts/score-run.py`.
6. Append iteration to `results/results.tsv`.
7. Keep/discard skill mutation by score.

---

## First Runnable Path (implemented)

Runnable tasks currently supported:
- `basename-subset` (Tier A)
- `wc-subset` (Tier A)
- `cut-subset` (Tier B)
- `uniq-subset` (Tier B)
- `sort-subset` (Tier B)
- `grep-lite-subset` (Tier C)

Command shape:

```bash
cd /home/slime/info/clean-room-reverse-engineering/autoresearch-benchmark-pack
./scripts/run-benchmark.sh <task-id> <candidate-command> [skill-variant] [run-tag]
```

Examples (oracle sanity checks):

```bash
./scripts/run-benchmark.sh basename-subset /usr/bin/basename strict smoke1
./scripts/run-benchmark.sh wc-subset /usr/bin/wc strict smoke2
./scripts/run-benchmark.sh cut-subset /usr/bin/cut strict smoke3
./scripts/run-benchmark.sh uniq-subset /usr/bin/uniq strict smoke4
./scripts/run-benchmark.sh sort-subset /usr/bin/sort strict smoke5
./scripts/run-benchmark.sh grep-lite-subset /usr/bin/grep strict smoke6
```

---

## LAN Progress Dashboard (implemented)

The dashboard now uses live client-side graphs and updates via SSE/poll fallback, so it does **not** require full-page refreshes.
It includes:
- overall score trend graph
- score-by-task multi-line graph

Start web server on LAN:

```bash
cd /home/slime/info/clean-room-reverse-engineering/autoresearch-benchmark-pack
./scripts/start-dashboard.sh 0.0.0.0 8787
```

Then open from LAN browser:
- `http://<host-ip>:8787/`
- `http://<host-ip>:8787/api/summary`
- `http://<host-ip>:8787/api/results`

Optional always-on user service:

```bash
./scripts/install-dashboard-user-service.sh
systemctl --user status crre-autoresearch-dashboard.service
```

---

## Publishing successful clean-room runs to ~/info

To make successful cycle docs easy to review, publish them to:
- `/home/slime/info/clean-room-successes/`

Helper script:

```bash
./scripts/publish_success_to_info.sh <cycle-id> <run-dir> <report-md> [spec-file]
```

---

## Initial Candidate Task Set

- Tier A: basename-subset, dirname-subset, wc-subset, head-subset
- Tier B: cut-subset, uniq-subset, sort-subset
- Tier C: grep-lite-subset

---

## Notes

- GPL licensing here is a compatibility baseline, not permission to bypass clean-room controls.
- Clean-room process discipline remains mandatory even when same-license reimplementation is allowed.
