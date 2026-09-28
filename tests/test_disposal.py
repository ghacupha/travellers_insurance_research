# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

from copy import deepcopy
import json
from pathlib import Path
import unittest

from bizplan.insurance.disposal import build_disposal_bridge


ROOT = Path(__file__).resolve().parents[1] / 'examples/travelers'


class CanadianDisposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads((ROOT / 'canadian_disposal_sources.json').read_text())
        cls.history = json.loads((ROOT / 'historical_actuals.json').read_text())
        cls.statements = json.loads((ROOT / 'statement_controls.json').read_text())
        cls.integrated = json.loads((ROOT / 'historical_integration.json').read_text())

    def build(self, raw=None, cutoff='2026-04-16'):
        return build_disposal_bridge(raw or self.raw, self.history, self.statements,
                                     self.integrated, cutoff)

    def test_february_cutoff_does_not_see_april_facts(self):
        result = self.build(cutoff='2026-02-12')
        self.assertEqual(len(result['facts']), 10)
        self.assertEqual(len(result['checks']), 7)
        self.assertEqual(result['derived']['disposed_net_assets_book'], 2008)
        self.assertEqual(result['derived']['investment_balance_opening_already_excludes_hfs'], 101182)
        self.assertEqual(result['derived']['cash_balance_opening_already_excludes_hfs'], 842)
        self.assertNotIn('continuing_net_claim_reserves_opening', result['derived'])
        self.assertNotIn('continuing_2025_nwp_comparable', result['derived'])
        with self.assertRaisesRegex(ValueError, 'unavailable at cutoff'):
            self.build(cutoff='2025-12-31')

    def test_april_bridge_distinguishes_unpaid_recovery_and_cash_gain(self):
        result = self.build()
        self.assertEqual(len(result['facts']), 20)
        self.assertEqual(len(result['checks']), 10)
        self.assertTrue(all(check['status'] == 'pass' for check in result['checks']))
        facts = {fact['metric']: fact for fact in result['facts']}
        self.assertEqual(facts['hfs_assets_total']['period_type'], 'instant')
        self.assertEqual(facts['divested_nwp_total_2025']['period_end'], '2025-12-31')
        self.assertEqual(facts['cash_proceeds_q1_2026']['period_end'], '2026-03-31')
        d = result['derived']
        self.assertEqual(d['disposed_unpaid_claim_recoverables_implied'], 282)
        self.assertEqual(d['held_for_sale_reinsurance_other_than_unpaid_implied'], 3)
        self.assertEqual(d['continuing_net_claim_reserves_opening'], 58219)
        self.assertEqual(d['continuing_gross_claim_reserves_opening'], 65734)
        self.assertEqual(d['continuing_unpaid_claim_recoverables_opening'], 7515)
        self.assertEqual(d['continuing_2025_nwp_comparable'], 43398)
        self.assertEqual(d['continuing_2025_nep_comparable'], 42879)
        self.assertEqual(d['cash_proceeds_less_2025_disposal_book_net_assets_diagnostic'], 376)
        self.assertNotIn('gain', d)

    def test_wrong_source_or_premium_total_is_rejected(self):
        raw = deepcopy(self.raw)
        raw['facts'][0]['source'] = 'q1_2026_10q'
        with self.assertRaisesRegex(ValueError, 'Wrong source'):
            self.build(raw)
        raw = deepcopy(self.raw)
        next(f for f in raw['facts'] if f['metric'] == 'divested_nwp_personal_2025')['value'] += 1
        with self.assertRaisesRegex(ValueError, 'divested_nwp_segments mismatch'):
            self.build(raw)

    def test_2025_held_for_sale_total_must_match_historical_balance_sheet(self):
        raw = deepcopy(self.raw)
        next(f for f in raw['facts'] if f['metric'] == 'hfs_assets_total')['value'] += 1
        with self.assertRaisesRegex(ValueError, 'held_for_sale_asset_classes mismatch'):
            self.build(raw)


if __name__ == '__main__':
    unittest.main()
