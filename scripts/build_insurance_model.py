#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

"""Thin script delegating to the company-neutral research harness."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bizplan.insurance.cli import main


if __name__ == '__main__':
    raise SystemExit(main(['run', *sys.argv[1:]]))
