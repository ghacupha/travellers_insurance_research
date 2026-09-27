#!/usr/bin/env python3
"""Rebuild the sourced premium/reserve actuals and reconciliation ledger."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bizplan.insurance.historical import write_history


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tables', type=Path, default=Path('examples/travelers/historical_tables.json'))
    parser.add_argument('--inventory', type=Path, default=Path('examples/travelers/source_inventory.json'))
    parser.add_argument('--release', type=Path, default=Path('examples/travelers/actuals.json'))
    parser.add_argument('--output', type=Path, default=Path('examples/travelers/historical_actuals.json'))
    parser.add_argument('--as-of', default='2026-02-12')
    args = parser.parse_args()
    result = write_history(args.tables, args.inventory, args.output, args.as_of, args.release)
    print(f"{len(result['facts'])} facts; checks {result['counts']}; issues {len(result['issues'])}")


if __name__ == '__main__':
    main()
