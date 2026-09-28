# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

import json
from pathlib import Path
import tempfile
import unittest

from bizplan.insurance.pipeline import build
from bizplan.insurance.report_pdf import collect_report_data


ROOT = Path(__file__).resolve().parents[1]


class InsuranceReportDataTests(unittest.TestCase):
    def test_six_year_report_remains_unrated_with_separate_sale_cutoffs(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            build(ROOT / 'examples/travelers/actuals.json', run_dir, '2026-02-12')
            (run_dir / 'manifest.json').write_text(json.dumps({
                'status': 'complete', 'run_id': 'test-run', 'git_revision': 'test-revision'}))
            data = collect_report_data(ROOT, run_dir)
            self.assertEqual(len(data['annual']), 6)
            self.assertEqual(data['annual'][-1]['net_income'], 6288)
            self.assertEqual(data['continuing_net_reserves'], 58219)
            self.assertEqual(data['continuing_nwp'], 43398)
            self.assertEqual(data['as_of'], '2026-02-12')
            self.assertEqual(data['later_as_of'], '2026-04-16')
            self.assertEqual(len(data['source_fingerprint']), 64)
            self.assertIn('exclude the Canadian sale', data['warning'])
            self.assertEqual(len(data['annual_source_rows']), 7)
            self.assertEqual(data['annual_source_rows'][1]['premium']['label'],
                             'FY2022 report, p.179')
            self.assertEqual(data['annual_source_rows'][1]['income']['label'],
                             'FY2022 report, p.145')
            self.assertEqual({item['fiscal_year'] for item in data['annual_sources']},
                             {2019, 2021, 2022, 2023, 2025})

            research_path = run_dir / 'research.json'
            research = json.loads(research_path.read_text())
            research['valuation'] = {'price_target': 1}
            research_path.write_text(json.dumps(research))
            with self.assertRaisesRegex(ValueError, 'validated partial insurance run'):
                collect_report_data(ROOT, run_dir)


if __name__ == '__main__':
    unittest.main()
