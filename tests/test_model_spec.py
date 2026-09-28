# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

import json
from pathlib import Path
import unittest

from bizplan.insurance.coverage import build_coverage
from bizplan.insurance.specification import metric_catalog, workbook_contract


ROOT = Path(__file__).resolve().parents[1]


class ModelSpecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = workbook_contract(list(range(2020, 2026)), list(range(2026, 2031)))
        cls.inventory = json.loads((ROOT / 'examples/travelers/source_inventory.json').read_text())
        cls.actuals = json.loads((ROOT / 'examples/travelers/actuals.json').read_text())

    def test_periods_and_opening_stock_policy(self):
        self.assertEqual(self.contract['opening_column'], 'G')
        self.assertEqual(self.contract['period_columns']['2020'], 'H')
        self.assertEqual(self.contract['period_columns']['2025'], 'M')
        self.assertEqual(self.contract['period_columns']['2026'], 'N')
        self.assertEqual(self.contract['period_columns']['2030'], 'R')
        self.assertTrue(next(r for r in self.contract['rows'] if r['id'] == 'net_upr')['opening_required'])
        self.assertFalse(next(r for r in self.contract['rows'] if r['id'] == 'nwp')['opening_required'])

    def test_catalog_ids_and_rows_are_unique(self):
        metrics = metric_catalog()
        self.assertEqual(len({m.id for m in metrics}), len(metrics))
        self.assertEqual(len({r['row'] for r in self.contract['rows']}), len(metrics))
        self.assertEqual(next(m for m in metrics if m.id == 'net_upr').equation,
                         'gross_upr - ceded_upr')
        self.assertNotEqual(next(m for m in metrics if m.id == 'reserve_prior_incurred').id,
                            next(m for m in metrics if m.id == 'reported_development').id)

    def test_invalid_period_windows_fail(self):
        for actual, forecast in (([], [2026]), ([2020], []), ([2020, 2022], [2023]),
                                 ([2020, 2021], [2023])):
            with self.subTest(actual=actual, forecast=forecast):
                with self.assertRaises(ValueError):
                    workbook_contract(actual, forecast)

    def test_coverage_does_not_promote_indexed_documents_to_actuals(self):
        coverage = build_coverage(self.contract, self.inventory, self.actuals, '2026-02-12')
        self.assertEqual(coverage['status'], 'coverage_inventory_not_validated_actuals')
        self.assertEqual(sum(coverage['counts'].values()), len(coverage['records']))
        self.assertFalse({'reconciled', 'validated'} & coverage['counts'].keys())
        rows = {(r['metric'], r['scope'], r['year']): r for r in coverage['records']}
        self.assertEqual(rows['nwp', 'consolidated', 2020]['status'], 'table_located')
        self.assertIsNone(rows['nwp', 'consolidated', 2020]['value'])
        self.assertEqual(rows['nwp', 'consolidated', 2025]['status'], 'extracted_unreconciled')
        self.assertEqual(rows['reported_loss_ratio', 'consolidated', 2025]['status'], 'issue_open')
        self.assertEqual(rows['nwp', 'business_insurance', 2025]['status'], 'document_indexed')
        self.assertIsNone(rows['nwp', 'business_insurance', 2025]['value'])
        self.assertNotIn(('nwp', 'consolidated', 2019), rows)
        self.assertIn(('net_upr', 'consolidated', 2019), rows)

    def test_post_cutoff_release_is_ineligible(self):
        coverage = build_coverage(self.contract, self.inventory, self.actuals, '2025-12-31')
        row = next(r for r in coverage['records'] if r['metric'] == 'nwp'
                   and r['scope'] == 'consolidated' and r['year'] == 2025)
        self.assertEqual(row['status'], 'after_cutoff')
        self.assertEqual(row['cutoff_eligibility'], 'ineligible')

    def test_sourced_history_updates_only_supported_consolidated_cells(self):
        history = json.loads((ROOT / 'examples/travelers/historical_actuals.json').read_text())
        coverage = build_coverage(self.contract, self.inventory, self.actuals,
                                  '2026-02-12', history)
        rows = {(r['metric'], r['scope'], r['year']): r for r in coverage['records']}
        self.assertEqual(rows['nwp', 'consolidated', 2020]['status'], 'pdf_reconciled')
        self.assertEqual(rows['net_upr', 'consolidated', 2025]['status'], 'pdf_extracted')
        self.assertEqual(rows['held_for_sale_upr', 'consolidated', 2025]['value'], 514)
        self.assertEqual(rows['reserve_prior_incurred', 'consolidated', 2025]['value'], -939)
        self.assertEqual(rows['reported_development', 'consolidated', 2025]['value'], -1036)
        self.assertEqual(rows['reported_loss_ratio', 'consolidated', 2025]['status'], 'issue_open')
        self.assertEqual(rows['nwp', 'business_insurance', 2025]['status'], 'document_indexed')
        self.assertIsNone(rows['upr_other_change', 'consolidated', 2025]['value'])

    def test_statement_controls_update_only_sourced_rows(self):
        history = json.loads((ROOT / 'examples/travelers/historical_actuals.json').read_text())
        statements = json.loads((ROOT / 'examples/travelers/statement_controls.json').read_text())
        coverage = build_coverage(self.contract, self.inventory, self.actuals,
                                  '2026-02-12', history, statements)
        rows = {(r['metric'], r['scope'], r['year']): r for r in coverage['records']}
        self.assertEqual(rows['total_assets', 'consolidated', 2019]['status'], 'statement_control_checked')
        self.assertEqual(rows['total_assets', 'consolidated', 2025]['value'], 143708)
        self.assertEqual(rows['investment_income', 'consolidated', 2025]['value'], 3959)
        self.assertEqual(rows['nwp', 'consolidated', 2025]['status'], 'pdf_reconciled')
        self.assertIsNone(rows['statutory_surplus', 'consolidated', 2025]['value'])

    def test_operating_controls_promote_only_matching_catalog_facts(self):
        history = json.loads((ROOT / 'examples/travelers/historical_actuals.json').read_text())
        statements = json.loads((ROOT / 'examples/travelers/statement_controls.json').read_text())
        movements = json.loads((ROOT / 'examples/travelers/operating_movements.json').read_text())
        coverage = build_coverage(self.contract, self.inventory, self.actuals,
                                  '2026-02-12', history, statements, movements)
        rows = {(r['metric'], r['scope'], r['year']): r for r in coverage['records']}
        self.assertEqual(rows['cash_tax', 'consolidated', 2025]['value'], 1274)
        self.assertEqual(rows['cash_tax', 'consolidated', 2025]['status'],
                         'operating_control_checked')
        self.assertEqual(rows['dividends', 'consolidated', 2025]['value'], 987)
        self.assertEqual(rows['closing_shares', 'consolidated', 2025]['value'], 217.5)
        self.assertIsNone(rows['dac_additions', 'consolidated', 2025]['value'])
        self.assertIsNone(rows['investment_disposal_carrying', 'consolidated', 2025]['value'])

    def test_source_inventory_has_one_official_report_per_year(self):
        sources = self.inventory['sources']
        self.assertEqual([s['fiscal_year'] for s in sources], list(range(2019, 2026)))
        self.assertEqual(len({s['id'] for s in sources}), len(sources))
        for source in sources:
            self.assertTrue(source['url'].startswith('https://s26.q4cdn.com/410417801/'))
            self.assertEqual(len(source['sha256']), 64)
            self.assertIsNone(source['publication_date'])
            self.assertEqual(source['cutoff_eligibility'], 'filing_date_verified_pdf_posting_and_parity_pending')
            self.assertTrue(all(1 <= table['pdf_page'] <= source['pages']
                                for table in source['reviewed_tables'].values()))


if __name__ == '__main__':
    unittest.main()
