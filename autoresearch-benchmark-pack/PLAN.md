# Execution Plan — CRRE Skill Autoresearch (GPL → GPL)

## Objective

Autoresearch the clean-room skill family to improve:
1. behavioral parity,
2. contamination-safe process quality,
3. reproducible delivery,
4. operational visibility.

## Constraint

Benchmark tasks use **GPL program behavior as source target** and produce **new GPL implementations** under clean-room process controls.

---

## Phase 1 (completed): benchmark scaffold

- Manifest + scoring model
- Tiered task cards (A/B/C)
- Baseline templates + starter scripts

---

## Phase 2 (completed): runnable harness for Tier A + Tier B baseline

Implemented executable path for:
- `basename-subset`
- `wc-subset`
- `cut-subset`
- `uniq-subset`

Outputs per run:
- test report JSON
- checklist report JSON
- score report JSON
- iteration report markdown
- row append to `results/results.tsv`

---

## Phase 3: autoresearch loop

- Baseline run with current clean-room skill
- One mutation dimension per iteration
- Keep/discard by score delta
- Checkpoint evaluation every 5 iterations

---

## Phase 4: LAN progress server (requested)

Run a local dashboard web server bound to LAN:
- default bind: `0.0.0.0`
- default port: `8787`

Required views:
1. `GET /` HTML dashboard with auto-refresh
2. `GET /api/results` JSON rows from `results.tsv`
3. `GET /api/summary` best score, latest iteration, status counts

Operational goal:
- user can monitor ongoing benchmark/autoresearch progress from another machine on LAN in real time.

---

## Phase 5: hardening

- Add auth/network controls if needed
- Add per-task drill-down pages
- Add checkpoint snapshots and exportable reports

---

## Success criteria

- Harness runs Tier A/B tasks end-to-end without manual patching.
- Dashboard displays live updates from result ledger.
- Optional user-level systemd service keeps dashboard persistent across sessions.
- At least one full keep/discard loop executes with auditable artifacts.
