#!/usr/bin/env python3
import argparse, sys

def parse_fields(spec):
    out=[]
    for part in spec.split(','):
        part=part.strip()
        if not part:
            continue
        if '-' in part:
            a,b=part.split('-',1)
            a=int(a); b=int(b)
            step=1 if b>=a else -1
            out.extend(range(a,b+step,step))
        else:
            out.append(int(part))
    if not out:
        raise ValueError('empty selector')
    return out

def main():
    ap=argparse.ArgumentParser(add_help=False)
    ap.add_argument('-d', dest='delim')
    ap.add_argument('-f', dest='fields')
    ap.add_argument('-s', dest='suppress', action='store_true')
    args, extra = ap.parse_known_args()
    if extra or not args.delim or not args.fields or len(args.delim) != 1:
        print('usage: cut -d <delim> -f <fields> [-s]', file=sys.stderr)
        return 2

    try:
        idxs=parse_fields(args.fields)
    except Exception:
        print('invalid field selector', file=sys.stderr)
        return 2

    d=args.delim
    for raw in sys.stdin:
        line=raw.rstrip('\n')

        # Compatibility-critical branch:
        # - with -s: suppress lines without delimiter
        # - without -s: pass through unchanged
        if d not in line:
            if args.suppress:
                continue
            print(line)
            continue

        parts=line.split(d)
        vals=[]
        for i in idxs:
            if 1 <= i <= len(parts):
                vals.append(parts[i-1])
        print(d.join(vals))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
