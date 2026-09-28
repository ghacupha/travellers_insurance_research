# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

"""Sourced GAAP statement controls; not a forecast or a full statement renderer."""
from collections import Counter
from datetime import date
from hashlib import sha256
import json
from pathlib import Path


BS_ROWS = ('fixed_maturity_fair', 'fixed_maturity_cost', 'equity_investments',
           'real_estate_investments', 'short_term_investments', 'other_investments',
           'total_investments', 'cash', 'accrued_investment_income',
           'premium_receivables', 'total_recoverables', 'ceded_upr', 'dac',
           'total_assets', 'balance_sheet_claim_reserves', 'gross_upr', 'debt',
           'total_liabilities', 'equity')
IS_ROWS = ('nep', 'investment_income', 'fee_income', 'realized_gains',
           'other_revenue', 'total_revenue', 'claims', 'dac_amortization',
           'general_admin', 'interest_expense', 'total_expenses',
           'pretax_income', 'tax_expense', 'net_income')
CF_ROWS = ('cash_flow_net_income', 'cfo', 'cfi', 'cff', 'cash_fx', 'cash_change_before_reclassification',
           'cash_flow_opening', 'cash_held_for_sale_reclassification', 'cash_flow_closing')


def build_statement_controls(raw, inventory, history, as_of):
    date.fromisoformat(as_of)
    if raw['company'] != inventory['company'] or history['company'] != raw['company']:
        raise ValueError('Issuer mismatch in statement controls')
    if raw['unit'] != 'USD million':
        raise ValueError('Statement control unit mismatch')
    sources = {s['fiscal_year']: s for s in inventory['sources']}
    filings = history['filings']
    facts, checks = [], []
    seen = set()

    def add(year, metric, value, report_year, page, statement):
        key = (year, metric, statement)
        if key in seen:
            raise ValueError(f'Duplicate statement fact: {key}')
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f'Non-numeric statement fact: {key}')
        source = sources[report_year]
        filing = filings[str(report_year)]
        if report_year < year or filing['filed'] > as_of:
            raise ValueError(f'Statement fact unavailable at cutoff: {key}')
        if source['reviewed_tables'][statement]['pdf_page'] != page:
            raise ValueError(f'Incorrect statement PDF page: {key}')
        seen.add(key)
        facts.append(dict(year=year, metric=metric, value=value, unit='USD million',
                          scope='consolidated', status='disclosed', statement=statement,
                          source_id=source['id'], source_pdf_url=source['url'],
                          source_pdf_sha256=source['sha256'], pdf_page=page,
                          sec_filing_accession=filing['accession'],
                          sec_filing_date=filing['filed'], sec_filing_url=filing['url'],
                          cutoff_status='filing_date_verified_pdf_copy_row_parity_pending'))

    def check(year, name, actual, expected):
        difference = actual-expected
        checks.append(dict(year=year, check=name, actual=actual, expected=expected,
                           difference=difference, status='pass' if difference == 0 else 'fail'))
        if difference:
            raise ValueError(f'{name} mismatch in {year}: {difference}')

    balances = {}
    for table in raw['balance_sheet']:
        year, report_year, page = table['year'], table['report_year'], table['pdf_page']
        if year in balances or set(table) != set(BS_ROWS) | {'year', 'report_year', 'pdf_page'}:
            raise ValueError(f'Invalid balance sheet year or fields: {year}')
        balances[year] = table
        for metric in BS_ROWS:
            add(year, metric, table[metric], report_year, page, 'balance_sheet')
        check(year, 'investment_asset_classes',
              sum(table[m] for m in ('fixed_maturity_fair', 'equity_investments',
                                     'real_estate_investments', 'short_term_investments',
                                     'other_investments')), table['total_investments'])
        check(year, 'balance_sheet', table['total_liabilities']+table['equity'], table['total_assets'])

    statement_data = {}
    for statement, tables, fields in (('income_statement', raw['income_statement'], IS_ROWS),
                                      ('cash_flow', raw['cash_flow'], CF_ROWS)):
        values = {}
        for table in tables:
            years = table['columns']
            if len(years) != len(set(years)) or set(table['rows']) != set(fields):
                raise ValueError(f'Invalid {statement} columns or rows')
            for row in fields:
                if len(table['rows'][row]) != len(years):
                    raise ValueError(f'Invalid {statement} row width: {row}')
                for year, value in zip(years, table['rows'][row]):
                    if year in values and row in values[year]:
                        raise ValueError(f'Duplicate {statement} year/row: {year} {row}')
                    values.setdefault(year, {})[row] = value
                    if row == 'cash_held_for_sale_reclassification' and value == 0:
                        # No dedicated line in pre-2025 cash-flow statements.
                        continue
                    add(year, row, value, table['report_year'], table['pdf_page'], statement)
        statement_data[statement] = values

    if set(balances) != set(range(2019, 2026)) or any(
            set(statement_data[s]) != set(range(2020, 2026))
            for s in ('income_statement', 'cash_flow')):
        raise ValueError('Statement controls do not cover the required fiscal window')

    history_index = {(f['year'], f['metric']): f['value'] for f in history['facts']}
    for year in range(2019, 2026):
        balance = balances[year]
        for metric in ('gross_upr', 'ceded_upr', 'dac'):
            if (year, metric) in history_index:
                check(year, f'balance_{metric}_to_operating_schedule',
                      balance[metric], history_index[year, metric])
        if (year, 'balance_sheet_claim_reserves') in history_index:
            check(year, 'balance_claims_to_reserve_schedule',
                  balance['balance_sheet_claim_reserves'],
                  history_index[year, 'balance_sheet_claim_reserves'])
    for year in range(2020, 2026):
        income, cash = statement_data['income_statement'][year], statement_data['cash_flow'][year]
        balance = balances[year]
        check(year, 'income_revenue', sum(income[m] for m in
              ('nep', 'investment_income', 'fee_income', 'realized_gains', 'other_revenue')),
              income['total_revenue'])
        check(year, 'income_expenses', sum(income[m] for m in
              ('claims', 'dac_amortization', 'general_admin', 'interest_expense')),
              income['total_expenses'])
        check(year, 'income_pretax', income['total_revenue']-income['total_expenses'],
              income['pretax_income'])
        check(year, 'income_net', income['pretax_income']-income['tax_expense'],
              income['net_income'])
        check(year, 'premium_to_income', income['nep'], history_index[year, 'nep'])
        check(year, 'income_to_cash_flow', income['net_income'], cash['cash_flow_net_income'])
        check(year, 'cash_flow_sections', sum(cash[m] for m in ('cfo', 'cfi', 'cff', 'cash_fx')),
              cash['cash_change_before_reclassification'])
        check(year, 'cash_flow_closing', cash['cash_flow_opening']+
              cash['cash_change_before_reclassification']-
              cash['cash_held_for_sale_reclassification'], cash['cash_flow_closing'])
        check(year, 'cash_flow_to_balance', cash['cash_flow_closing'], balance['cash'])
        check(year, 'prior_balance_to_cash_flow_opening', balances[year-1]['cash'],
              cash['cash_flow_opening'])
    return dict(schema_version=1, company=raw['company'], as_of=as_of,
                status='statement_controls_reconciled_to_issuer_pdf_not_full_integrated_model',
                facts=sorted(facts, key=lambda f: (f['year'], f['statement'], f['metric'])),
                checks=sorted(checks, key=lambda c: (c['year'], c['check'])),
                counts=dict(Counter(c['status'] for c in checks)),
                boundary='Only selected statement lines and controls; full line mapping, movements, segments and exact SEC HTML row parity remain pending.')


def write_statement_controls(raw_path, inventory_path, history_path, output_path, as_of):
    paths = (raw_path, inventory_path, history_path)
    raw, inventory, history = (json.loads(Path(p).read_text()) for p in paths)
    result = build_statement_controls(raw, inventory, history, as_of)
    result['input_hashes'] = {str(Path(p)): sha256(Path(p).read_bytes()).hexdigest() for p in paths}
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    return result
