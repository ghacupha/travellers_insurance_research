# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

from copy import deepcopy
import json
from pathlib import Path
import unittest

from bizplan.insurance.historical_integration import build_historical_integration


ROOT = Path(__file__).resolve().parents[1] / 'examples/travelers'


class HistoricalIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads((ROOT / 'balance_sheet_detail_tables.json').read_text())
        cls.inventory = json.loads((ROOT / 'source_inventory.json').read_text())
        cls.history = json.loads((ROOT / 'historical_actuals.json').read_text())
        cls.statements = json.loads((ROOT / 'statement_controls.json').read_text())

    def build(self, raw=None, cutoff='2026-02-12'):
        return build_historical_integration(raw or self.raw, self.inventory,
                                            self.history, self.statements, cutoff)

    def test_all_balance_sheet_lines_and_held_for_sale_presentation(self):
        result = self.build()
        self.assertEqual(len(result['facts']), 86)
        self.assertEqual(len(result['checks']), 28)
        self.assertTrue(all(check['status'] == 'pass' for check in result['checks']))
        facts = {(fact['year'], fact['metric']): fact['value'] for fact in result['facts']}
        self.assertEqual(facts[2025, 'assets_held_for_sale'], 4550)
        self.assertEqual(facts[2025, 'liabilities_held_for_sale'], 2542)
        self.assertNotIn((2024, 'assets_held_for_sale'), facts)
        self.assertNotIn((2019, 'deferred_tax_asset'), facts)

    def test_misstated_asset_or_equity_component_fails(self):
        raw = deepcopy(self.raw)
        raw['tables'][-1]['rows']['other_assets'][0] += 1
        with self.assertRaisesRegex(ValueError, 'asset_lines mismatch'):
            self.build(raw)
        raw = deepcopy(self.raw)
        raw['tables'][-1]['rows']['treasury_stock'][0] += 1
        with self.assertRaisesRegex(ValueError, 'equity_components mismatch'):
            self.build(raw)

    def test_cutoff_rejects_unavailable_filing(self):
        with self.assertRaisesRegex(ValueError, 'Unavailable'):
            self.build(cutoff='2025-12-31')


if __name__ == '__main__':
    unittest.main()
