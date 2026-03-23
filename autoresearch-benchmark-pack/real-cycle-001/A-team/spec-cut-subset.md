# A-Team Spec: cut-subset (clean-room)

Scope: GNU `cut` subset for delimiter + field selection behavior only.

## Allowed options
- `-d <char>` delimiter (single char expected)
- `-f <list>` field selector supporting:
  - single index (e.g., `2`)
  - comma list (e.g., `1,3`)
  - closed range (e.g., `2-4`)
- `-s` suppress lines with no delimiter

## Behavioral contract
1. Split each input line by delimiter.
2. Select requested 1-based fields in listed order.
3. Ignore fields that exceed line field count.
4. If no selected fields remain, output empty line.
5. Without `-s`, lines lacking delimiter are passed through unchanged when selecting field lists.
6. With `-s`, lines lacking delimiter are suppressed.

## Error handling
- Missing `-d` or `-f` => non-zero exit and brief usage error.
- Unsupported selectors => non-zero exit.

## Test vectors (oracle-driven)
- csv-field-2: `-d , -f 2`
- colon-fields-1-3: `-d : -f 1,3`
- pipe-range-2-4: `-d | -f 2-4`
- suppress-no-delim: `-d , -f 2 -s`

## Provenance note
Spec derived from black-box behavior and option docs; no upstream source copying.
