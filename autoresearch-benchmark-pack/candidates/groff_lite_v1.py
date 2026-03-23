#!/usr/bin/env python3
"""Minimal groff-lite candidate for CRRE benchmark testing.

Implements a subset of roff processing:
- Tokenization (--tokenize)
- Behavior analysis (--behavior) 
- State inspection (--state)
- Plaintext rendering (--render)

This is a clean-room implementation derived from groff documentation,
not from groff source code.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Token:
    type: str
    name: str = ""
    args: str = ""
    contains: str = ""

    def to_dict(self) -> dict:
        return {k: v for k, v in {
            "type": self.type,
            "name": self.name,
            "args": self.args,
            "contains": self.contains,
        }.items() if v}


@dataclass
class GroffState:
    registers: dict[str, int] = field(default_factory=dict)
    strings: dict[str, str] = field(default_factory=dict)
    macros: dict[str, list[str]] = field(default_factory=dict)
    fill_mode: bool = True
    diversions: dict[str, list[str]] = field(default_factory=dict)
    current_diversion: str | None = None
    output_buffer: list[str] = field(default_factory=list)


def tokenize(text: str) -> list[Token]:
    """Tokenize roff input into a stream of tokens."""
    tokens: list[Token] = []
    lines = text.split('\n')
    
    for line in lines:
        if not line.strip():
            tokens.append(Token(type="blank"))
            continue
            
        # Request line (starts with . or ')
        if line.startswith('.') or line.startswith("'"):
            request_line = line[1:].strip()
            parts = request_line.split(None, 1)
            if parts:
                request_name = parts[0]
                args = parts[1] if len(parts) > 1 else ""
                
                # Macro definition
                if request_name in ('de', 'am'):
                    tokens.append(Token(type="request", name=request_name, args=args))
                # String/register definition
                elif request_name in ('ds', 'nr'):
                    tokens.append(Token(type="request", name=request_name, args=args))
                # Control requests
                elif request_name in ('nf', 'fi', 'di', 'if'):
                    tokens.append(Token(type="request", name=request_name, args=args))
                else:
                    tokens.append(Token(type="request", name=request_name, args=args))
            continue
        
        # Text line - check for escape sequences
        if '\\' in line:
            # Escape sequence handling
            escape_pattern = r'\\([a-zA-Z]|\[.*?\]|\(..|\{|\}|.)'
            parts = re.split(escape_pattern, line)
            text_content = ''.join(p for p in parts if p and not p.startswith('\\'))
            tokens.append(Token(type="text", contains=line))
        else:
            tokens.append(Token(type="text", contains=line))
    
    return tokens


def parse_roff(text: str) -> tuple[list[Token], GroffState]:
    """Parse roff text into tokens and initial state."""
    tokens = tokenize(text)
    state = GroffState()
    return tokens, state


def interpret(tokens: list[Token], state: GroffState) -> GroffState:
    """Interpret token stream and update state."""
    macro_buffer: list[str] = []
    macro_name: str | None = None
    i = 0
    
    while i < len(tokens):
        tok = tokens[i]
        
        if tok.type == "request":
            name = tok.name
            args = tok.args.strip()
            
            # Macro definition start
            if name == 'de':
                parts = args.split(None, 1)
                macro_name = parts[0] if parts else "UNNAMED"
                macro_buffer = []
            elif name == 'am':  # append to macro
                parts = args.split(None, 1)
                macro_name = parts[0] if parts else "UNNAMED"
                macro_buffer = list(state.macros.get(macro_name, []))
            elif name == 'ds':
                parts = args.split(None, 1)
                if len(parts) >= 2:
                    state.strings[parts[0]] = parts[1]
                elif len(parts) == 1:
                    state.strings[parts[0]] = ""
            elif name == 'nr':
                parts = args.split(None, 1)
                if len(parts) >= 2:
                    try:
                        state.registers[parts[0]] = int(parts[1])
                    except ValueError:
                        state.registers[parts[0]] = 0
                elif len(parts) == 1:
                    state.registers[parts[0]] = 0
            elif name == 'nf':
                state.fill_mode = False
            elif name == 'fi':
                state.fill_mode = True
            elif name == 'di':
                if args:
                    if args in state.diversions:
                        # End diversion
                        state.current_diversion = None
                    else:
                        # Start diversion
                        state.diversions[args] = []
                        state.current_diversion = args
                else:
                    state.current_diversion = None
            elif name == 'if':
                # Simple conditional: .if 1 or .if 0
                parts = args.split(None, 1)
                if parts:
                    condition = parts[0]
                    body = parts[1] if len(parts) > 1 else ""
                    if condition == '1' or condition.isdigit() and int(condition) != 0:
                        # Condition true - process body
                        state.output_buffer.append(body)
            elif macro_name and name == '..':
                # End macro definition
                if macro_name:
                    state.macros[macro_name] = macro_buffer
                macro_name = None
                macro_buffer = []
            elif macro_name:
                # Inside macro definition
                macro_buffer.append(f".{name} {args}" if args else f".{name}")
        
        elif tok.type == "text":
            text = tok.contains
            
            # Expand string interpolations
            for str_name, str_val in state.strings.items():
                text = text.replace(f'\\*[{str_name}]', str_val)
                text = text.replace(f'\\*{str_name}', str_val)
            
            # Expand register interpolations  
            for reg_name, reg_val in state.registers.items():
                text = text.replace(f'\\n[{reg_name}]', str(reg_val))
                text = text.replace(f'\\n{reg_name}', str(reg_val))
            
            # Handle escape sequences
            text = text.replace('\\-', '-')
            text = text.replace('\\ ', ' ')
            
            # Check if this is a macro invocation
            stripped = text.strip()
            if stripped.startswith('.'):
                # It's a request/macro call on this line - already handled above
                pass
            elif stripped in state.macros:
                # Macro invocation
                for macro_line in state.macros[stripped]:
                    state.output_buffer.append(macro_line)
            elif macro_name:
                # Inside macro definition
                macro_buffer.append(text)
            else:
                # Regular output
                if state.current_diversion:
                    state.diversions[state.current_diversion].append(text)
                else:
                    state.output_buffer.append(text)
        
        i += 1
    
    return state


def render(state: GroffState) -> str:
    """Render final output from state."""
    lines = []
    for line in state.output_buffer:
        # Clean up escape sequences
        clean = line
        clean = clean.replace('\\-', '-')
        clean = clean.replace('\\ ', ' ')
        lines.append(clean)
    return '\n'.join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Groff-lite clean-room implementation")
    ap.add_argument("--tokenize", action="store_true", help="Output token stream as JSON")
    ap.add_argument("--behavior", action="store_true", help="Output behavior analysis as JSON")
    ap.add_argument("--state", action="store_true", help="Output state as JSON")
    ap.add_argument("--render", action="store_true", help="Output plaintext render")
    ap.add_argument("file", nargs="?", help="Input file (default: stdin)")
    args = ap.parse_args()
    
    # Read input
    if args.file:
        text = open(args.file).read()
    else:
        text = sys.stdin.read()
    
    # Process
    tokens, state = parse_roff(text)
    state = interpret(tokens, state)
    
    # Output
    if args.tokenize:
        result = {"tokens": [t.to_dict() for t in tokens]}
        print(json.dumps(result, indent=2))
    elif args.behavior:
        result = {
            "tokens": [t.to_dict() for t in tokens],
            "macros": state.macros,
            "render": render(state),
        }
        print(json.dumps(result, indent=2))
    elif args.state:
        result = {
            "registers": state.registers,
            "strings": state.strings,
            "macros": state.macros,
            "diversions": state.diversions,
            "fill_mode": state.fill_mode,
            "render": render(state),
        }
        print(json.dumps(result, indent=2))
    elif args.render:
        print(render(state))
    else:
        # Default: render
        print(render(state))
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
