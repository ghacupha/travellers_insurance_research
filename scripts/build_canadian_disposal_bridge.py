#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

"""Build separately dated Travelers Canadian-disposal evidence bridges."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bizplan.insurance.disposal import write_disposal_bridge


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, default=Path('examples/travelers/canadian_disposal_sources.json'))
    parser.add_argument('--history', type=Path, default=Path('examples/travelers/historical_actuals.json'))
    parser.add_argument('--statements', type=Path, default=Path('examples/travelers/statement_controls.json'))
    parser.add_argument('--integrated', type=Path, default=Path('examples/travelers/historical_integration.json'))
    parser.add_argument('--output-dir', type=Path, default=Path('examples/travelers'))
    args = parser.parse_args()
    for cutoff in ('2026-02-12', '2026-04-16'):
        result = write_disposal_bridge(args.sources, args.history, args.statements,
                                       args.integrated,
                                       args.output_dir / f'canadian_disposal_{cutoff}.json', cutoff)
        print(f'{cutoff}: {len(result["facts"])} facts; {len(result["checks"])} checks; {result["status"]}')


if __name__ == '__main__':
    main()
