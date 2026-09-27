"""Deterministic, provenance-preserving initial Travelers research output."""
from dataclasses import replace
from datetime import date
import json
from pathlib import Path

from .analytics import monte_carlo
from .projection import Drivers, project
from .schedules import finite
from .company import Company
from .adapters import calculate_ratios


def load_actuals(path, as_of, company=None):
    date.fromisoformat(as_of)
    document = json.loads(Path(path).read_text())
    if document['schema_version'] != 1:
        raise ValueError('Expected actuals schema version 1')
    actual_company = Company(**document['company']).validate()
    if company is not None and actual_company != company:
        raise ValueError('Actuals company/profile differs from run configuration')
    if document['currency_unit'] != 'USD million':
        raise ValueError('Expected USD million')
    if not document['periods']:
        raise ValueError('At least one historical period is required')
    for row in document['periods']:
        if row['period_start'] != f"{row['year']}-01-01" or row['period_end'] != f"{row['year']}-12-31":
            raise ValueError('Only full calendar years are supported')
        for metric, fact in row['facts'].items():
            finite(**{metric: fact['value']})
            expected_unit = 'fraction' if metric.startswith('reported_') and metric.endswith('_ratio') else 'USD million'
            if fact['unit'] != expected_unit:
                raise ValueError(f'{metric} has wrong unit')
            source = document['sources'][fact['source_id']]
            date.fromisoformat(source['published'])
            if source['published'] > as_of:
                raise ValueError(f"{metric} was not available as of {as_of}")
            if not fact['locator'] or fact['status'] != 'disclosed':
                raise ValueError(f'{metric} needs disclosed status and a table locator')
            if not source['url'].startswith('https://'):
                raise ValueError('Source URL required')
    years = [row['year'] for row in document['periods']]
    if len(set(years)) != len(years) or years != sorted(years):
        raise ValueError('Actual periods must be unique and ordered')
    return document


def build(actuals_path, output_dir, as_of, demo_path=None, company=None):
    actuals = load_actuals(actuals_path, as_of, company)
    company = Company(**actuals['company']).validate()
    historical = []
    warnings = []
    for row in actuals['periods']:
        facts = row['facts']
        ratios = calculate_ratios(facts, company.ratio_adapter)
        # Reported percentages are rounded to 0.1 percentage point.
        if abs(ratios['combined_ratio']-facts['reported_combined_ratio']['value']) > .0005:
            raise ValueError(f"Combined ratio reconciliation failed: {row['year']}")
        for metric in ('loss_ratio', 'expense_ratio'):
            disclosed = facts.get(f'reported_{metric}')
            if disclosed and abs(ratios[metric]-disclosed['value']) > .0005:
                warnings.append(f"{row['year']} {metric}: bridge calculates {ratios[metric]:.4%}; "
                                f"issuer reports {disclosed['value']:.4%}. Unresolved source discrepancy; "
                                'do not overwrite the disclosed value.')
        historical.append(dict(year=row['year'], ratios=ratios, facts=facts))
    result = dict(schema_version=1, company=actuals['company'], ticker=company.ticker, as_of=as_of,
                  currency_unit='USD million', status='partial_historical_research',
                  sources=actuals['sources'], historical=historical,
                  warnings=warnings,
                  valuation=None,
                  limitations=['Full premium/reserve history and integrated statements pending.',
                               'No market price, calibrated forecast, price target or recommendation.'])
    if demo_path:
        demo = json.loads(Path(demo_path).read_text())
        if demo['status'] != 'synthetic_not_travelers':
            raise ValueError('Only explicitly synthetic projection examples are supported')
        drivers = Drivers(**demo['drivers'])
        cases = {'base': drivers,
                 'higher_catastrophes': replace(drivers, catastrophe_loss_ratio=drivers.catastrophe_loss_ratio+.05),
                 'adverse_reserves': replace(drivers, development_share_opening_reserves=.03)}
        result['synthetic_example'] = dict(
            status=demo['status'], inputs=demo,
            scenarios={name: project(demo['opening'], d, demo['years']) for name, d in cases.items()},
            monte_carlo=monte_carlo(demo['opening'], drivers, demo['years']))
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    lines = [f'# {company.name} — initial historical research', '',
             f'Information cutoff: {as_of}. Currency: USD millions.', '',
             '**Partial model: no valuation or investment recommendation.**', '',
             '| Year | NWP | NEP | Calculated loss ratio | Calculated expense ratio | Calculated combined ratio |',
             '|---|---:|---:|---:|---:|---:|']
    for row in historical:
        f, r = row['facts'], row['ratios']
        lines.append(f"| {row['year']} | {f['nwp']['value']:,.0f} | {f['nep']['value']:,.0f} | "
                     f"{r['loss_ratio']:.2%} | {r['expense_ratio']:.2%} | {r['combined_ratio']:.2%} |")
    lines += ['', f'Ratio adapter: {company.ratio_adapter}.',
              'Every historical input retains its source and table locator in research.json.', '',
              '## Remaining work', ''] + [f'- {item}' for item in result['limitations']]
    if warnings:
        lines += ['', '## Reconciliation findings', ''] + [f'- {item}' for item in warnings]
    if demo_path:
        lines += ['', 'The JSON also contains a separately labelled synthetic schedule/scenario demo.',
                  'Its amounts and assumptions are not company estimates.']
    lines += ['', '## Sources', '']
    for source in actuals['sources'].values():
        lines.append(f"- [{source['title']}]({source['url']}) (published {source['published']}; accessed {source['accessed']}).")
    (output/'research.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    (output/'research.md').write_text('\n'.join(lines)+'\n')
    return result
