# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

"""Build the source-linked Travelers operating workbook with public Python packages.

The Python forecast is an independent parity oracle; Excel formulas remain live.
"""
from hashlib import sha256
import json
from pathlib import Path
import re

import xlsxwriter
from xlsxwriter.utility import xl_col_to_name


SCENARIOS = ('Base', 'Upside', 'Downside')
CELL_REFERENCE = re.compile(r'(?:(\w+)!)?(\$?[A-Z]{1,3}\$?\d+)')
DRIVERS = (
    ('gwp_growth', 'GWP growth'),
    ('ceded_share', 'Ceded written / GWP'),
    ('closing_upr_share', 'Closing gross UPR / GWP'),
    ('attritional_loss_ratio', 'Current accident-year attritional loss / NEP'),
    ('catastrophe_loss_ratio', 'Current accident-year catastrophe loss / NEP'),
    ('development_share_opening_reserves', 'Prior-year incurred / opening net reserves'),
    ('current_year_paid_share', 'Current accident-year paid / incurred'),
    ('prior_year_paid_share', 'Prior accident-year paid / opening net reserves'),
    ('unpaid_recoverable_share_gross', 'Unpaid recoverables / gross reserves'),
    ('expense_ratio', 'Illustrative underwriting expense / NEP'),
)


def build_workbook(root, destination):
    """Write a linked XLSX from normalized facts and the scenario specification."""
    root, destination = Path(root), Path(destination)
    base = root / 'examples/travelers'
    names = ('historical_actuals', 'statement_controls', 'operating_movements',
             'historical_integration', 'operating_scenarios', 'operating_forecast_reference')
    history, statements, operating, integrated, cases, reference = (
        json.loads((base / (name + '.json')).read_text()) for name in names)
    source_docs = (history, statements, operating, integrated)
    if (any(doc['company'] != 'TRV' or doc['as_of'] != '2026-02-12' for doc in source_docs)
            or cases['company'] != 'TRV' or reference['company'] != 'TRV'
            or cases['forecast_scope'] != reference['forecast_scope']
            or cases['forecast_scope'] != 'constant_fy2025_perimeter_excludes_2026_canadian_disposal'):
        raise ValueError('Workbook input issuer, cutoff or forecast scope mismatch')
    if set(cases['cases']) != set(SCENARIOS) or set(reference['cases']) != set(SCENARIOS):
        raise ValueError('Missing forecast case')
    layout = json.loads((root / 'docs/model_spec/rendered_row_map.json').read_text())['layout']
    rows = {item['id']: item['row'] for item in layout if 'id' in item}
    facts = {}
    for doc in source_docs:
        for fact in doc['facts']:
            key = (fact['year'], fact['metric'])
            if key in facts and facts[key]['value'] != fact['value']:
                raise ValueError('Conflicting source fact: %s' % (key,))
            facts.setdefault(key, fact)
    ordered = sorted(facts.values(), key=lambda fact: (fact['year'], fact['metric']))
    source_row = {(fact['year'], fact['metric']): index + 2
                  for index, fact in enumerate(ordered)}
    run_inputs = dict(history=history['input_hashes'], statements=statements['input_hashes'],
                      operating=operating['input_hashes'], integrated=integrated['input_hashes'],
                      scenarios=cases, forecast=reference)
    run_id = sha256(json.dumps(run_inputs, sort_keys=True).encode()).hexdigest()[:12]

    def col(year):
        return xl_col_to_name(year - 2019 + 6)

    def cell(year, metric):
        return '%s%d' % (col(year), rows[metric])

    def prev(year, metric):
        return cell(year - 1, metric)

    def source(year, metric):
        return 'Sources!C%d' % source_row[year, metric]

    def sums(year, metrics):
        return 'SUM(%s)' % ','.join(cell(year, metric) for metric in metrics)

    destination.parent.mkdir(parents=True, exist_ok=True)
    book = xlsxwriter.Workbook(str(destination))
    book.set_calc_mode('auto')
    navy, pale, orange = '#16324F', '#E7F0F6', '#B65A22'
    title = book.add_format({'font_name': 'Arial', 'font_size': 15, 'bold': True, 'font_color': navy})
    head = book.add_format({'font_name': 'Arial', 'font_color': 'white', 'bold': True,
                            'bg_color': navy})
    section = book.add_format({'font_name': 'Arial', 'font_color': navy, 'bold': True,
                               'bg_color': pale})
    number = book.add_format({'num_format': '#,##0.0;(#,##0.0);–', 'font_name': 'Arial'})
    actual = book.add_format({'num_format': '#,##0.0;(#,##0.0);–', 'font_name': 'Arial',
                              'font_color': '#24704A'})
    ratio = book.add_format({'num_format': '0.0%;(0.0%);–', 'font_name': 'Arial'})
    editable = book.add_format({'num_format': '0.0%;(0.0%);–', 'font_name': 'Arial',
                                'font_color': orange})
    selected = book.add_format({'bg_color': '#FFF0D9', 'font_color': orange, 'bold': True})
    sheets = {name: book.add_worksheet(name) for name in
              ('Cover', 'Summary', 'Assumptions', 'Scenarios', 'Model', 'Output', 'Sources')}
    for sheet in sheets.values():
        sheet.hide_gridlines(2)

    values, formulas = {}, {}

    def write(name, address, value, fmt=None):
        sheets[name].write(address, value, fmt)
        values[name, address] = value

    def formula(name, address, expression, fmt=None, cached=None):
        formulas[name, address] = (expression, fmt)

    sources = sheets['Sources']
    sources.set_column('A:A', 11)
    sources.set_column('B:B', 39)
    sources.set_column('C:C', 16)
    sources.set_column('D:G', 15)
    sources.set_column('H:J', 38)
    sources.freeze_panes(1, 0)
    for index, label in enumerate(('Year', 'Metric ID', 'Value', 'Status', 'Source ID',
                                   'PDF page', 'SEC filed', 'Annual report PDF',
                                   'SEC filing', 'PDF SHA-256')):
        address = '%s1' % xl_col_to_name(index)
        write('Sources', address, label, head)
    for index, fact in enumerate(ordered, 1):
        ledger_values = (fact['year'], fact['metric'], fact['value'], fact['status'],
                  fact.get('source_id', ''), fact.get('pdf_page', ''),
                  fact.get('sec_filing_date', ''), fact.get('source_pdf_url', ''),
                  fact.get('sec_filing_url', ''), fact.get('source_pdf_sha256', ''))
        for column, value in enumerate(ledger_values):
            address = '%s%d' % (xl_col_to_name(column), index + 1)
            write('Sources', address, value, number if column == 2 else None)

    model = sheets['Model']
    model.set_column('C:C', 49)
    model.set_column('D:F', 3)
    model.set_column('G:R', 14)
    model.freeze_panes(8, 7)
    write('Model', 'C2', 'Travelers P&C operating model', title)
    write('Model', 'C3', 'USD millions except shares and ratios · FY2020–25 actual · FY2026–30 illustrative')
    formula('Model', 'C4', '=Scenarios!D6')
    for year in range(2019, 2031):
        write('Model', '%s7' % col(year), year, head)
        write('Model', '%s8' % col(year), 'Opening' if year == 2019 else
              'Actual' if year <= 2025 else 'Forecast', head)
    for item in layout:
        write('Model', 'C%d' % item['row'], item.get('label', item.get('section')),
              section if 'id' not in item else None)

    def f(year, metric, expression):
        formula('Model', cell(year, metric), expression, ratio if metric == 'investment_yield' else number)

    def actual_fact(year, metric, fact_metric=None):
        key = (year, fact_metric or metric)
        if key not in source_row:
            raise ValueError('Missing source fact %s' % (key,))
        formula('Model', cell(year, metric), '=' + source(*key), actual, facts[key]['value'])

    detail_ids = ('deferred_tax_asset', 'contractholder_receivables', 'goodwill',
                  'intangible_assets', 'other_assets', 'assets_held_for_sale',
                  'contractholder_payables', 'reinsurance_premium_payables',
                  'deferred_tax_liability', 'other_liabilities',
                  'liabilities_held_for_sale', 'common_stock', 'retained_earnings',
                  'aoci', 'treasury_stock')
    control_ids = ('accrued_investment_income', 'premium_receivables',
                   'total_assets', 'balance_sheet_claim_reserves', 'total_liabilities')

    def balance(year):
        for metric in detail_ids + control_ids:
            if (year, metric) in source_row:
                actual_fact(year, metric)
        assets = ('total_investments', 'cash', 'accrued_investment_income',
                  'premium_receivables', 'total_recoverables', 'ceded_upr', 'dac',
                  'deferred_tax_asset', 'contractholder_receivables', 'goodwill',
                  'intangible_assets', 'other_assets', 'assets_held_for_sale')
        liabilities = ('balance_sheet_claim_reserves', 'gross_upr', 'debt',
                       'contractholder_payables', 'reinsurance_premium_payables',
                       'deferred_tax_liability', 'other_liabilities',
                       'liabilities_held_for_sale')
        f(year, 'balance_assets_check', '=%s-%s' % (sums(year, assets), cell(year, 'total_assets')))
        f(year, 'balance_liabilities_check', '=%s-%s' % (sums(year, liabilities), cell(year, 'total_liabilities')))
        f(year, 'balance_equity_check', '=%s-%s' %
          (sums(year, ('common_stock', 'retained_earnings', 'aoci', 'treasury_stock')),
           cell(year, 'closing_equity')))
        f(year, 'balance_equation_check', '=%s-%s-%s' %
          (cell(year, 'total_assets'), cell(year, 'total_liabilities'), cell(year, 'closing_equity')))

    stock_ids = ('gross_upr', 'ceded_upr', 'net_upr', 'net_reserves',
                 'unpaid_recoverables', 'gross_reserves', 'total_recoverables', 'dac',
                 'fixed_maturity_fair', 'equity_investments', 'real_estate_investments',
                 'short_term_investments', 'other_investments', 'total_investments',
                 'closing_equity', 'debt', 'cash')
    investments = ('fixed_maturity_fair', 'equity_investments', 'real_estate_investments',
                   'short_term_investments', 'other_investments')
    for metric in stock_ids:
        if metric == 'net_upr':
            f(2019, metric, '=%s-%s' % (cell(2019, 'gross_upr'), cell(2019, 'ceded_upr')))
        elif metric == 'gross_reserves':
            f(2019, metric, '=%s+%s' % (cell(2019, 'net_reserves'), cell(2019, 'unpaid_recoverables')))
        elif metric == 'total_investments':
            f(2019, metric, '=%s' % sums(2019, investments))
        else:
            actual_fact(2019, metric, 'equity' if metric == 'closing_equity' else metric)
    balance(2019)

    history_inputs = ('direct_written', 'assumed_written', 'ceded_written', 'gross_upr',
                      'ceded_upr', 'gross_earned', 'ceded_earned', 'current_incurred',
                      'reserve_prior_incurred', 'paid_current', 'paid_prior',
                      'reserve_fx_other', 'adoption_change', 'net_reserves',
                      'unpaid_recoverables', 'total_recoverables', 'dac',
                      'dac_cash_additions', 'dac_amortization', 'general_admin', 'claims') + investments + (
                      'investment_income', 'net_income', 'total_oci',
                      'employee_shares_equity', 'stock_comp_and_other_equity',
                      'retained_earnings_other', 'adoption_equity', 'equity_dividends',
                      'equity_buybacks_authorized', 'equity_employee_treasury',
                      'closing_equity', 'closing_shares', 'debt', 'debt_issuance',
                      'debt_repayment', 'cfo', 'cfi', 'cff', 'cash_fx', 'cash')
    for year in range(2020, 2026):
        c = lambda metric: cell(year, metric)
        p = lambda metric: prev(year, metric)
        for metric in history_inputs:
            actual_fact(year, metric)
        f(year, 'opening_equity', '=' + p('closing_equity'))
        if year == 2025:
            for metric in ('held_for_sale_upr', 'held_for_sale_recoverables',
                           'cash_held_for_sale_reclassification'):
                actual_fact(year, metric)
        expressions = {
            'gwp': '=%s+%s' % (c('direct_written'), c('assumed_written')),
            'nwp': '=%s-%s' % (c('gwp'), c('ceded_written')),
            'net_upr': '=%s-%s' % (c('gross_upr'), c('ceded_upr')),
            'nep': '=%s-%s' % (c('gross_earned'), c('ceded_earned')),
            'gross_premium_earning_gap': '=%s-(%s+%s-%s)' %
                (c('gross_earned'), c('gwp'), p('gross_upr'), c('gross_upr')),
            'ceded_premium_earning_gap': '=%s-(%s+%s-%s)' %
                (c('ceded_earned'), c('ceded_written'), p('ceded_upr'), c('ceded_upr')),
            'net_premium_earning_gap': '=%s-%s' %
                (c('gross_premium_earning_gap'), c('ceded_premium_earning_gap')),
            'reported_total_incurred': '=%s+%s' %
                (c('current_incurred'), c('reserve_prior_incurred')),
            'reported_total_paid': '=%s+%s' % (c('paid_current'), c('paid_prior')),
            'gross_reserves': '=%s+%s' % (c('net_reserves'), c('unpaid_recoverables')),
            'reserve_rollforward_check': '=%s+%s+%s-%s+%s-%s' %
                (p('net_reserves'), c('adoption_change'), c('reported_total_incurred'),
                 c('reported_total_paid'), c('reserve_fx_other'), c('net_reserves')),
            'recoverable_scope_difference': '=%s-%s' %
                (c('total_recoverables'), c('unpaid_recoverables')),
            'dac_stock_gap': '=%s-(%s+%s-%s)' %
                (c('dac'), p('dac'), c('dac_cash_additions'), c('dac_amortization')),
            'total_investments': '=%s' % sums(year, investments),
            'investment_cash_purchases': '=SUM(%s)' % ','.join(source(year, metric) for metric in (
                'fixed_maturity_purchases', 'equity_security_purchases',
                'real_estate_purchases', 'other_investment_purchases')),
            'investment_cash_proceeds': '=SUM(%s)' % ','.join(source(year, metric) for metric in (
                'fixed_maturity_maturities', 'fixed_maturity_sale_proceeds',
                'equity_security_sale_proceeds', 'real_estate_sale_proceeds',
                'other_investment_sale_proceeds')),
            'investment_cash_proxy_gap': '=%s-%s-(%s-%s-%s)' %
                (c('total_investments'), p('total_investments'),
                 c('investment_cash_purchases'), c('investment_cash_proceeds'),
                 c('short_term_net_sales')),
            'average_investments': '=(%s+%s)/2' %
                (c('total_investments'), p('total_investments')),
            'investment_yield': '=%s/%s' % (c('investment_income'), c('average_investments')),
            'equity_rollforward_check': '=%s+%s-%s-%s' %
                (c('opening_equity'), sums(year, ('net_income', 'total_oci',
                 'employee_shares_equity', 'stock_comp_and_other_equity',
                 'retained_earnings_other', 'adoption_equity')),
                 sums(year, ('equity_dividends', 'equity_buybacks_authorized',
                 'equity_employee_treasury')), c('closing_equity')),
            'debt_stock_gap': '=%s-(%s+%s-%s)' %
                (c('debt'), p('debt'), c('debt_issuance'), c('debt_repayment')),
            'cash_rollforward_check': '=%s+%s%s-%s' %
                (p('cash'), sums(year, ('cfo', 'cfi', 'cff', 'cash_fx')),
                 '-' + c('cash_held_for_sale_reclassification') if year == 2025 else '', c('cash')),
            'total_revenue': '=%s' % sums(year, ('nep', 'investment_income', 'fee_income',
                                                 'realized_gains', 'other_revenue')),
            'total_expenses': '=%s' % sums(year, ('claims', 'dac_amortization',
                                                  'general_admin', 'interest_expense')),
            'pretax_income': '=%s-%s' % (c('total_revenue'), c('total_expenses')),
            'income_revenue_check': '=%s-%s' % (c('total_revenue'), source(year, 'total_revenue')),
            'income_expense_check': '=%s-%s' % (c('total_expenses'), source(year, 'total_expenses')),
            'income_net_check': '=%s-%s-%s' %
                (c('pretax_income'), c('tax_expense'), c('net_income')),
            'income_cash_check': '=%s-%s' % (c('net_income'), source(year, 'cash_flow_net_income')),
        }
        actual_fact(year, 'short_term_net_sales')
        for metric in ('fee_income', 'realized_gains', 'other_revenue',
                       'interest_expense', 'tax_expense'):
            actual_fact(year, metric)
        for metric, expression in expressions.items():
            f(year, metric, expression)
        balance(year)

    scenarios = sheets['Scenarios']
    scenarios.set_column('C:C', 87)
    scenarios.set_column('D:D', 18)
    write('Scenarios', 'C2', 'Forecast scenario', title)
    write('Scenarios', 'C6', 'Selected case')
    write('Scenarios', 'D6', 'Base', selected)
    scenarios.data_validation('D6', {'validate': 'list', 'source': list(SCENARIOS)})
    write('Scenarios', 'C9', 'Base, upside and downside are illustrative analyst inputs. Changing D6 updates the same forecast schedules.')
    write('Scenarios', 'C10', 'Forecast holds the FY2025 operating perimeter constant; the January 2026 Canadian sale is not reflected.')

    assumptions = sheets['Assumptions']
    assumptions.set_column('C:C', 53)
    assumptions.set_column('D:M', 3)
    assumptions.set_column('N:R', 14)
    write('Assumptions', 'C2', 'Illustrative P&C forecast drivers', title)
    write('Assumptions', 'C3', 'Analyst scenarios; not Travelers guidance or a valuation forecast')
    formula('Assumptions', 'C5', '=Scenarios!D6')
    for year in range(2026, 2031):
        write('Assumptions', '%s7' % col(year), year, head)
    driver_rows = {}
    for index, (driver, label) in enumerate(DRIVERS):
        row = 9 + index * 5
        driver_rows[driver] = row
        write('Assumptions', 'C%d' % row, label, section)
        for offset, name in enumerate(SCENARIOS, 1):
            value = cases['cases'][name][driver]
            if not isinstance(value, (int, float)):
                raise ValueError('Missing driver %s %s' % (name, driver))
            write('Assumptions', 'C%d' % (row + offset), name)
            for year in range(2026, 2031):
                write('Assumptions', '%s%d' % (col(year), row + offset), value, editable)
        for year in range(2026, 2031):
            c = col(year)
            formula('Assumptions', '%s%d' % (c, row),
                    '=IF(Scenarios!$D$6="Base",%s%d,IF(Scenarios!$D$6="Upside",%s%d,%s%d))' %
                    (c, row + 1, c, row + 2, c, row + 3), ratio)

    for year in range(2026, 2031):
        c = lambda metric: cell(year, metric)
        p = lambda metric: prev(year, metric)
        a = lambda driver: 'Assumptions!%s%d' % (col(year), driver_rows[driver])
        forecast = {
            'gwp': '=%s*(1+%s)' % (p('gwp'), a('gwp_growth')),
            'ceded_written': '=%s*%s' % (c('gwp'), a('ceded_share')),
            'nwp': '=%s-%s' % (c('gwp'), c('ceded_written')),
            'gross_upr': '=%s*%s' % (c('gwp'), a('closing_upr_share')),
            'ceded_upr': '=%s*%s' % (c('ceded_written'), a('closing_upr_share')),
            'net_upr': '=%s-%s' % (c('gross_upr'), c('ceded_upr')),
            'gross_earned': '=%s+%s-%s' % (c('gwp'), p('gross_upr'), c('gross_upr')),
            'ceded_earned': '=%s+%s-%s' % (c('ceded_written'), p('ceded_upr'), c('ceded_upr')),
            'nep': '=%s-%s' % (c('gross_earned'), c('ceded_earned')),
            'current_incurred': '=%s*(%s+%s)' %
                (c('nep'), a('attritional_loss_ratio'), a('catastrophe_loss_ratio')),
            'reserve_prior_incurred': '=%s*%s' %
                (p('net_reserves'), a('development_share_opening_reserves')),
            'reported_total_incurred': '=%s+%s' %
                (c('current_incurred'), c('reserve_prior_incurred')),
            'paid_current': '=%s*%s' % (c('current_incurred'), a('current_year_paid_share')),
            'paid_prior': '=%s*%s' % (p('net_reserves'), a('prior_year_paid_share')),
            'reported_total_paid': '=%s+%s' % (c('paid_current'), c('paid_prior')),
            'net_reserves': '=%s+%s-%s' %
                (p('net_reserves'), c('reported_total_incurred'), c('reported_total_paid')),
            'unpaid_recoverables': '=%s*%s/(1-%s)' %
                (c('net_reserves'), a('unpaid_recoverable_share_gross'),
                 a('unpaid_recoverable_share_gross')),
            'gross_reserves': '=%s+%s' % (c('net_reserves'), c('unpaid_recoverables')),
            'reserve_rollforward_check': '=%s+%s-%s-%s' %
                (p('net_reserves'), c('reported_total_incurred'),
                 c('reported_total_paid'), c('net_reserves')),
            'underwriting_expense_proxy': '=%s*%s' % (c('nep'), a('expense_ratio')),
        }
        for metric, expression in forecast.items():
            f(year, metric, expression)

    summary = sheets['Summary']
    summary.set_column('C:C', 43)
    summary.set_column('D:F', 3)
    summary.set_column('G:R', 14)
    write('Summary', 'C2', 'Travelers operating history and illustrative outlook', title)
    write('Summary', 'C3', 'Actuals: 2020–2025 · forecast: 2026–2030 · USD millions')
    formula('Summary', 'C5', '=Scenarios!D6')
    for year in range(2019, 2031):
        write('Summary', '%s7' % col(year), year, head)
    summary_rows = (('Gross written premiums', 'gwp'), ('Net written premiums', 'nwp'),
                    ('Net earned premiums', 'nep'), ('Net P&C claims reserves', 'net_reserves'),
                    ('P&C reserve-table incurred', 'reported_total_incurred'),
                    ('Illustrative underwriting expense', 'underwriting_expense_proxy'),
                    ('Illustrative combined ratio', None),
                    ('Total investments', 'total_investments'),
                    ('Net investment income', 'investment_income'),
                    ('Common equity', 'closing_equity'), ('Net income', 'net_income'),
                    ('Closing cash', 'cash'))
    forecast_metrics = {'gwp', 'nwp', 'nep', 'net_reserves',
                        'reported_total_incurred', 'underwriting_expense_proxy'}
    for row, (label, metric) in enumerate(summary_rows, 9):
        write('Summary', 'C%d' % row, label)
        for year in range(2019, 2031):
            available = (metric in {'net_reserves', 'total_investments', 'closing_equity', 'cash'}
                         if year == 2019 else metric is not None and
                         metric != 'underwriting_expense_proxy' if year <= 2025 else
                         metric in forecast_metrics)
            if available:
                formula('Summary', '%s%d' % (col(year), row), '=Model!' + cell(year, metric), number)
            elif metric is None and year >= 2026:
                formula('Summary', '%s%d' % (col(year), row),
                        '=(Model!%s+Model!%s)/Model!%s' %
                        (cell(year, 'reported_total_incurred'),
                         cell(year, 'underwriting_expense_proxy'), cell(year, 'nep')), ratio)
    write('Summary', 'C23', 'Illustrative forecast excludes the January 2026 Canadian sale; investment income, equity, cash and valuation remain unmodeled.')
    write('Summary', 'C25', 'Master Check', section)
    open_terms = ['ABS(Model!%s)' % cell(year, metric)
                  for metric in ('net_premium_earning_gap', 'dac_stock_gap',
                                 'investment_cash_proxy_gap', 'debt_stock_gap')
                  for year in range(2020, 2026)]
    formula('Summary', 'M25', '=IF(SUM(%s)>0.01,"OPEN: historical stock bridges","PASS")' %
            ','.join(open_terms), section, 'OPEN: historical stock bridges')
    summary.conditional_format('M25', {'type': 'text', 'criteria': 'containing',
                                        'value': 'OPEN', 'format': book.add_format({
                                            'bg_color': '#FDE8E7', 'font_color': '#B42318',
                                            'bold': True})})

    cover = sheets['Cover']
    cover.set_column('C:C', 73)
    cover.set_column('D:D', 54)
    for address, value in (
        ('C3', 'The Travelers Companies'), ('C4', 'P&C operating model'),
        ('C6', 'Fiscal 2020–2025 actuals · 2019 opening · 2026–2030 illustrative forecast'),
        ('C8', 'Information cutoff'), ('D8', '2026-02-12'), ('C9', 'Status'),
        ('D9', 'Integrated historical statements; forecast and valuation pending'),
        ('C10', 'Input fingerprint'), ('D10', run_id),
        ('C11', 'Historical detail uses annual-report PDFs and filing dates; selected SEC rows have independent parity checks.'),
        ('C12', '2026 forecast is illustrative and excludes the January 2 Canadian disposal.')):
        write('Cover', address, value, title if address == 'C3' else None)

    output = sheets['Output']
    output.set_column('C:C', 32)
    output.set_column('D:D', 76)
    write('Output', 'C2', 'Research output status', title)
    for address, value in (
        ('C5', 'Price target'), ('D5', 'Pending integrated forecast and market input review'),
        ('C7', 'Historical controls'),
        ('D7', 'Premium, reserve, audited income, balance sheet, cash, equity and financing checks'),
        ('C8', 'Open work'),
        ('D8', 'Canada disposal perimeter; UPR/DAC/investment/debt bridges; forecast statements'),
        ('C9', 'Forecast scope'),
        ('D9', 'Illustrative constant FY2025 perimeter; excludes January 2, 2026 Canadian sale'),
        ('C10', 'Scenario result'), ('C11', '2030 net earned premiums'),
        ('C12', '2030 net P&C reserves'), ('C13', '2030 illustrative combined ratio'),
        ('C14', 'Historical bridge status')):
        write('Output', address, value)
    formula('Output', 'D10', '=Scenarios!D6')
    formula('Output', 'D11', '=Model!' + cell(2030, 'nep'), number)
    formula('Output', 'D12', '=Model!' + cell(2030, 'net_reserves'), number)
    formula('Output', 'D13', '=Summary!R15', ratio)
    formula('Output', 'D14', '=Summary!M25')
    def evaluate(case, overrides=None):
        """Evaluate the supported, generated formula grammar for saved Excel caches.

        Excel remains the live calculation engine after a user changes a cell.
        """
        memo = {}
        overrides = overrides or {}

        def ref(sheet, address):
            key = sheet, address.replace('$', '')
            if key == ('Scenarios', 'D6'):
                return case
            if key in overrides:
                return overrides[key]
            if key in memo:
                return memo[key]
            if key in values:
                return values[key]
            if key not in formulas:
                return 0
            expression = formulas[key][0][1:]
            expression = CELL_REFERENCE.sub(
                lambda match: 'REF(%r,%r)' % (match.group(1) or sheet,
                                                match.group(2).replace('$', '')),
                expression)
            expression = re.sub(r'(?<![<>=])=(?!=)', '==', expression)
            result = eval(expression, {'__builtins__': {}}, {
                'REF': ref, 'SUM': lambda *args: sum(args), 'ABS': abs,
                'IF': lambda condition, yes, no: yes if condition else no})
            memo[key] = result
            return result

        return ref

    base_value = evaluate('Base')
    for case in SCENARIOS:
        value = evaluate(case)
        for index, year in enumerate(range(2026, 2031)):
            expected = reference['cases'][case][index]
            pairs = (
                ('gwp', expected['premiums']['gwp']),
                ('nwp', expected['premiums']['nwp']),
                ('nep', expected['premiums']['nep']),
                ('net_upr', expected['premiums']['closing_net_upr']),
                ('reported_total_incurred', expected['reserves']['incurred_net']),
                ('reported_total_paid', expected['reserves']['paid_net']),
                ('net_reserves', expected['reserves']['closing_net']),
                ('gross_reserves', expected['reserves']['closing_gross']),
                ('underwriting_expense_proxy', expected['underwriting_expenses']),
            )
            for metric, target in pairs:
                result = value('Model', cell(year, metric))
                if abs(result - target) > 1e-9 * max(1, abs(target)):
                    raise ValueError('Python/Excel formula parity failed: %s %d %s' %
                                     (case, year, metric))
        for year in range(2019, 2026):
            for metric in ('balance_assets_check', 'balance_liabilities_check',
                           'balance_equity_check', 'balance_equation_check'):
                if abs(value('Model', cell(year, metric))) > 0.01:
                    raise ValueError('Historical balance check failed: %d %s' % (year, metric))
            if year >= 2020:
                for metric in ('income_revenue_check', 'income_expense_check',
                               'income_net_check', 'income_cash_check',
                               'reserve_rollforward_check', 'equity_rollforward_check'):
                    if abs(value('Model', cell(year, metric))) > 0.01:
                        raise ValueError('Historical control failed: %d %s' % (year, metric))
        if value('Model', cell(2025, 'net_premium_earning_gap')) != -412 or \
                value('Model', cell(2025, 'dac_stock_gap')) != -83 or \
                value('Summary', 'M25') != 'OPEN: historical stock bridges':
            raise ValueError('Open historical stock bridges were not preserved')

    changed = evaluate('Base', {('Assumptions', '%s%d' %
                                 (col(2028), driver_rows['gwp_growth'])): 0.10})
    if (changed('Output', 'D11') <= base_value('Output', 'D11') or
            changed('Model', cell(2025, 'nep')) != base_value('Model', cell(2025, 'nep'))):
        raise ValueError('An assumption change did not flow to output cleanly')
    if (evaluate('Upside')('Output', 'D11') == base_value('Output', 'D11') or
            evaluate('Downside')('Output', 'D11') == base_value('Output', 'D11')):
        raise ValueError('Scenario selection did not flow to output')

    for (name, address), (expression, fmt) in formulas.items():
        sheets[name].write_formula(address, expression, fmt, base_value(name, address))
    book.close()
    return destination
