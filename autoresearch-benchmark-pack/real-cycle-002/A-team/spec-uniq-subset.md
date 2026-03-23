# A-Team Spec: uniq-subset (clean-room)

Scope: GNU `uniq` subset for adjacent-group behavior only.

## Allowed options
- default (no option)
- `-c` count adjacent groups
- `-d` only groups with count > 1
- `-u` only groups with count == 1

## Behavioral contract
1. Operate on **adjacent** runs, not global set semantics.
2. Input line order is preserved by group order.
3. Final group at end-of-stream must be emitted according to selected mode.
4. Option semantics:
   - default: emit one representative line per adjacent group.
   - `-c`: emit count + representative line for every adjacent group.
   - `-d`: emit representative only for groups where count > 1.
   - `-u`: emit representative only for groups where count == 1.

## Error handling
- unsupported options => non-zero exit.

## Test vectors (oracle-driven)
- default
- -c
- -d
- -u

## Provenance note
Spec derived from black-box behavior and option docs; no upstream source copying.
