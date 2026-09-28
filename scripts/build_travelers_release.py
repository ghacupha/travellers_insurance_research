#!/usr/bin/env python3
"""Run the Travelers insurance harness and package reviewed PDF/XLSX deliverables."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bizplan.insurance.harness import run
from bizplan.insurance.report_pdf import collect_report_data, render_report
from bizplan.insurance.workbook import build_workbook


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deliverables-dir', type=Path,
                        default=ROOT / 'examples/travelers/deliverables')
    parser.add_argument('--output-dir', type=Path,
                        help='A new output run directory; defaults to a timestamped output run')
    args = parser.parse_args()
    python = sys.executable
    for script in ('build_historical.py', 'build_statement_controls.py',
                   'build_historical_integration.py', 'build_operating_movements.py',
                   'build_canadian_disposal_bridge.py', 'build_operating_forecast_reference.py',
                   'check_sec_parity.py'):
        subprocess.run([python, str(ROOT / 'scripts' / script)], cwd=ROOT, check=True)
    run_dir = run(ROOT / 'examples/travelers/run.json', output_dir=args.output_dir)
    workbook = run_dir / 'Travelers_Insurance_Operating_Model.xlsx'
    pdf = run_dir / 'Travelers_Equity_Research_Status.pdf'
    build_workbook(ROOT, workbook)
    report_data = collect_report_data(ROOT, run_dir)
    render_report(report_data, pdf)
    deliverables = args.deliverables_dir.resolve()
    deliverables.mkdir(parents=True, exist_ok=True)
    for source in (workbook, pdf):
        shutil.copy2(source, deliverables / source.name)
    hashes = {source.name: sha256(source.read_bytes()).hexdigest() for source in (workbook, pdf)}
    record = dict(schema_version=1, issuer='TRV', run_id=report_data['run_id'],
                  historical_information_cutoff=report_data['as_of'],
                  later_disposal_evidence_cutoff=report_data['later_as_of'],
                  source_fingerprint=report_data['source_fingerprint'],
                  valuation_status='not_available_no_rating_or_price_target',
                  artifacts=hashes)
    (deliverables / 'release_manifest.json').write_text(json.dumps(record, indent=2) + '\n')
    print(f'Release run: {run_dir}')
    print(f'Deliverables: {deliverables}')


if __name__ == '__main__':
    main()
