#!/usr/bin/env python3
"""Compare selected original SEC HTML rows with normalized historical facts."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bizplan.insurance.sec_parity import write_sec_parity


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sec', type=Path, default=Path('examples/travelers/sec_parity_tables.json'))
    parser.add_argument('--history', type=Path, default=Path('examples/travelers/historical_actuals.json'))
    parser.add_argument('--statements', type=Path, default=Path('examples/travelers/statement_controls.json'))
    parser.add_argument('--output', type=Path, default=Path('examples/travelers/sec_parity_results.json'))
    parser.add_argument('--as-of', default='2026-02-12')
    args = parser.parse_args()
    result = write_sec_parity(args.sec, args.history, args.statements, args.output, args.as_of)
    print(f"{result['checked_rows']} selected SEC rows matched")


if __name__ == '__main__':
    main()
