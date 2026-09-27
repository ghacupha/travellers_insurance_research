"""Complete audited consolidated balance-sheet line controls for historical integration."""
from datetime import date
from hashlib import sha256
import json
from pathlib import Path


DETAIL_ROWS = (
    'deferred_tax_asset', 'contractholder_receivables', 'goodwill', 'intangible_assets',
    'other_assets', 'assets_held_for_sale', 'contractholder_payables',
    'reinsurance_premium_payables', 'deferred_tax_liability', 'other_liabilities',
    'liabilities_held_for_sale', 'common_stock', 'retained_earnings', 'aoci',
    'treasury_stock')
ASSET_CONTROL_ROWS = (
    'total_investments', 'cash', 'accrued_investment_income', 'premium_receivables',
    'total_recoverables', 'ceded_upr', 'dac')
ASSET_DETAIL_ROWS = (
    'deferred_tax_asset', 'contractholder_receivables', 'goodwill', 'intangible_assets',
    'other_assets', 'assets_held_for_sale')
LIABILITY_CONTROL_ROWS = ('balance_sheet_claim_reserves', 'gross_upr', 'debt')
LIABILITY_DETAIL_ROWS = (
    'contractholder_payables', 'reinsurance_premium_payables',
    'deferred_tax_liability', 'other_liabilities', 'liabilities_held_for_sale')
EQUITY_DETAIL_ROWS = ('common_stock', 'retained_earnings', 'aoci', 'treasury_stock')


def build_historical_integration(raw, inventory, history, statements, as_of):
    date.fromisoformat(as_of)
    if not raw['company'] == inventory['company'] == history['company'] == statements['company']:
        raise ValueError('Historical statement issuer mismatch')
    if raw['unit'] != 'USD million':
        raise ValueError('Historical statement unit mismatch')
    sources = {source['fiscal_year']: source for source in inventory['sources']}
    indexed = {}
    facts = []
    for table in raw['tables']:
        source = sources[table['report_year']]
        filing = history['filings'][str(table['report_year'])]
        if filing['filed'] > as_of or source['reviewed_tables']['balance_sheet']['pdf_page'] != table['pdf_page']:
            raise ValueError('Unavailable or misplaced balance-sheet detail table')
        if set(table['rows']) != set(DETAIL_ROWS) or len(table['columns']) != len(set(table['columns'])):
            raise ValueError('Invalid balance-sheet detail rows or periods')
        for metric in DETAIL_ROWS:
            values = table['rows'][metric]
            if len(values) != len(table['columns']):
                raise ValueError(f'Invalid balance-sheet detail width: {metric}')
            for year, value in zip(table['columns'], values):
                if year > table['report_year'] or (year, metric) in indexed:
                    raise ValueError(f'Duplicate or future balance-sheet detail: {year} {metric}')
                if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))):
                    raise ValueError(f'Invalid balance-sheet detail number: {year} {metric}')
                indexed[year, metric] = value
                if value is not None:
                    facts.append(dict(year=year, metric=metric, value=value, unit='USD million',
                                      status='disclosed', statement='balance_sheet',
                                      source_id=source['id'], source_pdf_url=source['url'],
                                      source_pdf_sha256=source['sha256'], pdf_page=table['pdf_page'],
                                      sec_filing_date=filing['filed'], sec_filing_url=filing['url']))
    if {year for year, _ in indexed} != set(range(2019, 2026)):
        raise ValueError('Balance-sheet detail must cover 2019–2025')
    controls = {(f['year'], f['metric']): f['value'] for f in statements['facts']}
    checks = []

    def check(year, metric, actual, expected):
        difference = actual-expected
        checks.append(dict(year=year, metric=metric, actual=actual, expected=expected,
                           difference=difference, status='pass' if difference == 0 else 'fail'))
        if difference:
            raise ValueError(f'Historical {metric} mismatch in {year}: {difference}')

    for year in range(2019, 2026):
        c = lambda metric: controls[year, metric]
        d = lambda metric: indexed[year, metric] or 0
        check(year, 'asset_lines',
              sum(c(metric) for metric in ASSET_CONTROL_ROWS) +
              sum(d(metric) for metric in ASSET_DETAIL_ROWS), c('total_assets'))
        check(year, 'liability_lines',
              sum(c(metric) for metric in LIABILITY_CONTROL_ROWS) +
              sum(d(metric) for metric in LIABILITY_DETAIL_ROWS), c('total_liabilities'))
        check(year, 'equity_components',
              sum(d(metric) for metric in EQUITY_DETAIL_ROWS), c('equity'))
        check(year, 'accounting_equation', c('total_assets'),
              c('total_liabilities') + c('equity'))
    return dict(schema_version=1, company=raw['company'], as_of=as_of,
                status='complete_audited_balance_sheet_line_controls_not_forecast',
                facts=sorted(facts, key=lambda fact: (fact['year'], fact['metric'])),
                checks=checks,
                boundary='Null presentation lines create no sourced zero facts. Original SEC HTML row parity remains separately tracked.')


def write_historical_integration(raw_path, inventory_path, history_path,
                                 statement_path, output_path, as_of):
    paths = (raw_path, inventory_path, history_path, statement_path)
    raw, inventory, history, statements = (json.loads(Path(path).read_text()) for path in paths)
    result = build_historical_integration(raw, inventory, history, statements, as_of)
    result['input_hashes'] = {str(Path(path)): sha256(Path(path).read_bytes()).hexdigest()
                              for path in paths}
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    return result
