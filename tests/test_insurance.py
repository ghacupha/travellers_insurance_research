import json
from pathlib import Path
import tempfile
import unittest

from bizplan.insurance.analytics import dividend_value, regression, monte_carlo
from bizplan.insurance.pipeline import build, load_actuals
from bizplan.insurance.projection import Drivers, project
from bizplan.insurance.schedules import (PremiumInputs, ReserveInputs, premiums, reserves,
                                         investment_portfolio, equity)
from bizplan.insurance.sources import select_annual

ROOT = Path(__file__).resolve().parents[1]


class ScheduleTests(unittest.TestCase):
    def test_earning_differs_from_written(self):
        p = premiums(PremiumInputs(100, 0, 20, 0, 75, 0, 15, 0, 0))
        self.assertEqual((p['gwp'], p['nwp'], p['nep']), (100, 80, 20))

    def test_reserves_include_unpaid_and_signed_development(self):
        r = reserves(ReserveInputs(100, 10, 40, -5, 10, 20, 2, 12))
        self.assertEqual(r['incurred_net'], 35)
        self.assertEqual(r['closing_net'], 97)
        self.assertEqual(r['closing_gross'], 109)

    def test_non_cash_reserve_change_is_not_incurred_loss(self):
        r = reserves(ReserveInputs(100, 0, 0, 0, 0, 0, 8, 0))
        self.assertEqual(r['incurred_net'], 0)
        self.assertEqual(r['closing_net'], 108)

    def test_invalid_reinsurance_and_nonfinite_rejected(self):
        for ceded in (101, float('nan')):
            with self.assertRaises(ValueError):
                premiums(PremiumInputs(100, 0, ceded, 0, 0, 0, 0, 0, 0))

    def test_portfolio_and_equity_changes_are_separate_from_income(self):
        p = investment_portfolio(100, 20, 10, -5, 0, .04)
        self.assertEqual(p['closing'], 105)
        self.assertAlmostEqual(p['net_investment_income'], 4.1)
        self.assertEqual(equity(100, 10, -5, 2, 3, 1, 0)['closing'], 101)


class SecTests(unittest.TestCase):
    def setUp(self):
        self.original = dict(start='2024-01-01', end='2024-12-31', val=1000000,
                             form='10-K', filed='2025-02-15', accn='original')
        self.payload = {'cik':86312, 'facts':{'us-gaap':{'NetIncomeLoss':{'units':{'USD':[
            self.original,
            dict(self.original, start='2024-10-01', val=200000),
            dict(self.original, filed='2026-02-15', accn='later', val=1100000)]}}}}}

    def test_no_quarter_or_lookahead_contamination(self):
        f = select_annual(self.payload, 'NetIncomeLoss', 2024, '2025-12-31', 'duration')
        self.assertEqual(f['value'], 1)
        self.assertEqual(f['source']['accession'], 'original')

    def test_restatement_only_when_available(self):
        self.assertEqual(select_annual(self.payload, 'NetIncomeLoss', 2024,
                                      '2026-03-01', 'duration')['value'], 1.1)

    def test_missing_is_not_zero(self):
        with self.assertRaises(ValueError):
            select_annual(self.payload, 'Assets', 2024, '2025-12-31', 'instant')

    def test_ambiguous_facts_rejected(self):
        self.payload['facts']['us-gaap']['NetIncomeLoss']['units']['USD'].append(dict(self.original, val=2))
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            select_annual(self.payload, 'NetIncomeLoss', 2024, '2025-12-31', 'duration')


class PipelineTests(unittest.TestCase):
    def test_report_reproduces_disclosures_and_has_no_price_target(self):
        with tempfile.TemporaryDirectory() as out:
            result = build(ROOT/'examples/travelers/actuals.json', out, '2026-02-12',
                           ROOT/'examples/travelers/synthetic_projection.json')
            self.assertIsNone(result['valuation'])
            self.assertAlmostEqual(result['historical'][1]['ratios']['combined_ratio'], .899, delta=.0005)
            self.assertEqual(result['historical'][1]['ratios']['loss_numerator'], 26990)
            self.assertIn('2025 loss_ratio', result['warnings'][0])
            self.assertTrue((Path(out)/'research.md').is_file())
            self.assertEqual(result['synthetic_example']['status'], 'synthetic_not_travelers')

    def test_release_cannot_be_used_before_publication(self):
        with self.assertRaises(ValueError):
            load_actuals(ROOT/'examples/travelers/actuals.json', '2025-12-31')

    def test_broken_reconciliation_blocks_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads((ROOT/'examples/travelers/actuals.json').read_text())
            data['periods'][0]['facts']['claims']['value'] += 1000
            path = Path(tmp)/'bad.json'
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'reconciliation'):
                build(path, Path(tmp)/'out', '2026-02-12')
            self.assertFalse((Path(tmp)/'out/research.json').exists())

    def test_projection_rollforward_and_reproducibility(self):
        demo = json.loads((ROOT/'examples/travelers/synthetic_projection.json').read_text())
        d = Drivers(**demo['drivers'])
        rows = project(demo['opening'], d, demo['years'])
        self.assertEqual(rows[1]['reserves']['opening_net'], rows[0]['reserves']['closing_net'])
        a = monte_carlo(demo['opening'], d, demo['years'], draws=20)
        b = monte_carlo(demo['opening'], d, demo['years'], draws=20)
        self.assertEqual(a, b)

    def test_valuation_and_regression_guards(self):
        self.assertAlmostEqual(dividend_value([10], .1, 0)['equity_value'], 100)
        with self.assertRaises(ValueError):
            dividend_value([10], .03, .04)
        self.assertEqual(regression([1,2,3], [3,5,7])['slope'], 2)
        with self.assertRaises(ValueError):
            regression([1,1,1], [2,3,4])


if __name__ == '__main__':
    unittest.main()
