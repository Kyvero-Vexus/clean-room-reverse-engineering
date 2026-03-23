#!/usr/bin/env python3
import argparse
import sys

def emit(mode, line, count):
    if line is None:
        return
    if mode == 'default':
        print(line)
    elif mode == 'c':
        print(f"{count:7d} {line}")
    elif mode == 'd':
        if count > 1:
            print(line)
    elif mode == 'u':
        if count == 1:
            print(line)

def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument('-c', action='store_true')
    ap.add_argument('-d', action='store_true')
    ap.add_argument('-u', action='store_true')
    args, extra = ap.parse_known_args()
    if extra:
      print('usage: uniq [-c|-d|-u]', file=sys.stderr)
      return 2

    mode = 'default'
    if args.c: mode = 'c'
    if args.d: mode = 'd'
    if args.u: mode = 'u'

    cur = None
    cnt = 0

    for raw in sys.stdin:
        line = raw.rstrip('\n')
        if cur is None:
            cur = line
            cnt = 1
            continue
        if line == cur:
            cnt += 1
        else:
            emit(mode, cur, cnt)
            cur = line
            cnt = 1

    # Mutation fix: always flush terminal group.
    emit(mode, cur, cnt)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
