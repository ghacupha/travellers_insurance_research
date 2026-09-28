#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

"""Rebuild sourced historical statement-control facts and checks."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bizplan.insurance.statement_controls import write_statement_controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tables', type=Path, default=Path('examples/travelers/statement_control_tables.json'))
    parser.add_argument('--inventory', type=Path, default=Path('examples/travelers/source_inventory.json'))
    parser.add_argument('--history', type=Path, default=Path('examples/travelers/historical_actuals.json'))
    parser.add_argument('--output', type=Path, default=Path('examples/travelers/statement_controls.json'))
    parser.add_argument('--as-of', default='2026-02-12')
    args = parser.parse_args()
    result = write_statement_controls(args.tables, args.inventory, args.history,
                                      args.output, args.as_of)
    print(f"{len(result['facts'])} facts; {result['counts']}")


if __name__ == '__main__':
    main()
