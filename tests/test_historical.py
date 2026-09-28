# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

from copy import deepcopy
import json
from pathlib import Path
import unittest

from bizplan.insurance.historical import build_history


ROOT = Path(__file__).resolve().parents[1]


class HistoricalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads((ROOT / 'examples/travelers/historical_tables.json').read_text())
        cls.inventory = json.loads((ROOT / 'examples/travelers/source_inventory.json').read_text())
        cls.release = json.loads((ROOT / 'examples/travelers/actuals.json').read_text())

    def history(self, raw=None, cutoff='2026-02-12'):
        return build_history(raw or self.raw, self.inventory, cutoff, self.release)

    def test_six_year_premium_and_reserve_rollforwards(self):
        history = self.history()
        self.assertEqual(history['counts']['fail'] if 'fail' in history['counts'] else 0, 0)
        self.assertEqual(len(history['issues']), 7)
        facts = {(f['year'], f['metric']): f for f in history['facts']}
        self.assertEqual(facts[2019, 'net_reserves']['value'], 43801)
        self.assertEqual(facts[2020, 'adoption_change']['value'], 53)
        self.assertEqual(facts[2025, 'nwp']['value'], 44387)
        self.assertEqual(facts[2025, 'nep']['value'], 43914)
        self.assertEqual(facts[2025, 'gross_upr']['value'], 22431)
        self.assertEqual(facts[2025, 'net_upr']['value'], 21148)
        self.assertEqual(facts[2025, 'gross_reserves']['value'], 67643)
        self.assertEqual(facts[2025, 'unpaid_recoverables']['value'], 7797)
        self.assertEqual(facts[2025, 'net_reserves']['value'], 59846)
        self.assertEqual(facts[2025, 'held_for_sale_upr']['value'], 514)
        self.assertEqual(facts[2025, 'balance_sheet_claim_reserves']['value'], 65737)
        self.assertEqual(facts[2025, 'nwp']['sec_filing_date'], '2026-02-12')
        self.assertEqual({f['year'] for f in history['facts']}, set(range(2019, 2026)))

    def test_upr_bridge_gap_is_visible_and_not_plugged(self):
        history = self.history()
        checks = {(c['year'], c['check']): c for c in history['checks']}
        self.assertEqual(checks[2025, 'net_premium_earning_from_reported_upr']['difference'], -412)
        self.assertTrue(any(i['issue'] == 'held_for_sale_net_upr_unknown' for i in history['issues']))
        self.assertEqual(checks[2025, 'claims_reserve_balance_sheet_presentation']['status'], 'pass')
        self.assertFalse(any(f['metric'] == 'upr_other_change' for f in history['facts']))

    def test_bad_transcription_fails_without_balancing_plug(self):
        raw = deepcopy(self.raw)
        raw['reserve_tables'][-1]['paid_current'] += 1
        with self.assertRaisesRegex(ValueError, 'reserve_paid mismatch'):
            self.history(raw)

    def test_wrong_page_and_future_filing_fail(self):
        raw = deepcopy(self.raw)
        raw['premium_tables'][0]['pdf_page'] += 1
        with self.assertRaisesRegex(ValueError, 'Page does not match reviewed table'):
            self.history(raw)
        with self.assertRaisesRegex(ValueError, 'Filing unavailable at cutoff'):
            self.history(cutoff='2025-12-31')


if __name__ == '__main__':
    unittest.main()
