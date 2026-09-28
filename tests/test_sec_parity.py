# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

from copy import deepcopy
import json
from pathlib import Path
import unittest

from bizplan.insurance.sec_parity import check_sec_parity


ROOT = Path(__file__).resolve().parents[1] / 'examples/travelers'


class SecParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sec = json.loads((ROOT / 'sec_parity_tables.json').read_text())
        cls.history = json.loads((ROOT / 'historical_actuals.json').read_text())
        cls.statements = json.loads((ROOT / 'statement_controls.json').read_text())

    def test_selected_rows_match_and_bases_remain_distinct(self):
        result = check_sec_parity(self.sec, self.history, self.statements, '2026-02-12')
        self.assertEqual(result['checked_rows'], 88)
        self.assertTrue(all(row['status'] == 'match' for row in result['results']))
        reserve = next(row for row in result['results']
                       if row['year'] == 2025 and row['metric'] == 'pc_reserves_continuing')
        self.assertEqual(reserve['sec_value'], 65734)
        self.assertEqual(reserve['pdf_value'], 65734)
        self.assertNotIn(2020, {row['year'] for row in result['results']})

    def test_transcription_error_fails(self):
        sec = deepcopy(self.sec)
        sec['tables'][0]['rows']['nwp'][0] += 1
        with self.assertRaisesRegex(ValueError, 'SEC parity mismatch'):
            check_sec_parity(sec, self.history, self.statements, '2026-02-12')

    def test_future_or_wrong_filing_fails(self):
        with self.assertRaisesRegex(ValueError, 'unavailable'):
            check_sec_parity(self.sec, self.history, self.statements, '2025-12-31')
        sec = deepcopy(self.sec)
        sec['tables'][0]['url'] = sec['tables'][1]['url']
        with self.assertRaisesRegex(ValueError, 'URL mismatch'):
            check_sec_parity(sec, self.history, self.statements, '2026-02-12')


if __name__ == '__main__':
    unittest.main()
