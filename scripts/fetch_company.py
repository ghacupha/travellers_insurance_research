#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

"""Fetch SEC data for any CIK supplied on the command line."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bizplan.insurance.cli import main

if __name__ == '__main__':
    raise SystemExit(main(['fetch', *sys.argv[1:]]))
