#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

"""Build the formula-linked Travelers operating workbook with Python."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bizplan.insurance.workbook import build_workbook


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', nargs='?', type=Path,
                        default=ROOT / 'output/travelers_operating_model.xlsx')
    args = parser.parse_args()
    print('Saved %s' % build_workbook(ROOT, args.output))


if __name__ == '__main__':
    main()
