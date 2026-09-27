#!/usr/bin/env python3
"""Regenerate the model specification and coverage ledger from source evidence."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bizplan.insurance.coverage import write_planning_outputs


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory',required=True,type=Path)
    parser.add_argument('--actuals',required=True,type=Path)
    parser.add_argument('--history',type=Path,help='Optional normalized historical premium/reserve facts')
    parser.add_argument('--statement-controls',type=Path,help='Optional audited statement control facts')
    parser.add_argument('--operating-movements',type=Path,help='Optional audited operating cash/equity facts')
    parser.add_argument('--output-dir',required=True,type=Path)
    parser.add_argument('--as-of',required=True)
    args=parser.parse_args()
    result=write_planning_outputs(args.inventory,args.actuals,args.output_dir,args.as_of,
                                  args.history,args.statement_controls,args.operating_movements)
    print(f"{len(result['records'])} coverage records: {result['counts']}")


if __name__=='__main__':
    main()
