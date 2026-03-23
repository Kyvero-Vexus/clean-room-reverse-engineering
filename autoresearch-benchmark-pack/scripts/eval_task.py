#!/usr/bin/env python3
"""Evaluate candidate command parity for CRRE benchmark tasks.

Supported tasks:
- basename-subset
- wc-subset
- cut-subset
- uniq-subset
- sort-subset
- grep-lite-subset
- grep-core-regex-flags
- grep-file-context
- roff-tokenizer-parser-subset
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class CaseResult:
    name: str
    passed: bool
    expected: str
    actual: str
    detail: str = ""


def run_cmd(cmd: List[str], stdin_text: str | None = None) -> tuple[int, str, str]:
    p = subprocess.run(
        cmd,
        input=stdin_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return p.returncode, p.stdout, p.stderr


def normalize_ws(s: str) -> str:
    return "\n".join(line.rstrip() for line in s.strip().splitlines()).strip()


def ints_from_output(s: str) -> List[int]:
    return [int(x) for x in re.findall(r"\d+", s)]


def mk_case_result(
    name: str,
    rc_expected: int,
    out_expected: str,
    err_expected: str,
    rc_actual: int,
    out_actual: str,
    err_actual: str,
    numeric_only: bool = False,
) -> CaseResult:
    if numeric_only:
        expected_norm = " ".join(map(str, ints_from_output(out_expected)))
        actual_norm = " ".join(map(str, ints_from_output(out_actual)))
    else:
        expected_norm = normalize_ws(out_expected)
        actual_norm = normalize_ws(out_actual)

    passed = rc_expected == rc_actual and expected_norm == actual_norm
    detail = ""
    if not passed:
        detail = (
            f"oracle_rc={rc_expected} cand_rc={rc_actual} "
            f"oracle_err={err_expected.strip()} cand_err={err_actual.strip()}"
        )

    return CaseResult(
        name=name,
        passed=passed,
        expected=expected_norm,
        actual=actual_norm,
        detail=detail,
    )


def eval_basename(candidate: str) -> List[CaseResult]:
    cases = [
        ("simple", ["hello.txt"]),
        ("nested", ["/tmp/a/b/c.log"]),
        ("trailing-slash", ["/usr/local/bin/"]),
        ("root", ["/"]),
        ("dot", ["."]),
    ]

    out: List[CaseResult] = []
    for name, args in cases:
        rc_e, exp, err_e = run_cmd(["basename", *args])
        rc_a, act, err_a = run_cmd([candidate, *args])
        out.append(mk_case_result(name, rc_e, exp, err_e, rc_a, act, err_a))
    return out


def eval_wc(candidate: str) -> List[CaseResult]:
    samples = [
        ("empty", ""),
        ("single-line", "hello world\n"),
        ("two-lines", "alpha beta\ngamma\n"),
        ("spaces", "  a   b c\n\n"),
    ]

    flags_cases = [
        ("l", ["-l"]),
        ("w", ["-w"]),
        ("c", ["-c"]),
        ("default", []),
    ]

    out: List[CaseResult] = []
    for sample_name, sample in samples:
        for flag_name, flags in flags_cases:
            name = f"{sample_name}:{flag_name}"
            rc_e, exp, err_e = run_cmd(["wc", *flags], stdin_text=sample)
            rc_a, act, err_a = run_cmd([candidate, *flags], stdin_text=sample)
            out.append(mk_case_result(name, rc_e, exp, err_e, rc_a, act, err_a, numeric_only=True))
    return out


def eval_cut(candidate: str) -> List[CaseResult]:
    cases = [
        (
            "csv-field-2",
            ["-d", ",", "-f", "2"],
            "a,b,c\nx,y,z\n",
        ),
        (
            "colon-fields-1-3",
            ["-d", ":", "-f", "1,3"],
            "aa:bb:cc\n11:22:33\n",
        ),
        (
            "pipe-range-2-4",
            ["-d", "|", "-f", "2-4"],
            "p|q|r|s|t\n1|2|3|4|5\n",
        ),
        (
            "suppress-no-delim",
            ["-d", ",", "-f", "2", "-s"],
            "nodelemline\na,b\n",
        ),
    ]

    out: List[CaseResult] = []
    for name, args, sample in cases:
        rc_e, exp, err_e = run_cmd(["cut", *args], stdin_text=sample)
        rc_a, act, err_a = run_cmd([candidate, *args], stdin_text=sample)
        out.append(mk_case_result(name, rc_e, exp, err_e, rc_a, act, err_a))
    return out


def eval_uniq(candidate: str) -> List[CaseResult]:
    sample = "a\na\na\nb\nb\nc\na\na\n"
    cases = [
        ("default", [], sample),
        ("count", ["-c"], sample),
        ("duplicates-only", ["-d"], sample),
        ("unique-only", ["-u"], sample),
    ]

    out: List[CaseResult] = []
    for name, args, stdin_text in cases:
        rc_e, exp, err_e = run_cmd(["uniq", *args], stdin_text=stdin_text)
        rc_a, act, err_a = run_cmd([candidate, *args], stdin_text=stdin_text)
        out.append(mk_case_result(name, rc_e, exp, err_e, rc_a, act, err_a))
    return out


def eval_sort(candidate: str) -> List[CaseResult]:
    cases = [
        (
            "default-lexical",
            [],
            "pear\napple\nbanana\n",
        ),
        (
            "reverse",
            ["-r"],
            "pear\napple\nbanana\n",
        ),
        (
            "numeric",
            ["-n"],
            "10\n2\n1\n",
        ),
        (
            "key-field-2",
            ["-t", ",", "-k", "2,2"],
            "alice,3\nbob,1\ncarol,2\n",
        ),
    ]

    out: List[CaseResult] = []
    for name, args, sample in cases:
        rc_e, exp, err_e = run_cmd(["sort", *args], stdin_text=sample)
        rc_a, act, err_a = run_cmd([candidate, *args], stdin_text=sample)
        out.append(mk_case_result(name, rc_e, exp, err_e, rc_a, act, err_a))
    return out


def eval_grep_lite(candidate: str) -> List[CaseResult]:
    sample = "alpha\nBeta\ngamma\nalpha beta\n"
    cases = [
        ("basic-match", ["alpha"], sample),
        ("ignore-case", ["-i", "beta"], sample),
        ("invert", ["-v", "alpha"], sample),
        ("count", ["-c", "alpha"], sample),
        ("extended-regex", ["-E", "alpha|gamma"], sample),
    ]

    out: List[CaseResult] = []
    for name, args, stdin_text in cases:
        rc_e, exp, err_e = run_cmd(["grep", *args], stdin_text=stdin_text)
        rc_a, act, err_a = run_cmd([candidate, *args], stdin_text=stdin_text)
        out.append(mk_case_result(name, rc_e, exp, err_e, rc_a, act, err_a))
    return out


def eval_grep_core_regex_flags(candidate: str) -> List[CaseResult]:
    sample = "alpha\nBeta\ngamma\nalpha beta\nbeta\nword\nwordplay\n"
    cases = [
        ("extended-regex", ["-E", "alpha|gamma"], sample),
        ("fixed-string", ["-F", "alpha beta"], sample),
        ("ignore-case", ["-i", "beta"], sample),
        ("invert-match", ["-v", "alpha"], sample),
        ("word-regexp", ["-w", "word"], sample),
        ("line-regexp", ["-x", "beta"], sample),
        ("count-ext", ["-c", "-E", "alpha|beta"], sample),
    ]

    out: List[CaseResult] = []
    for name, args, stdin_text in cases:
        rc_e, exp, err_e = run_cmd(["grep", *args], stdin_text=stdin_text)
        rc_a, act, err_a = run_cmd([candidate, *args], stdin_text=stdin_text)
        out.append(mk_case_result(name, rc_e, exp, err_e, rc_a, act, err_a))
    return out


def eval_grep_file_context(candidate: str) -> List[CaseResult]:
    with tempfile.TemporaryDirectory(prefix="grep-file-context-") as td:
        root = Path(td)
        f1 = root / "a.txt"
        f2 = root / "b.txt"
        f1.write_text("alpha\nmatch\ngamma\nmatch2\n", encoding="utf-8")
        f2.write_text("delta\nmatch\nepsilon\n", encoding="utf-8")

        cases = [
            ("multi-file-label", ["-H", "match", str(f1), str(f2)]),
            ("line-numbers", ["-n", "match", str(f1)]),
            ("after-context", ["-A", "1", "match", str(f1)]),
            ("before-context", ["-B", "1", "match", str(f1)]),
            ("around-context", ["-C", "1", "match", str(f1)]),
        ]

        out: List[CaseResult] = []
        for name, args in cases:
            rc_e, exp, err_e = run_cmd(["grep", *args])
            rc_a, act, err_a = run_cmd([candidate, *args])
            out.append(mk_case_result(name, rc_e, exp, err_e, rc_a, act, err_a))
        return out


def eval_roff_tokenizer_parser_subset(candidate: str) -> List[CaseResult]:
    """Evaluate roff tokenizer/parser/interpreter candidate against groff-lite-v1 fixtures."""
    FIXTURES = Path(__file__).parent.parent / "results" / "fixtures" / "groff-lite-v1"
    inputs_dir = FIXTURES / "inputs"
    expected_dir = FIXTURES / "expected"
    out: List[CaseResult] = []

    def run_candidate(mode_flag: str, roff_input: str):
        proc = subprocess.run(
            [candidate, mode_flag],
            input=roff_input,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return proc.returncode, proc.stdout, proc.stderr

    # --- Case 1: tokenizer - groff-token-001 ---
    try:
        roff_src = (inputs_dir / "groff-token-001.roff").read_text()
        expected = json.loads((expected_dir / "groff-token-001.tokens.json").read_text())
        rc, stdout, _ = run_candidate("--tokenize", roff_src)
        passed = False
        if rc == 0:
            tokens = json.loads(stdout)
            # Check that each expected token appears (subset match)
            def token_present(exp_tok, toks):
                for t in toks:
                    if t.get('type') != exp_tok.get('type'):
                        continue
                    if exp_tok.get('name') and t.get('name') != exp_tok.get('name'):
                        continue
                    if exp_tok.get('contains') and exp_tok['contains'] not in t.get('contains', ''):
                        continue
                    if exp_tok.get('args') is not None and t.get('args') != exp_tok.get('args'):
                        continue
                    return True
                return False
            passed = all(token_present(e, tokens) for e in expected.get('expect', []))
        out.append(CaseResult(name="groff-token-001", passed=passed, expected="", actual=""))
    except Exception as exc:
        out.append(CaseResult(name="groff-token-001", passed=False, expected="", actual=""))

    # --- Case 2: tokenizer - groff-escape-001 ---
    try:
        roff_src = (inputs_dir / "groff-escape-001.roff").read_text()
        expected = json.loads((expected_dir / "groff-escape-001.tokens.json").read_text())
        rc, stdout, _ = run_candidate("--tokenize", roff_src)
        passed = False
        if rc == 0:
            tokens = json.loads(stdout)
            def token_present(exp_tok, toks):
                for t in toks:
                    if t.get('type') != exp_tok.get('type'):
                        continue
                    if exp_tok.get('contains') and exp_tok['contains'] not in t.get('contains', ''):
                        continue
                    return True
                return False
            passed = all(token_present(e, tokens) for e in expected.get('expect', []))
        out.append(CaseResult(name="groff-escape-001", passed=passed, expected="", actual=""))
    except Exception:
        out.append(CaseResult(name="groff-escape-001", passed=False, expected="", actual=""))

    # --- Case 3: behavior - groff-macro-001 ---
    try:
        roff_src = (inputs_dir / "groff-macro-001.roff").read_text()
        expected = json.loads((expected_dir / "groff-macro-001.behavior.json").read_text())
        rc, stdout, _ = run_candidate("--behavior", roff_src)
        passed = False
        if rc == 0:
            report = json.loads(stdout)
            exp = expected.get('expect', {})
            macro_name = exp.get('defined_macro', '')
            expanded_contains = exp.get('expanded_contains', [])
            render = report.get('render', '')
            macros = report.get('macros', {})
            macro_ok = macro_name in macros or macro_name in report.get('macros', {})
            render_ok = all(s in render for s in expanded_contains)
            passed = macro_ok and render_ok
        out.append(CaseResult(name="groff-macro-001", passed=passed, expected="", actual=""))
    except Exception:
        out.append(CaseResult(name="groff-macro-001", passed=False, expected="", actual=""))

    # --- Case 4: behavior - groff-flow-001 ---
    try:
        roff_src = (inputs_dir / "groff-flow-001.roff").read_text()
        expected = json.loads((expected_dir / "groff-flow-001.behavior.json").read_text())
        rc, stdout, _ = run_candidate("--behavior", roff_src)
        passed = False
        if rc == 0:
            report = json.loads(stdout)
            exp = expected.get('expect', {})
            render = report.get('render', '')
            nf_text = exp.get('no_fill_preserves', '')
            fill_text = exp.get('fill_mode_has_text', '')
            passed = nf_text in render and fill_text in render
        out.append(CaseResult(name="groff-flow-001", passed=passed, expected="", actual=""))
    except Exception:
        out.append(CaseResult(name="groff-flow-001", passed=False, expected="", actual=""))

    # --- Case 5: state - groff-state-001 ---
    try:
        roff_src = (inputs_dir / "groff-state-001.roff").read_text()
        expected = json.loads((expected_dir / "groff-state-001.behavior.json").read_text())
        rc, stdout, _ = run_candidate("--state", roff_src)
        passed = False
        if rc == 0:
            report = json.loads(stdout)
            exp = expected.get('expect', {})
            regs_ok = all(
                report.get('registers', {}).get(k) == v
                for k, v in exp.get('registers', {}).items()
            )
            strs_ok = all(
                report.get('strings', {}).get(k) == v
                for k, v in exp.get('strings', {}).items()
            )
            render_contains = exp.get('render_contains', '')
            render_ok = render_contains in report.get('render', '')
            passed = regs_ok and strs_ok and render_ok
        out.append(CaseResult(name="groff-state-001", passed=passed, expected="", actual=""))
    except Exception:
        out.append(CaseResult(name="groff-state-001", passed=False, expected="", actual=""))

    return out


def eval_roff_macro_expansion_subset(candidate: str) -> List[CaseResult]:
    """Evaluate roff macro expansion (.de/.am/.ds/.nr) subset against groff-lite-v1 fixtures."""
    FIXTURES = Path(__file__).parent.parent / "results" / "fixtures" / "groff-lite-v1"
    inputs_dir = FIXTURES / "inputs"
    expected_dir = FIXTURES / "expected"
    out: List[CaseResult] = []

    def run_candidate(mode_flag: str, roff_input: str):
        proc = subprocess.run(
            [candidate, mode_flag],
            input=roff_input,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return proc.returncode, proc.stdout, proc.stderr

    # Case 1: .de/.am macro define+append+invoke
    try:
        roff_src = (inputs_dir / "groff-macro-001.roff").read_text()
        expected = json.loads((expected_dir / "groff-macro-001.behavior.json").read_text())
        rc, stdout, _ = run_candidate("--behavior", roff_src)
        passed = False
        if rc == 0:
            report = json.loads(stdout)
            exp = expected.get('expect', {})
            macro_name = exp.get('defined_macro', '')
            expanded_contains = exp.get('expanded_contains', [])
            render = report.get('render', '')
            macro_ok = macro_name in report.get('macros', {})
            render_ok = all(s in render for s in expanded_contains)
            passed = macro_ok and render_ok
        out.append(CaseResult(name="groff-macro-001-define-append", passed=passed, expected=str(expected), actual=stdout[:200]))
    except Exception as exc:
        out.append(CaseResult(name="groff-macro-001-define-append", passed=False, expected="", actual=str(exc)))

    # Case 2: .nr and .ds state
    try:
        roff_src = (inputs_dir / "groff-state-001.roff").read_text()
        expected = json.loads((expected_dir / "groff-state-001.behavior.json").read_text())
        rc, stdout, _ = run_candidate("--state", roff_src)
        passed = False
        if rc == 0:
            report = json.loads(stdout)
            exp = expected.get('expect', {})
            regs_ok = all(report.get('registers', {}).get(k) == v for k, v in exp.get('registers', {}).items())
            strs_ok = all(report.get('strings', {}).get(k) == v for k, v in exp.get('strings', {}).items())
            render_ok = exp.get('render_contains', '') in report.get('render', '')
            passed = regs_ok and strs_ok and render_ok
        out.append(CaseResult(name="groff-state-001-nr-ds", passed=passed, expected=str(expected), actual=stdout[:200]))
    except Exception as exc:
        out.append(CaseResult(name="groff-state-001-nr-ds", passed=False, expected="", actual=str(exc)))

    # Case 3: inline macro expansion produces correct render
    try:
        roff_src = ".de HELLO\nHello from macro\n..\n.HELLO\n"
        rc, stdout, _ = run_candidate("--behavior", roff_src)
        passed = False
        if rc == 0:
            report = json.loads(stdout)
            passed = "Hello from macro" in report.get('render', '')
        out.append(CaseResult(name="inline-macro-invoke", passed=passed, expected="Hello from macro", actual=stdout[:200]))
    except Exception as exc:
        out.append(CaseResult(name="inline-macro-invoke", passed=False, expected="", actual=str(exc)))

    return out


def eval_roff_request_interpreter_subset(candidate: str) -> List[CaseResult]:
    """Evaluate roff request interpreter: conditionals, register semantics."""
    out: List[CaseResult] = []

    def run_behavior(roff_src):
        proc = subprocess.run(
            [candidate, "--behavior"],
            input=roff_src,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return proc.returncode, proc.stdout

    # Case 1: .if with true condition renders body
    try:
        roff_src = ".nr X 1\n.if 1 true branch\nfallthrough\n"
        rc, stdout = run_behavior(roff_src)
        passed = False
        if rc == 0:
            report = json.loads(stdout)
            passed = "true branch" in report.get('render', '')
        out.append(CaseResult(name="if-true-renders", passed=passed, expected="true branch", actual=stdout[:200]))
    except Exception as exc:
        out.append(CaseResult(name="if-true-renders", passed=False, expected="", actual=str(exc)))

    # Case 2: .if with false (0) condition does not render body
    try:
        roff_src = ".if 0 should-not-appear\nvisible\n"
        rc, stdout = run_behavior(roff_src)
        passed = False
        if rc == 0:
            report = json.loads(stdout)
            render = report.get('render', '')
            passed = "should-not-appear" not in render and "visible" in render
        out.append(CaseResult(name="if-false-skips", passed=passed, expected="visible only", actual=stdout[:200]))
    except Exception as exc:
        out.append(CaseResult(name="if-false-skips", passed=False, expected="", actual=str(exc)))

    # Case 3: .nr register stores and expands correctly
    try:
        roff_src = ".nr COUNT 42\n\\n[COUNT]\n"
        rc, stdout = run_behavior(roff_src)
        passed = False
        if rc == 0:
            report = json.loads(stdout)
            passed = "42" in report.get('render', '') and report.get('registers', {}).get('COUNT') == 42
        out.append(CaseResult(name="nr-register-expand", passed=passed, expected="42", actual=stdout[:200]))
    except Exception as exc:
        out.append(CaseResult(name="nr-register-expand", passed=False, expected="", actual=str(exc)))

    # Case 4: .ds string stores and expands
    try:
        roff_src = ".ds GREET world\nhello \\*[GREET]\n"
        rc, stdout = run_behavior(roff_src)
        passed = False
        if rc == 0:
            report = json.loads(stdout)
            passed = "hello world" in report.get('render', '')
        out.append(CaseResult(name="ds-string-expand", passed=passed, expected="hello world", actual=stdout[:200]))
    except Exception as exc:
        out.append(CaseResult(name="ds-string-expand", passed=False, expected="", actual=str(exc)))

    return out


def eval_roff_fill_diversion_subset(candidate: str) -> List[CaseResult]:
    """Evaluate roff fill/no-fill state and diversions."""
    FIXTURES = Path(__file__).parent.parent / "results" / "fixtures" / "groff-lite-v1"
    out: List[CaseResult] = []

    def run_behavior(roff_src):
        proc = subprocess.run(
            [candidate, "--behavior"],
            input=roff_src,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return proc.returncode, proc.stdout

    # Case 1: .nf/.fi from fixture
    try:
        roff_src = (FIXTURES / "inputs" / "groff-flow-001.roff").read_text()
        expected = json.loads((FIXTURES / "expected" / "groff-flow-001.behavior.json").read_text())
        rc, stdout = run_behavior(roff_src)
        passed = False
        if rc == 0:
            report = json.loads(stdout)
            exp = expected.get('expect', {})
            render = report.get('render', '')
            passed = exp.get('no_fill_preserves', '') in render and exp.get('fill_mode_has_text', '') in render
        out.append(CaseResult(name="nf-fi-flow", passed=passed, expected=str(expected), actual=stdout[:200]))
    except Exception as exc:
        out.append(CaseResult(name="nf-fi-flow", passed=False, expected="", actual=str(exc)))

    # Case 2: diversion capture
    try:
        roff_src = ".di CAPTURED\ndiversion content\n.di\nafter diversion\n"
        rc, stdout = run_behavior(roff_src)
        passed = False
        if rc == 0:
            report = json.loads(stdout)
            divs = report.get('diversions', {})
            render = report.get('render', '')
            passed = 'CAPTURED' in divs and 'diversion content' in '\n'.join(divs.get('CAPTURED', [])) and 'after diversion' in render
        out.append(CaseResult(name="diversion-capture", passed=passed, expected="CAPTURED diversion", actual=stdout[:200]))
    except Exception as exc:
        out.append(CaseResult(name="diversion-capture", passed=False, expected="", actual=str(exc)))

    # Case 3: no-fill mode preserves spacing
    try:
        roff_src = ".nf\nline  one\nline  two\n.fi\n"
        rc, stdout = run_behavior(roff_src)
        passed = False
        if rc == 0:
            report = json.loads(stdout)
            render = report.get('render', '')
            passed = 'line  one' in render and 'line  two' in render
        out.append(CaseResult(name="nf-preserves-spacing", passed=passed, expected="line  one", actual=stdout[:200]))
    except Exception as exc:
        out.append(CaseResult(name="nf-preserves-spacing", passed=False, expected="", actual=str(exc)))

    return out


def eval_roff_backend_plaintext_subset(candidate: str) -> List[CaseResult]:
    """Evaluate roff plaintext/terminal rendering backend."""
    FIXTURES = Path(__file__).parent.parent / "results" / "fixtures" / "groff-lite-v1"
    out: List[CaseResult] = []

    def run_render(roff_src):
        proc = subprocess.run(
            [candidate, "--render"],
            input=roff_src,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return proc.returncode, proc.stdout

    # Case 1: state fixture renders register+string correctly
    try:
        roff_src = (FIXTURES / "inputs" / "groff-state-001.roff").read_text()
        rc, stdout = run_render(roff_src)
        passed = rc == 0 and "3 hello" in stdout
        out.append(CaseResult(name="state-plaintext-render", passed=passed, expected="3 hello", actual=stdout[:200]))
    except Exception as exc:
        out.append(CaseResult(name="state-plaintext-render", passed=False, expected="", actual=str(exc)))

    # Case 2: macro invocation renders to plaintext
    try:
        roff_src = (FIXTURES / "inputs" / "groff-macro-001.roff").read_text()
        rc, stdout = run_render(roff_src)
        passed = rc == 0 and "Macro line 1" in stdout and "Macro line 2" in stdout
        out.append(CaseResult(name="macro-plaintext-render", passed=passed, expected="Macro line 1\nMacro line 2", actual=stdout[:200]))
    except Exception as exc:
        out.append(CaseResult(name="macro-plaintext-render", passed=False, expected="", actual=str(exc)))

    # Case 3: escape sequences render correctly in plaintext
    try:
        roff_src = ".PP\nword \\- hyphen\n"
        rc, stdout = run_render(roff_src)
        passed = rc == 0 and "word - hyphen" in stdout
        out.append(CaseResult(name="escape-plaintext-render", passed=passed, expected="word - hyphen", actual=stdout[:200]))
    except Exception as exc:
        out.append(CaseResult(name="escape-plaintext-render", passed=False, expected="", actual=str(exc)))

    # Case 4: no-fill mode preserves line structure
    try:
        roff_src = ".nf\nfirst line\nsecond line\n.fi\n"
        rc, stdout = run_render(roff_src)
        passed = rc == 0 and "first line" in stdout and "second line" in stdout
        out.append(CaseResult(name="nf-plaintext-render", passed=passed, expected="first line\nsecond line", actual=stdout[:200]))
    except Exception as exc:
        out.append(CaseResult(name="nf-plaintext-render", passed=False, expected="", actual=str(exc)))

    return out


def eval_roff_compatibility_differential(candidate: str) -> List[CaseResult]:
    """Differential harness: compare candidate --render vs nroff for groff-lite-v1 fixtures."""
    FIXTURES = Path(__file__).parent.parent / "results" / "fixtures" / "groff-lite-v1" / "inputs"
    out: List[CaseResult] = []

    def normalize(text: str) -> str:
        """Normalize whitespace and unicode minus for comparison."""
        return re.sub(r'\s+', ' ', text.replace('\u2212', '-').replace('\u2010', '-')).strip()

    for roff_file in sorted(FIXTURES.glob("*.roff")):
        fixture_id = roff_file.stem
        try:
            roff_src = roff_file.read_text()
            # Reference: nroff
            ref_proc = subprocess.run(
                ["nroff", str(roff_file)],
                capture_output=True, text=True, timeout=10,
            )
            ref_raw = ref_proc.stdout
            # Remove backspace-encoded bold/underline (col -b equivalent)
            ref_clean = re.sub(r'.\x08', '', ref_raw)
            ref_norm = normalize(ref_clean)

            # Candidate
            cand_proc = subprocess.run(
                [candidate, "--render"],
                input=roff_src,
                capture_output=True, text=True, timeout=10,
            )
            cand_norm = normalize(cand_proc.stdout)

            passed = ref_norm == cand_norm
            out.append(CaseResult(
                name=f"diff-{fixture_id}",
                passed=passed,
                expected=ref_norm[:200],
                actual=cand_norm[:200],
            ))
        except Exception as exc:
            out.append(CaseResult(name=f"diff-{fixture_id}", passed=False, expected="", actual=str(exc)))

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--candidate", required=True, help="candidate command path")
    args = ap.parse_args()

    task = args.task.strip()
    candidate = args.candidate.strip()

    if task == "basename-subset":
        results = eval_basename(candidate)
    elif task == "wc-subset":
        results = eval_wc(candidate)
    elif task == "cut-subset":
        results = eval_cut(candidate)
    elif task == "uniq-subset":
        results = eval_uniq(candidate)
    elif task == "sort-subset":
        results = eval_sort(candidate)
    elif task == "grep-lite-subset":
        results = eval_grep_lite(candidate)
    elif task == "grep-core-regex-flags":
        results = eval_grep_core_regex_flags(candidate)
    elif task == "grep-file-context":
        results = eval_grep_file_context(candidate)
    elif task == "roff-tokenizer-parser-subset":
        results = eval_roff_tokenizer_parser_subset(candidate)
    elif task == "roff-macro-expansion-subset":
        results = eval_roff_macro_expansion_subset(candidate)
    elif task == "roff-request-interpreter-subset":
        results = eval_roff_request_interpreter_subset(candidate)
    elif task == "roff-fill-diversion-subset":
        results = eval_roff_fill_diversion_subset(candidate)
    elif task == "roff-backend-plaintext-subset":
        results = eval_roff_backend_plaintext_subset(candidate)
    elif task == "roff-compatibility-differential":
        results = eval_roff_compatibility_differential(candidate)
    else:
        print(json.dumps({"status": "error", "error": f"unsupported task: {task}"}))
        return 1

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    pass_rate = (passed / total) if total else 0.0

    payload = {
        "status": "ok",
        "task": task,
        "candidate": candidate,
        "total_cases": total,
        "passed_cases": passed,
        "pass_rate": pass_rate,
        "failures": [
            {
                "name": r.name,
                "expected": r.expected,
                "actual": r.actual,
                "detail": r.detail,
            }
            for r in results
            if not r.passed
        ],
    }

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
