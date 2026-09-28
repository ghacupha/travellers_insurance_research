# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

"""Audited P&C operating cash/equity flows and explicitly open stock bridges."""
from datetime import date
from hashlib import sha256
import json
from pathlib import Path


def build_operating_movements(raw, inventory, history, statements, as_of):
    date.fromisoformat(as_of)
    if not raw['company'] == inventory['company'] == history['company'] == statements['company']:
        raise ValueError('Issuer mismatch in operating schedules')
    sources = {entry['fiscal_year']: entry for entry in inventory['sources']}
    values = {}
    facts = []
    for statement in ('cash_flow', 'equity'):
        for table in raw[statement]:
            report_year = table['report_year']
            source = sources[report_year]
            filing = history['filings'][str(report_year)]
            if filing['filed'] > as_of or source['reviewed_tables'][statement]['pdf_page'] != table['pdf_page']:
                raise ValueError(f'Unavailable or misplaced operating table: {report_year} {statement}')
            years = table['columns']
            if len(years) != len(set(years)) or any(year > report_year for year in years):
                raise ValueError(f'Invalid operating columns: {report_year} {statement}')
            for metric, row in table['rows'].items():
                if len(row) != len(years):
                    raise ValueError(f'Invalid operating row width: {metric}')
                for year, value in zip(years, row):
                    key = (year, metric)
                    if key in values or isinstance(value, bool) or not isinstance(value, (int, float)):
                        raise ValueError(f'Duplicate or invalid operating fact: {key}')
                    values[key] = value
                    facts.append(dict(year=year, metric=metric, value=value,
                                      unit='million shares' if metric == 'closing_shares' else 'USD million',
                                      status='derived' if metric == 'opening_equity' else 'disclosed',
                                      calculation=('sum opening equity components / prior closing equity'
                                                   if metric == 'opening_equity' else None),
                                      statement=statement,
                                      source_id=source['id'], source_pdf_url=source['url'],
                                      source_pdf_sha256=source['sha256'], pdf_page=table['pdf_page'],
                                      sec_filing_date=filing['filed'], sec_filing_url=filing['url']))
    if {year for year, _ in values} != set(range(2020, 2026)):
        raise ValueError('Operating facts do not span 2020–2025')
    history_index = {(f['year'], f['metric']): f['value'] for f in history['facts']}
    statement_index = {(f['year'], f['metric']): f['value'] for f in statements['facts']}
    checks, bridges = [], []

    def control(year, metric, actual, expected):
        difference = actual - expected
        checks.append(dict(year=year, metric=metric, actual=actual, expected=expected,
                           difference=difference, status='pass' if difference == 0 else 'fail'))
        if difference:
            raise ValueError(f'Operating control failed: {metric} {year}: {difference}')

    for year in range(2020, 2026):
        v = lambda metric: values[year, metric]
        h = lambda metric, y=year: history_index[y, metric]
        s = lambda metric, y=year: statement_index[y, metric]
        control(year, 'equity_opening', v('opening_equity'), s('equity', year-1))
        control(year, 'equity_closing', v('closing_equity'), s('equity'))
        ending = (v('opening_equity') + s('net_income') + v('total_oci')
                  + v('employee_shares_equity') + v('stock_comp_and_other_equity')
                  + v('retained_earnings_other') + v('adoption_equity')
                  - v('equity_dividends') - v('equity_buybacks_authorized')
                  - v('equity_employee_treasury'))
        control(year, 'equity_rollforward', ending, v('closing_equity'))
        financing = (v('debt_issuance') - v('debt_repayment') + v('employee_option_cash')
                     - v('share_buybacks_cash') - v('employee_share_net_cash')
                     - v('dividends_cash'))
        control(year, 'financing_cash_flow', financing, s('cff'))
        opening_gross, opening_ceded = h('gross_upr', year-1), h('ceded_upr', year-1)
        gross_gap = h('gross_earned')-(h('gwp')+opening_gross-h('gross_upr'))
        ceded_gap = h('ceded_earned')-(h('ceded_written')+opening_ceded-h('ceded_upr'))
        net_gap = h('nep')-(h('nwp')+opening_gross-opening_ceded-h('net_upr'))
        control(year, 'premium_gap_basis', gross_gap-ceded_gap, net_gap)
        for metric, difference, formula in (
            ('gross_premium_earning_gap', gross_gap,
             'gross earned - (GWP + opening gross UPR - closing gross UPR)'),
            ('ceded_premium_earning_gap', ceded_gap,
             'ceded earned - (ceded written + opening ceded UPR - closing ceded UPR)'),
            ('net_premium_earning_gap', net_gap,
             'NEP - (NWP + opening net UPR - closing net UPR)'),
            ('dac_stock_gap', s('dac')-(s('dac', year-1)+v('dac_cash_additions')-s('dac_amortization')),
             'closing DAC - (opening DAC + cash-flow DAC additions - amortization)'),
            ('investment_cash_proxy_gap', s('total_investments')-s('total_investments', year-1)
             -(sum(v(m) for m in ('fixed_maturity_purchases', 'equity_security_purchases',
                                  'real_estate_purchases', 'other_investment_purchases'))
               -sum(v(m) for m in ('fixed_maturity_maturities', 'fixed_maturity_sale_proceeds',
                                   'equity_security_sale_proceeds', 'real_estate_sale_proceeds',
                                   'other_investment_sale_proceeds'))-v('short_term_net_sales')),
             'investment balance change - cash-flow net purchases proxy; proceeds are not carrying value'),
            ('debt_stock_gap', s('debt')-(s('debt', year-1)+v('debt_issuance')-v('debt_repayment')),
             'closing debt - (opening debt + cash issuance - cash repayment)')):
            bridges.append(dict(year=year, metric=metric, difference=difference,
                                formula=formula, status='open' if difference else 'zero',
                                treatment='diagnostic_only_no_balancing_entry'))
    return dict(schema_version=1, company=raw['company'], as_of=as_of,
                status='audited_equity_reconciled_other_operating_bridges_open',
                facts=sorted(facts, key=lambda fact: (fact['year'], fact['statement'], fact['metric'])),
                checks=sorted(checks, key=lambda row: (row['year'], row['metric'])),
                bridges=sorted(bridges, key=lambda row: (row['year'], row['metric'])),
                boundary='Cash proceeds are not investment disposal carrying values; DAC, UPR, investment and debt gaps are diagnostics, not forecast assumptions.')


def write_operating_movements(raw_path, inventory_path, history_path, statement_path,
                              output_path, as_of):
    paths = (raw_path, inventory_path, history_path, statement_path)
    raw, inventory, history, statements = (json.loads(Path(path).read_text()) for path in paths)
    result = build_operating_movements(raw, inventory, history, statements, as_of)
    result['input_hashes'] = {str(Path(path)): sha256(Path(path).read_bytes()).hexdigest()
                              for path in paths}
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    return result
