# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

from copy import deepcopy
import json
from pathlib import Path
import unittest

from bizplan.insurance.statement_controls import build_statement_controls


ROOT = Path(__file__).resolve().parents[1]


class StatementControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads((ROOT / 'examples/travelers/statement_control_tables.json').read_text())
        cls.inventory = json.loads((ROOT / 'examples/travelers/source_inventory.json').read_text())
        cls.history = json.loads((ROOT / 'examples/travelers/historical_actuals.json').read_text())

    def build(self, raw=None, cutoff='2026-02-12'):
        return build_statement_controls(raw or self.raw, self.inventory, self.history, cutoff)

    def test_six_year_statements_and_opening_balance_controls(self):
        result = self.build()
        self.assertEqual(result['counts'], {'pass': 89})
        facts = {(f['year'], f['metric'], f['statement']): f for f in result['facts']}
        self.assertEqual(facts[2019, 'total_assets', 'balance_sheet']['value'], 110122)
        self.assertEqual(facts[2025, 'total_assets', 'balance_sheet']['value'], 143708)
        self.assertEqual(facts[2025, 'total_investments', 'balance_sheet']['value'], 101182)
        self.assertEqual(facts[2025, 'net_income', 'income_statement']['value'], 6288)
        self.assertEqual(facts[2025, 'cash_held_for_sale_reclassification', 'cash_flow']['value'], 171)
        self.assertEqual(facts[2025, 'cash_flow_closing', 'cash_flow']['value'], 842)
        self.assertFalse(any(f['metric'] == 'cash_held_for_sale_reclassification' and f['year'] < 2025
                             for f in result['facts']))

    def test_bad_investment_or_cash_transcription_fails(self):
        raw = deepcopy(self.raw)
        raw['balance_sheet'][-1]['other_investments'] += 1
        with self.assertRaisesRegex(ValueError, 'investment_asset_classes mismatch'):
            self.build(raw)
        raw = deepcopy(self.raw)
        raw['cash_flow'][-1]['rows']['cash_held_for_sale_reclassification'][0] += 1
        with self.assertRaisesRegex(ValueError, 'cash_flow_closing mismatch'):
            self.build(raw)

    def test_income_statement_premium_must_match_operating_history(self):
        raw = deepcopy(self.raw)
        raw['income_statement'][-1]['rows']['nep'][0] += 1
        raw['income_statement'][-1]['rows']['total_revenue'][0] += 1
        raw['income_statement'][-1]['rows']['pretax_income'][0] += 1
        raw['income_statement'][-1]['rows']['net_income'][0] += 1
        with self.assertRaisesRegex(ValueError, 'premium_to_income mismatch'):
            self.build(raw)

    def test_cutoff_rejects_future_filing(self):
        with self.assertRaisesRegex(ValueError, 'unavailable at cutoff'):
            self.build(cutoff='2025-12-31')


if __name__ == '__main__':
    unittest.main()
