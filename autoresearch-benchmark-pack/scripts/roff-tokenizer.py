#!/usr/bin/env python3
"""Clean-room roff tokenizer/parser/evaluator subset.

Usage:
  roff-tokenizer.py --tokenize < input.roff     -> JSON token list
  roff-tokenizer.py --behavior < input.roff     -> JSON behavior report
  roff-tokenizer.py --state    < input.roff     -> JSON state report (registers/strings/render)

All output on stdout as JSON.
"""
import json
import re
import sys


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

def tokenize(lines):
    tokens = []
    for line in lines:
        line = line.rstrip('\n')
        if line.startswith('.') and len(line) > 1:
            # Request line: .NAME arg1 arg2 ...
            parts = line[1:].split(None, 1)
            name = parts[0]
            args = []
            if len(parts) > 1:
                # simple whitespace split for args
                args = parts[1].split()
            tokens.append({'type': 'request', 'name': name, 'args': args})
        elif line.startswith('..'):
            tokens.append({'type': 'end_macro'})
        else:
            # Text line - extract escapes
            escapes = re.findall(r'\\[\\&\-\w\[\]]*', line)
            if escapes:
                for esc in escapes:
                    tokens.append({'type': 'escape', 'contains': esc})
            # Also emit as text if there's non-escape content
            text_stripped = re.sub(r'\\[\\&\-\w\[\]]*', '', line).strip()
            if text_stripped:
                tokens.append({'type': 'text', 'contains': text_stripped})
    return tokens


# ---------------------------------------------------------------------------
# Parser / interpreter
# ---------------------------------------------------------------------------

class RoffInterpreter:
    def __init__(self):
        self.registers = {}    # name -> int
        self.strings = {}      # name -> str
        self.macros = {}       # name -> [lines]
        self.output_lines = []
        self.fill_mode = True
        self.diversions = {}   # name -> [lines]
        self._diversion_active = None  # current diversion name or None

    def _expand_inline(self, text):
        """Expand register/string references in text."""
        # \n[N] -> register N
        def repl_nr(m):
            return str(self.registers.get(m.group(1), 0))
        text = re.sub(r'\\n\[([^\]]+)\]', repl_nr, text)
        # \*[S] -> string S
        def repl_str(m):
            return self.strings.get(m.group(1), '')
        text = re.sub(r'\\\*\[([^\]]+)\]', repl_str, text)
        # \- -> -  \\ -> \ \& -> (zero-width)
        text = text.replace('\\-', '-').replace('\\\\', '\\').replace('\\&', '')
        return text

    def process(self, source):
        lines = source.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith('..'):
                i += 1
                continue
            if line.startswith('.'):
                parts = line[1:].split(None, 1)
                request = parts[0]
                rest = parts[1] if len(parts) > 1 else ''
                if request == 'de':
                    # Define macro
                    macro_name = rest.strip().split()[0]
                    body = []
                    i += 1
                    while i < len(lines) and not lines[i].startswith('..'):
                        body.append(lines[i])
                        i += 1
                    self.macros[macro_name] = body
                elif request == 'am':
                    # Append to macro
                    macro_name = rest.strip().split()[0]
                    body = []
                    i += 1
                    while i < len(lines) and not lines[i].startswith('..'):
                        body.append(lines[i])
                        i += 1
                    existing = self.macros.get(macro_name, [])
                    self.macros[macro_name] = existing + body
                elif request == 'nr':
                    # Set number register: .nr NAME value
                    args = rest.strip().split()
                    if len(args) >= 2:
                        try:
                            self.registers[args[0]] = int(args[1])
                        except ValueError:
                            pass
                elif request == 'ds':
                    # Define string: .ds NAME value
                    args = rest.strip().split(None, 1)
                    if len(args) >= 2:
                        self.strings[args[0]] = args[1]
                    elif len(args) == 1:
                        self.strings[args[0]] = ''
                elif request == 'nf':
                    self.fill_mode = False
                elif request == 'fi':
                    self.fill_mode = True
                elif request == 'di':
                    # Start diversion: .di NAME
                    diversion_name = rest.strip().split()[0] if rest.strip() else ''
                    if diversion_name:
                        self._diversion_active = diversion_name
                        if diversion_name not in self.diversions:
                            self.diversions[diversion_name] = []
                    else:
                        # .di with no arg ends diversion
                        self._diversion_active = None
                elif request == 'da':
                    # Append diversion: .da NAME
                    diversion_name = rest.strip().split()[0] if rest.strip() else ''
                    if diversion_name:
                        self._diversion_active = diversion_name
                        if diversion_name not in self.diversions:
                            self.diversions[diversion_name] = []
                    else:
                        self._diversion_active = None
                elif request in ('TH', 'SH', 'PP', 'LP', 'br'):
                    pass  # structural, no text output
                elif request == 'if':
                    # .if COND body  - simple numeric/string conditionals
                    cond_body = rest.strip()
                    result = self._eval_condition(cond_body)
                    if result:
                        body_text = cond_body.split(None, 1)[1] if ' ' in cond_body else ''
                        body_text = body_text.strip()
                        if body_text.startswith('\\{'):
                            body_text = body_text[2:].strip()
                        if body_text:
                            expanded = self._expand_inline(body_text)
                            self.output_lines.append(expanded)
                elif request == 'ie':
                    cond_body = rest.strip()
                    self._last_if = self._eval_condition(cond_body)
                    if self._last_if:
                        body_text = cond_body.split(None, 1)[1] if ' ' in cond_body else ''
                        body_text = body_text.strip().lstrip('\\{').strip()
                        if body_text:
                            self.output_lines.append(self._expand_inline(body_text))
                elif request == 'el':
                    if not getattr(self, '_last_if', True):
                        body_text = rest.strip().lstrip('\\{').strip()
                        if body_text:
                            self.output_lines.append(self._expand_inline(body_text))
                elif request in self.macros:
                    # Invoke macro
                    for mline in self.macros[request]:
                        expanded = self._expand_inline(mline)
                        self.output_lines.append(expanded)
                # other unknown requests: ignore
            else:
                expanded = self._expand_inline(line)
                if self._diversion_active:
                    self.diversions[self._diversion_active].append(expanded)
                else:
                    self.output_lines.append(expanded)
            i += 1

    def _eval_condition(self, cond_body):
        """Evaluate a simple roff condition string."""
        # Extract condition token (first word)
        parts = cond_body.split(None, 1)
        if not parts:
            return False
        cond = parts[0]
        # Numeric: if the condition is a number
        try:
            return int(cond) != 0
        except ValueError:
            pass
        # Register comparison: \n[N]>0 or similar
        expanded = self._expand_inline(cond)
        try:
            return int(expanded) != 0
        except ValueError:
            pass
        # String: 't' = troff mode (True), 'n' = nroff mode (False)
        if cond == 't':
            return True
        if cond == 'n':
            return False
        return False

    def render(self):
        return '\n'.join(l for l in self.output_lines if l.strip())


# ---------------------------------------------------------------------------
# Behavior checks
# ---------------------------------------------------------------------------

def behavior_report(source):
    interp = RoffInterpreter()
    interp.process(source)
    render = interp.render()
    return {
        'registers': interp.registers,
        'strings': interp.strings,
        'macros': {k: v for k, v in interp.macros.items()},
        'diversions': {k: v for k, v in interp.diversions.items()},
        'render': render,
        'render_lines': interp.output_lines,
        'fill_mode': interp.fill_mode,
        'no_fill_segments': [],   # placeholder
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    source = sys.stdin.read()
    lines = source.splitlines(keepends=True)

    if '--behavior' in sys.argv or '--state' in sys.argv:
        report = behavior_report(source)
        print(json.dumps(report, indent=2))
    elif '--render' in sys.argv:
        # Plaintext backend: output rendered text only
        report = behavior_report(source)
        print(report.get('render', ''))
    else:
        # Default: tokenize
        toks = tokenize(lines)
        print(json.dumps(toks, indent=2))


if __name__ == '__main__':
    main()
