#!/usr/bin/env python3
"""Rebuild audited operating cash/equity flows and open stock-bridge diagnostics."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bizplan.insurance.operating_movements import write_operating_movements


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tables', type=Path, default=Path('examples/travelers/operating_movement_tables.json'))
    parser.add_argument('--inventory', type=Path, default=Path('examples/travelers/source_inventory.json'))
    parser.add_argument('--history', type=Path, default=Path('examples/travelers/historical_actuals.json'))
    parser.add_argument('--statements', type=Path, default=Path('examples/travelers/statement_controls.json'))
    parser.add_argument('--output', type=Path, default=Path('examples/travelers/operating_movements.json'))
    parser.add_argument('--as-of', default='2026-02-12')
    args = parser.parse_args()
    result = write_operating_movements(args.tables, args.inventory, args.history,
                                       args.statements, args.output, args.as_of)
    print(f"{len(result['facts'])} facts, {len(result['checks'])} controls, {len(result['bridges'])} bridge diagnostics")


if __name__ == '__main__':
    main()
