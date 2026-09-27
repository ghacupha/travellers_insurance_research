import contextlib
from hashlib import sha256
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from bizplan.insurance.cli import main
from bizplan.insurance.company import Company
from bizplan.insurance.harness import run
from bizplan.insurance.sources import fetch_companyfacts, select_annual

ROOT = Path(__file__).resolve().parents[1]


class HarnessTests(unittest.TestCase):
    def test_snapshot_can_replay_and_outputs_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = run(ROOT/'examples/travelers/run.json', Path(tmp)/'first')
            manifest = json.loads((output/'manifest.json').read_text())
            self.assertEqual(manifest['status'], 'complete')
            self.assertEqual(manifest['artifacts']['research.json'],
                             sha256((output/'research.json').read_bytes()).hexdigest())
            second = run(output/'inputs/run.json', Path(tmp)/'second')
            self.assertEqual((output/'research.json').read_bytes(), (second/'research.json').read_bytes())
            with self.assertRaises(FileExistsError):
                run(ROOT/'examples/travelers/run.json', output)

    def test_failed_run_records_error_and_does_not_publish_research(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = json.loads((ROOT/'examples/travelers/run.json').read_text())
            cfg['actuals'] = str(ROOT/'examples/travelers/actuals.json')
            cfg['as_of'] = '2025-12-31'
            path = Path(tmp)/'config.json'
            path.write_text(json.dumps(cfg))
            output = Path(tmp)/'failed'
            with self.assertRaises(ValueError):
                run(path, output)
            self.assertEqual(json.loads((output/'manifest.json').read_text())['status'], 'failed')
            self.assertFalse((output/'research.json').exists())

    def test_another_pc_issuer_needs_no_fetch_or_model_code_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            company = dict(name='Synthetic P&C Test Company', ticker='TEST', cik='123456',
                           accounting_basis='US_GAAP', insurer_type='property_casualty', ratio_adapter='standard_pc')
            source = dict(title='Synthetic test disclosure', url='https://example.invalid/fixture',
                          published='2025-02-01', accessed='2026-09-23')
            facts = {name: dict(value=value, unit='fraction' if name=='reported_combined_ratio' else 'USD million',
                                source_id='fixture', locator=name, status='disclosed')
                     for name, value in dict(nwp=105, nep=100, loss_ratio_numerator=60,
                                            expense_ratio_numerator=30, reported_combined_ratio=.9).items()}
            actuals = dict(schema_version=1, company=company, currency_unit='USD million',
                           sources={'fixture':source}, periods=[dict(year=2024, period_start='2024-01-01',
                                                                    period_end='2024-12-31', facts=facts)])
            (Path(tmp)/'actuals.json').write_text(json.dumps(actuals))
            cfg = dict(schema_version=1, company=company, as_of='2025-03-01', actuals='actuals.json')
            (Path(tmp)/'config.json').write_text(json.dumps(cfg))
            output = run(Path(tmp)/'config.json', Path(tmp)/'out')
            result = json.loads((output/'research.json').read_text())
            self.assertEqual(result['ticker'], 'TEST')
            self.assertAlmostEqual(result['historical'][0]['ratios']['combined_ratio'], .9)

    def test_life_profile_rejected_instead_of_using_pc_engine(self):
        with self.assertRaisesRegex(ValueError, 'life and IFRS'):
            Company('Example', 'TEST', '123456', 'IFRS', 'life', 'standard_pc').validate()

    def test_fetch_is_company_neutral_and_keeps_raw_bytes(self):
        raw = json.dumps({'cik':123456, 'facts':{}}).encode()
        response = MagicMock()
        response.__enter__.return_value.read.return_value = raw
        with tempfile.TemporaryDirectory() as tmp, patch('bizplan.insurance.sources.urlopen', return_value=response) as http:
            path = fetch_companyfacts('123456', tmp, 'Test suite contact@example.invalid')
            self.assertEqual(path.read_bytes(), raw)
            self.assertIn('CIK0000123456.json', http.call_args[0][0].full_url)
            self.assertEqual(path.stem, sha256(raw).hexdigest())

    def test_snapshot_issuer_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, 'issuer'):
            select_annual({'cik':123456, 'facts':{}}, 'Assets', 2024,
                          '2025-02-01', 'instant', expected_cik='86312')

    def test_cli_failure_returns_nonzero(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(['run', '--config', '/nonexistent/config.json']), 2)


if __name__ == '__main__':
    unittest.main()
