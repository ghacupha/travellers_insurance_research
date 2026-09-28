# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

from copy import deepcopy
import json
from pathlib import Path
import unittest

from bizplan.insurance.operating_movements import build_operating_movements


ROOT = Path(__file__).resolve().parents[1] / 'examples/travelers'


class OperatingMovementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads((ROOT / 'operating_movement_tables.json').read_text())
        cls.inventory = json.loads((ROOT / 'source_inventory.json').read_text())
        cls.history = json.loads((ROOT / 'historical_actuals.json').read_text())
        cls.statements = json.loads((ROOT / 'statement_controls.json').read_text())

    def build(self, raw=None, cutoff='2026-02-12'):
        return build_operating_movements(raw or self.raw, self.inventory,
                                         self.history, self.statements, cutoff)

    def test_equity_and_financing_reconcile_while_gaps_remain_open(self):
        result = self.build()
        self.assertEqual(len(result['facts']), 180)
        self.assertEqual(len(result['checks']), 30)
        self.assertTrue(all(check['status'] == 'pass' for check in result['checks']))
        gaps = {(row['year'], row['metric']): row['difference'] for row in result['bridges']}
        self.assertEqual(gaps[2025, 'net_premium_earning_gap'], -412)
        self.assertEqual(gaps[2025, 'dac_stock_gap'], -83)
        self.assertEqual(gaps[2025, 'investment_cash_proxy_gap'], -304)
        self.assertEqual(gaps[2025, 'debt_stock_gap'], 1)
        self.assertTrue(all(row['treatment'] == 'diagnostic_only_no_balancing_entry'
                            for row in result['bridges']))

    def test_equity_misstatement_fails(self):
        raw = deepcopy(self.raw)
        raw['equity'][-1]['rows']['equity_dividends'][0] += 1
        with self.assertRaisesRegex(ValueError, 'equity_rollforward'):
            self.build(raw)

    def test_financing_misstatement_fails(self):
        raw = deepcopy(self.raw)
        raw['cash_flow'][-1]['rows']['share_buybacks_cash'][0] += 1
        with self.assertRaisesRegex(ValueError, 'financing_cash_flow'):
            self.build(raw)

    def test_cutoff_rejects_future_filing(self):
        with self.assertRaisesRegex(ValueError, 'Unavailable'):
            self.build(cutoff='2025-12-31')


if __name__ == '__main__':
    unittest.main()
