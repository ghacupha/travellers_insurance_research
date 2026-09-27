#!/usr/bin/env python3
"""Build Python authority for illustrative P&C case formulas from sourced opening facts."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bizplan.insurance.projection import Drivers, project


def main():
    root = Path(__file__).resolve().parents[1] / 'examples/travelers'
    scenarios = json.loads((root / 'operating_scenarios.json').read_text())
    history = json.loads((root / 'historical_actuals.json').read_text())
    if scenarios['company'] != history['company'] or scenarios['years'] != list(range(2026, 2031)):
        raise ValueError('Operating forecast issuer or years mismatch')
    if scenarios.get('forecast_scope') != 'constant_fy2025_perimeter_excludes_2026_canadian_disposal':
        raise ValueError('Operating forecast must declare its Canadian disposal boundary')
    facts = {(f['year'], f['metric']): f['value'] for f in history['facts']}
    opening = {metric: facts[2025, metric] for metric in
               ('gwp', 'gross_upr', 'ceded_upr', 'gross_reserves', 'unpaid_recoverables')}
    cases = {name: project(opening, Drivers(**drivers), scenarios['years'])
             for name, drivers in scenarios['cases'].items()}
    output = dict(schema_version=1, status=scenarios['status'],
                  forecast_scope=scenarios['forecast_scope'], scope_source=scenarios['scope_source'],
                  company=history['company'],
                  years=scenarios['years'], opening=opening, cases=cases)
    target = root / 'operating_forecast_reference.json'
    target.write_text(json.dumps(output, indent=2, allow_nan=False) + '\n')
    print(f'Python forecast reference: {len(cases)} cases, {len(scenarios["years"])} years')


if __name__ == '__main__':
    main()
