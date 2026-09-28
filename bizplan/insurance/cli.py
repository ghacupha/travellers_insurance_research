# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

"""Company-neutral CLI; explicit commands separate acquisition and model execution."""
import argparse
import json
import os
from pathlib import Path
import sys

from .harness import run
from .sources import fetch_companyfacts, select_annual, STANDARD_TAGS


def main(argv=None):
    parser = argparse.ArgumentParser(prog='insurance-research')
    commands = parser.add_subparsers(dest='command', required=True)
    fetch = commands.add_parser('fetch', help='Cache SEC Company Facts for any CIK')
    fetch.add_argument('--cik', required=True)
    fetch.add_argument('--cache-dir', type=Path, default=Path('data/sec'))
    normalize = commands.add_parser('normalize', help='Extract initial annual US GAAP statement candidates')
    normalize.add_argument('--cik', required=True)
    normalize.add_argument('--snapshot', type=Path, required=True)
    normalize.add_argument('--as-of', required=True)
    normalize.add_argument('--years', type=int, nargs='+', required=True)
    normalize.add_argument('--output', type=Path, required=True)
    research = commands.add_parser('run', help='Validate inputs, calculate, and render a new research run')
    research.add_argument('--config', required=True, type=Path)
    research.add_argument('--output-dir', type=Path)
    research.add_argument('--demo', type=Path, help='Optional synthetic operating scenario config')
    args = parser.parse_args(argv)
    try:
        if args.command == 'fetch':
            print(fetch_companyfacts(args.cik, args.cache_dir, os.environ.get('SEC_USER_AGENT')))
        elif args.command == 'run':
            print(run(args.config, args.output_dir, args.demo).resolve())
        else:
            payload = json.loads(args.snapshot.read_text())
            results, unresolved = {}, []
            for year in args.years:
                results[year] = {}
                for metric, (tag, kind) in STANDARD_TAGS.items():
                    try:
                        results[year][metric] = select_annual(payload, tag, year, args.as_of,
                                                             kind, expected_cik=args.cik)
                    except ValueError as exc:
                        unresolved.append(str(exc))
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open('x') as handle:
                json.dump(dict(cik=args.cik, snapshot=str(args.snapshot.resolve()), as_of=args.as_of,
                               facts=results, unresolved=unresolved), handle, indent=2, allow_nan=False)
            print(f'{args.output}: {len(unresolved)} unresolved selections')
            return 2 if unresolved else 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr)
        return 2
    return 0
