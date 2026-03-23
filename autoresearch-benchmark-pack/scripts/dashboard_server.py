#!/usr/bin/env python3
"""LAN dashboard server for CRRE autoresearch benchmark progress.

Features:
- JSON APIs: /api/results, /api/summary
- Live stream API: /api/stream (Server-Sent Events)
- Single-page dashboard with live-updating graph (no full page refresh)
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


KNOWN_BENCH_TASKS = [
    "basename-subset",
    "dirname-subset",
    "wc-subset",
    "head-subset",
    "cut-subset",
    "uniq-subset",
    "sort-subset",
    "grep-lite-subset",
    "chain-progress",
]

BEAD_ID_RE = re.compile(r"^workspace-ceo_chryso-[a-z0-9.]+$")


def _infer_task_from_description(desc: str) -> str | None:
    d = (desc or "").lower()
    for task in KNOWN_BENCH_TASKS:
        if task in d:
            return task
    if "chain progress" in d or "no cycle benchmark executed" in d:
        return "chain-progress"

    # Try run_dir extraction: ...run_dir=YYYY...-sort-subset-...
    m = re.search(r"run_dir=[^\s]*-(basename-subset|dirname-subset|wc-subset|head-subset|cut-subset|uniq-subset|sort-subset|grep-lite-subset)-", d)
    if m:
        return m.group(1)
    return None


def _normalize_row(row: dict[str, str]) -> dict[str, str]:
    out = dict(row)
    task_id = (out.get("task_id") or "").strip()
    if not task_id:
        out["task_id"] = "unknown"
        return out

    # Guard against cron telemetry accidentally writing bead IDs as task IDs.
    if BEAD_ID_RE.match(task_id):
        inferred = _infer_task_from_description(out.get("description") or "")
        if inferred:
            out["task_id_raw"] = task_id
            out["task_id"] = inferred
        else:
            # Keep chart sane even when inference fails.
            out["task_id_raw"] = task_id
            out["task_id"] = "chain-progress"
    return out


def load_results(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        return [_normalize_row(dict(r)) for r in reader]


def to_float(v: str | None) -> float:
    try:
        return float(v or 0.0)
    except Exception:
        return 0.0


def summarize(rows: list[dict[str, str]]) -> dict[str, Any]:
    if not rows:
        return {
            "total_runs": 0,
            "best_score": None,
            "best_iter": None,
            "latest": None,
            "status_counts": {},
        }

    best = max(rows, key=lambda r: to_float(r.get("score")))
    latest = rows[-1]
    counts: dict[str, int] = {}
    for r in rows:
        s = (r.get("status") or "unknown").strip()
        counts[s] = counts.get(s, 0) + 1

    return {
        "total_runs": len(rows),
        "best_score": to_float(best.get("score")),
        "best_iter": best.get("iter"),
        "best_task": best.get("task_id"),
        "latest": latest,
        "status_counts": counts,
    }


def make_handler(results_path: Path):
    class Handler(BaseHTTPRequestHandler):
        def _send_json(self, payload: Any, code: int = 200) -> None:
            body = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_html(self, body: str, code: int = 200) -> None:
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _send_sse(self, event: str, payload: Any) -> None:
            msg = f"event: {event}\ndata: {json.dumps(payload)}\n\n".encode("utf-8")
            self.wfile.write(msg)
            self.wfile.flush()

        def _dashboard_html(self) -> str:
            return """
<!doctype html>
<html>
<head>
  <meta charset='utf-8'/>
  <title>CRRE Autoresearch Dashboard</title>
  <style>
    :root {
      --bg: #111;
      --panel: #1b1b1b;
      --line: #333;
      --text: #ddd;
      --muted: #aaa;
      --accent: #8ec7ff;
      --ok: #62d26f;
      --warn: #ffca3a;
      --bad: #ff6b6b;
    }
    body { font-family: system-ui, sans-serif; margin: 20px; background: var(--bg); color: var(--text); }
    h1 { margin: 0 0 12px 0; }
    .row { display: grid; grid-template-columns: repeat(4, minmax(140px, 1fr)); gap: 10px; margin-bottom: 14px; }
    .card { background: var(--panel); border: 1px solid var(--line); padding: 10px; border-radius: 8px; }
    .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .05em; }
    .value { font-size: 22px; margin-top: 4px; }
    .panel { background: var(--panel); border: 1px solid var(--line); padding: 10px; border-radius: 8px; margin-bottom: 14px; }
    .sub { color: var(--muted); font-size: 12px; margin-bottom: 8px; }
    svg { width: 100%; height: 240px; display: block; background: #121212; border: 1px solid #2a2a2a; border-radius: 6px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #444; padding: 6px; font-size: 13px; }
    th { background: #222; text-align: left; }
    .status-ok { color: var(--ok); }
    .status-failed, .status-error { color: var(--bad); }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 999px; background: #222; border: 1px solid #444; font-size: 12px; }
    .footer { color: var(--muted); font-size: 12px; margin-top: 10px; }
    a { color: var(--accent); }
  </style>
</head>
<body>
  <h1>CRRE Autoresearch Progress (LAN)</h1>

  <div class="row">
    <div class="card"><div class="label">Total Runs</div><div id="totalRuns" class="value">0</div></div>
    <div class="card"><div class="label">Best Score</div><div id="bestScore" class="value">-</div></div>
    <div class="card"><div class="label">Best Task</div><div id="bestTask" class="value" style="font-size:16px">-</div></div>
    <div class="card"><div class="label">Latest Status</div><div id="latestStatus" class="value" style="font-size:16px">-</div></div>
  </div>

  <div class="panel">
    <div class="sub">Score Trend (iteration → score)</div>
    <svg id="scoreChart" viewBox="0 0 1000 240" preserveAspectRatio="none"></svg>
  </div>

  <div class="panel">
    <div class="sub">Score by Task (multi-line trend)</div>
    <svg id="taskScoreChart" viewBox="0 0 1000 240" preserveAspectRatio="none"></svg>
  </div>

  <div class="panel">
    <div class="sub">Latest Runs</div>
    <table>
      <thead><tr><th>iter</th><th>task</th><th>variant</th><th>score</th><th>status</th><th>description</th></tr></thead>
      <tbody id="runsBody"></tbody>
    </table>
  </div>

  <div class="footer">
    APIs: <a href="/api/summary">/api/summary</a> | <a href="/api/results">/api/results</a> |
    Stream: <a href="/api/stream">/api/stream</a>
  </div>

<script>
(() => {
  const totalRunsEl = document.getElementById('totalRuns');
  const bestScoreEl = document.getElementById('bestScore');
  const bestTaskEl = document.getElementById('bestTask');
  const latestStatusEl = document.getElementById('latestStatus');
  const runsBody = document.getElementById('runsBody');
  const chart = document.getElementById('scoreChart');
  const taskChart = document.getElementById('taskScoreChart');

  function esc(s) {
    return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  function num(v) {
    const n = Number(v);
    return Number.isFinite(n) ? n : 0;
  }

  function statusClass(s) {
    const x = String(s || '').toLowerCase();
    if (x === 'ok' || x === 'completed') return 'status-ok';
    if (x === 'failed' || x === 'error' || x === 'hard-fail') return 'status-failed';
    return '';
  }

  function renderTable(rows) {
    const view = rows.slice(-100).reverse();
    runsBody.innerHTML = view.map(r => `
      <tr>
        <td>${esc(r.iter)}</td>
        <td>${esc(r.task_id)}</td>
        <td>${esc(r.skill_variant)}</td>
        <td>${esc(r.score)}</td>
        <td class="${statusClass(r.status)}">${esc(r.status)}</td>
        <td>${esc(r.description)}</td>
      </tr>
    `).join('');
  }

  function renderChart(rows) {
    const pts = rows
      .map(r => ({ x: num(r.iter), y: num(r.score), status: String(r.status || '').toLowerCase() }))
      .filter(p => Number.isFinite(p.x) && Number.isFinite(p.y));

    if (!pts.length) {
      chart.innerHTML = '<text x="20" y="30" fill="#aaa" font-size="14">No data yet</text>';
      return;
    }

    const minX = Math.min(...pts.map(p => p.x));
    const maxX = Math.max(...pts.map(p => p.x));
    const minY = 0;
    const maxY = 100;

    const left = 42, right = 20, top = 14, bottom = 26;
    const W = 1000, H = 240;
    const CW = W - left - right;
    const CH = H - top - bottom;

    const sx = x => left + ((x - minX) / Math.max(1, (maxX - minX))) * CW;
    const sy = y => top + (1 - ((y - minY) / Math.max(1, (maxY - minY)))) * CH;

    const poly = pts.map(p => `${sx(p.x)},${sy(p.y)}`).join(' ');

    const yTicks = [0, 25, 50, 75, 100];
    const yGrid = yTicks.map(v => {
      const y = sy(v);
      return `<line x1="${left}" y1="${y}" x2="${W-right}" y2="${y}" stroke="#2c2c2c" stroke-width="1" />\n`
        + `<text x="6" y="${y+4}" fill="#888" font-size="11">${v}</text>`;
    }).join('');

    const circles = pts.map(p => {
      const c = p.status === 'ok' ? '#62d26f' : (p.status.includes('fail') || p.status === 'error' ? '#ff6b6b' : '#8ec7ff');
      return `<circle cx="${sx(p.x)}" cy="${sy(p.y)}" r="3.5" fill="${c}" />`;
    }).join('');

    chart.innerHTML = `
      ${yGrid}
      <line x1="${left}" y1="${H-bottom}" x2="${W-right}" y2="${H-bottom}" stroke="#555" stroke-width="1.2" />
      <line x1="${left}" y1="${top}" x2="${left}" y2="${H-bottom}" stroke="#555" stroke-width="1.2" />
      <polyline fill="none" stroke="#8ec7ff" stroke-width="2" points="${poly}" />
      ${circles}
      <text x="${W-110}" y="${H-6}" fill="#888" font-size="11">iteration</text>
      <text x="8" y="12" fill="#888" font-size="11">score</text>
    `;
  }

  function renderTaskChart(rows) {
    const pts = rows
      .map(r => ({ x: num(r.iter), y: num(r.score), task: String(r.task_id || 'unknown') }))
      .filter(p => Number.isFinite(p.x) && Number.isFinite(p.y));

    if (!pts.length) {
      taskChart.innerHTML = '<text x="20" y="30" fill="#aaa" font-size="14">No data yet</text>';
      return;
    }

    const minX = Math.min(...pts.map(p => p.x));
    const maxX = Math.max(...pts.map(p => p.x));
    const minY = 0;
    const maxY = 100;

    const left = 42, right = 20, top = 14, bottom = 26;
    const W = 1000, H = 240;
    const CW = W - left - right;
    const CH = H - top - bottom;

    const sx = x => left + ((x - minX) / Math.max(1, (maxX - minX))) * CW;
    const sy = y => top + (1 - ((y - minY) / Math.max(1, (maxY - minY)))) * CH;

    const yTicks = [0, 25, 50, 75, 100];
    const yGrid = yTicks.map(v => {
      const y = sy(v);
      return `<line x1="${left}" y1="${y}" x2="${W-right}" y2="${y}" stroke="#2c2c2c" stroke-width="1" />\n`
        + `<text x="6" y="${y+4}" fill="#888" font-size="11">${v}</text>`;
    }).join('');

    const palette = ['#8ec7ff', '#62d26f', '#ffca3a', '#ff8fab', '#b794f4', '#4fd1c5', '#f6ad55'];
    const byTask = {};
    for (const p of pts) {
      if (!byTask[p.task]) byTask[p.task] = [];
      byTask[p.task].push(p);
    }

    const tasks = Object.keys(byTask).sort();
    const lines = tasks.map((t, i) => {
      const color = palette[i % palette.length];
      const linePts = byTask[t].sort((a,b) => a.x - b.x).map(p => `${sx(p.x)},${sy(p.y)}`).join(' ');
      return `<polyline fill="none" stroke="${color}" stroke-width="2" points="${linePts}" />`;
    }).join('');

    const dots = tasks.map((t, i) => {
      const color = palette[i % palette.length];
      return byTask[t].map(p => `<circle cx="${sx(p.x)}" cy="${sy(p.y)}" r="2.8" fill="${color}" />`).join('');
    }).join('');

    const legend = tasks.slice(0, 8).map((t, i) => {
      const color = palette[i % palette.length];
      const x = 70 + (i % 4) * 220;
      const y = 18 + Math.floor(i / 4) * 14;
      return `<rect x="${x}" y="${y-8}" width="10" height="10" fill="${color}" />`
        + `<text x="${x+14}" y="${y}" fill="#aaa" font-size="11">${t}</text>`;
    }).join('');

    taskChart.innerHTML = `
      ${yGrid}
      <line x1="${left}" y1="${H-bottom}" x2="${W-right}" y2="${H-bottom}" stroke="#555" stroke-width="1.2" />
      <line x1="${left}" y1="${top}" x2="${left}" y2="${H-bottom}" stroke="#555" stroke-width="1.2" />
      ${lines}
      ${dots}
      ${legend}
      <text x="${W-110}" y="${H-6}" fill="#888" font-size="11">iteration</text>
      <text x="8" y="12" fill="#888" font-size="11">score</text>
    `;
  }

  function render(payload) {
    const rows = payload.results || [];
    const s = payload.summary || {};

    totalRunsEl.textContent = String(s.total_runs ?? rows.length ?? 0);
    bestScoreEl.textContent = s.best_score == null ? '-' : String(s.best_score);
    bestTaskEl.textContent = s.best_task || '-';

    const latest = s.latest || rows[rows.length - 1] || {};
    latestStatusEl.innerHTML = `<span class="badge ${statusClass(latest.status)}">${esc(latest.status || '-')}</span>`;

    renderChart(rows);
    renderTaskChart(rows);
    renderTable(rows);
  }

  async function pullOnce() {
    try {
      const [summaryRes, resultsRes] = await Promise.all([
        fetch('/api/summary', { cache: 'no-store' }),
        fetch('/api/results', { cache: 'no-store' }),
      ]);
      const summary = await summaryRes.json();
      const results = await resultsRes.json();
      render({ summary, results });
    } catch (e) {
      // silent retry by timer
    }
  }

  // Prefer SSE for live push; fallback to polling.
  let polling = null;
  try {
    const es = new EventSource('/api/stream');
    es.addEventListener('snapshot', ev => {
      try { render(JSON.parse(ev.data)); } catch (_) {}
    });
    es.onerror = () => {
      es.close();
      if (!polling) {
        pullOnce();
        polling = setInterval(pullOnce, 3000);
      }
    };
  } catch (_) {
    pullOnce();
    polling = setInterval(pullOnce, 3000);
  }

  pullOnce();
})();
</script>
</body>
</html>
"""

        def do_GET(self):  # noqa: N802
            if self.path in ("/api/results", "/api/results/"):
                rows = load_results(results_path)
                return self._send_json(rows)

            if self.path in ("/api/summary", "/api/summary/"):
                rows = load_results(results_path)
                return self._send_json(summarize(rows))

            if self.path in ("/api/stream", "/api/stream/"):
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.send_header("X-Accel-Buffering", "no")
                self.end_headers()

                try:
                    while True:
                        rows = load_results(results_path)
                        payload = {
                            "summary": summarize(rows),
                            "results": rows[-300:],
                        }
                        self._send_sse("snapshot", payload)
                        time.sleep(2)
                except (BrokenPipeError, ConnectionResetError):
                    return

            if self.path in ("/", ""):
                return self._send_html(self._dashboard_html())

            self._send_json({"error": "not found"}, code=404)

        def log_message(self, fmt: str, *args):  # silence noisy logging
            return

    return Handler


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument(
        "--results",
        default=str(Path(__file__).resolve().parents[1] / "results" / "results.tsv"),
    )
    args = ap.parse_args()

    results_path = Path(args.results)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(results_path))
    print(f"Dashboard listening on http://{args.host}:{args.port}")
    print(f"Reading results from: {results_path}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
