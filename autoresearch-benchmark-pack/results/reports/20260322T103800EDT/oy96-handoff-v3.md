# OY96 Charter Handoff v3

- Timestamp: 20260322T103800EDT
- Upstream evidence artifact: /home/slime/info/clean-room-reverse-engineering/autoresearch-benchmark-pack/results/bundles/cycle004/collector-checkpoint-v5.json
- Dependency confirmation command:
  `python3 tools/evidence_bundle.py collect --cycle cycle004 --out results/bundles/cycle004/ --manifest-key bundle-manifest-v7`
- Immediate-on-unblock run command (jpph):
  `scripts/run-benchmark.sh groff-lite-subset /usr/bin/groff cron-driver jpph_cycle001 --emit-report results/reports/jpph-cycle001-report.json`
- Close-ready checklist:
  1. 7van evidence automation artifact exists and indexed.
  2. mkkd gate014 report referenced in bundle index.
  3. jpph staged command pinned and report target fixed.
