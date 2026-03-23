#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

RUBRIC = {
    "version": "v1",
    "target": "groff-lite-subset",
    "method": "behavior-first",
    "criteria": [
        {
            "id": "parsing_fidelity",
            "weight": 30,
            "description": "Request/control-line recognition and escape handling for scoped subset.",
            "fixture_ids": ["groff-token-001", "groff-escape-001"],
        },
        {
            "id": "macro_semantics",
            "weight": 20,
            "description": "Deterministic .de/.am expansion behavior on fixture corpus.",
            "fixture_ids": ["groff-macro-001"],
        },
        {
            "id": "register_string_state",
            "weight": 15,
            "description": "Observable parity for .nr/.ds state transitions.",
            "fixture_ids": ["groff-state-001"],
        },
        {
            "id": "flow_formatting",
            "weight": 15,
            "description": "Fill/no-fill and line-break behavior against expected text output.",
            "fixture_ids": ["groff-flow-001"],
        },
        {
            "id": "traceability_legality",
            "weight": 20,
            "description": "Fixture provenance, contamination controls, and reproducible run records.",
            "fixture_ids": ["groff-trace-001"],
        },
    ],
    "acceptance_gates": [
        "Serialize rubric JSON under results/reports/",
        "Write bounded scope markdown under results/reports/",
        "Map each included feature to >=1 fixture id",
        "Include contamination-control checklist in scope report",
    ],
}

SCOPE_MD = """# Groff-lite Bounded Scope (rire v1)\n\n## Include\n- Tokenization and request/control-line parsing\n- Escape sequence handling required by scoped fixtures\n- Macro subset: `.de`, `.am`\n- Register/string subset: `.nr`, `.ds`\n- Text flow behavior: fill/no-fill and line breaks for plaintext output backend\n\n## Exclude\n- Full troff device model\n- PostScript/PDF/binary device backends\n- Vendor-specific macro ecosystems outside scoped fixture corpus\n\n## Feature → Fixture Mapping\n- Tokenization + request lines → `groff-token-001`\n- Escape handling → `groff-escape-001`\n- `.de/.am` macro expansion → `groff-macro-001`\n- `.nr/.ds` state behavior → `groff-state-001`\n- Flow formatting → `groff-flow-001`\n\n## Contamination-Control Checklist\n- [x] Behavior-first scope defined without copying implementation code\n- [x] Required outputs are artifacted under `results/reports/`\n- [x] Acceptance gates stated explicitly\n- [x] Scope limits recorded (include/exclude) to avoid hidden expansion\n"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Define groff-lite rubric and bounded scope artifacts")
    parser.add_argument("--rubric", required=True, help="Path for rubric JSON output")
    parser.add_argument("--scope", required=True, help="Path for scope markdown output")
    args = parser.parse_args()

    rubric_path = Path(args.rubric)
    scope_path = Path(args.scope)
    rubric_path.parent.mkdir(parents=True, exist_ok=True)
    scope_path.parent.mkdir(parents=True, exist_ok=True)

    rubric_path.write_text(json.dumps(RUBRIC, indent=2) + "\n", encoding="utf-8")
    scope_path.write_text(SCOPE_MD, encoding="utf-8")
    print(f"wrote {rubric_path}")
    print(f"wrote {scope_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
