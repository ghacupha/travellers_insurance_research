"""P&C workbook/data contract. No financial estimates are created here."""
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Metric:
    id: str
    label: str
    section: str
    source_group: str
    basis: str = 'consolidated_gaap'
    period_type: str = 'duration'
    unit: str = 'USD million'
    segment_detail: bool = False
    actual_key: str = ''
    equation: str = ''


def metric_catalog():
    """Stable semantic IDs; renderer row coordinates are generated, never imported."""
    result = []

    def add(section, source, rows, **defaults):
        for key, label, options in rows:
            settings = dict(defaults, **options)
            source_group = settings.pop('source_group', source)
            result.append(Metric(key, label, section, source_group, **settings))

    add('Premiums', 'earned_reinsurance', [
        ('direct_written','Direct written premiums',dict(basis='direct')),
        ('assumed_written','Assumed written premiums',dict(basis='assumed')),
        ('gwp','Gross written premiums',dict(basis='gross',equation='direct_written + assumed_written')),
        ('ceded_written','Ceded written premiums',dict(basis='ceded')),
        ('nwp','Net written premiums',dict(basis='net',actual_key='nwp',equation='gwp - ceded_written')),
        ('gross_upr','Gross unearned premium reserve',dict(basis='gross',period_type='instant',source_group='balance_sheet')),
        ('ceded_upr','Ceded unearned premiums',dict(basis='ceded',period_type='instant',source_group='balance_sheet')),
        ('net_upr','Net unearned premium reserve',dict(basis='net',period_type='instant',source_group='balance_sheet',equation='gross_upr - ceded_upr')),
        ('held_for_sale_upr','Gross unearned premium reserves classified as held for sale',dict(basis='gross',period_type='instant',source_group='held_for_sale')),
        ('gross_upr_other_change','Gross UPR FX/transfers/other earning movements',dict(basis='gross')),
        ('ceded_upr_other_change','Ceded UPR FX/transfers/other earning movements',dict(basis='ceded')),
        ('gross_earned','Gross earned premiums',dict(basis='gross',equation='gwp + opening_gross_upr - gross_upr + gross_upr_other_change')),
        ('ceded_earned','Ceded earned premiums',dict(basis='ceded',equation='ceded_written + opening_ceded_upr - ceded_upr + ceded_upr_other_change')),
        ('nep','Net earned premiums',dict(basis='net',actual_key='nep',equation='gross_earned - ceded_earned')),
        ('upr_other_change','Net UPR FX/transfers/other earning movements',dict(basis='net',equation='gross_upr_other_change - ceded_upr_other_change')),
    ], segment_detail=True)
    add('Claims and reserves', 'claims_rollforward', [
        ('gross_reserves','Gross P&C loss and LAE reserves before held-for-sale presentation',dict(basis='gross',period_type='instant')),
        ('unpaid_recoverables','Recoverables on unpaid P&C losses (reserve-table basis)',dict(basis='ceded',period_type='instant')),
        ('net_reserves','Net P&C loss and LAE reserves',dict(period_type='instant',equation='gross_reserves - unpaid_recoverables')),
        ('current_incurred','Current accident-year losses and LAE incurred',{}),
        ('reserve_prior_incurred','Prior accident-year incurred adjustment in reserve rollforward',{}),
        ('reserve_total_incurred','Total P&C incurred in reserve rollforward',dict(equation='current_incurred + reserve_prior_incurred')),
        ('paid_current','Paid losses and LAE for current accident year',{}),
        ('paid_prior','Paid losses and LAE for prior accident years',{}),
        ('reserve_fx_other','Reserve FX/acquisition/other movements',{}),
        ('catastrophes','Reported catastrophe losses, net of reinsurance',dict(actual_key='catastrophe_losses',source_group='written_premiums')),
        ('reported_development','Reported prior-year development used in underwriting ratios',dict(actual_key='prior_year_development',source_group='written_premiums')),
        ('discount_accretion','Accretion of claims-reserve discount',{}),
    ], basis='net', segment_detail=True)
    add('Reinsurance and presentation bridges', 'recoverables', [
        ('total_recoverables','Balance-sheet reinsurance recoverables net of allowance',dict(period_type='instant')),
        ('paid_recoverables','Recoverables on paid losses',dict(period_type='instant')),
        ('reinsurance_allowance','Allowance for uncollectible reinsurance',dict(period_type='instant')),
        ('reinsurance_collections','Cash collected from reinsurers',{}),
        ('held_for_sale_reserves','Claims reserves classified as held for sale',dict(period_type='instant',source_group='held_for_sale')),
        ('other_insurance_reserves','Accident/health and other claims reserves outside P&C rollforward',dict(period_type='instant',source_group='claims_rollforward')),
        ('balance_sheet_claim_reserves','Reported balance-sheet claims and LAE reserves',dict(period_type='instant',source_group='balance_sheet')),
        ('held_for_sale_recoverables','Recoverables classified as held for sale',dict(period_type='instant',source_group='held_for_sale')),
    ])
    add('Expenses and underwriting ratios', 'dac', [
        ('dac','Deferred acquisition costs',dict(period_type='instant')),
        ('dac_additions','Capitalized acquisition costs',{}),
        ('dac_amortization','Amortization of deferred acquisition costs',dict(actual_key='dac_amortization')),
        ('dac_other','DAC FX/transfers/other movements',{}),
        ('general_admin','General and administrative expenses',dict(actual_key='general_admin')),
        ('claims','GAAP claims and claim adjustment expense line',dict(actual_key='claims',source_group='income_statement')),
        ('policyholder_dividends','Policyholder dividends',dict(actual_key='policyholder_dividends',source_group='ratio_bridge')),
        ('loss_allocated_fees','Fees allocated against loss-ratio numerator',dict(actual_key='loss_allocated_fees',source_group='ratio_bridge')),
        ('expense_allocated_fees','Fees allocated against expense-ratio numerator',dict(actual_key='expense_allocated_fees',source_group='ratio_bridge')),
        ('noninsurance_admin','Non-insurance G&A excluded from expense ratio',dict(actual_key='noninsurance_admin',source_group='ratio_bridge')),
        ('billing_fees_other','Billing/policy fees and other ratio adjustments',dict(actual_key='billing_fees_other',source_group='ratio_bridge')),
        ('reported_loss_ratio','Reported loss and LAE ratio',dict(actual_key='reported_loss_ratio',unit='fraction',period_type='ratio',source_group='ratio_bridge')),
        ('reported_expense_ratio','Reported underwriting expense ratio',dict(actual_key='reported_expense_ratio',unit='fraction',period_type='ratio',source_group='ratio_bridge')),
        ('reported_combined_ratio','Reported combined ratio',dict(actual_key='reported_combined_ratio',unit='fraction',period_type='ratio',source_group='ratio_bridge')),
        ('underlying_combined_ratio','Reported underlying combined ratio',dict(unit='fraction',period_type='ratio',source_group='ratio_bridge')),
    ])
    add('Investments', 'investments', [
        ('fixed_maturity_cost','Fixed maturities at amortized cost',dict(period_type='instant',basis='amortized_cost')),
        ('fixed_maturity_fair','Fixed maturities at fair value',dict(period_type='instant',basis='fair_value')),
        ('equity_investments','Equity securities',dict(period_type='instant',basis='fair_value')),
        ('short_term_investments','Short-term investments',dict(period_type='instant')),
        ('other_investments','Real estate and other investments (separate child classes)',dict(period_type='instant')),
        ('investment_purchases','Investment purchases',dict(source_group='cash_flow')),
        ('investment_sales','Investment sale proceeds',dict(source_group='cash_flow')),
        ('investment_maturities','Investment maturity proceeds',dict(source_group='cash_flow')),
        ('investment_disposal_carrying','Carrying value of investments disposed',{}),
        ('investment_income','Net investment income',dict(source_group='income_statement',segment_detail=True)),
        ('realized_gains','Net realized investment gains/losses',dict(source_group='income_statement')),
        ('investment_oci','Investment-related OCI, after tax',dict(source_group='equity')),
        ('investment_yield','Net investment yield on defined average asset basis',dict(unit='fraction',period_type='ratio')),
    ])
    add('Tax and debt', 'tax', [
        ('tax_expense','Total income tax expense',dict(source_group='income_statement')),
        ('current_tax','Current income tax expense',{}),
        ('deferred_tax','Deferred income tax expense',{}),
        ('deferred_tax_balance','Deferred tax assets/liabilities, net',dict(period_type='instant')),
        ('cash_tax','Income taxes paid',dict(source_group='cash_flow')),
        ('debt','Debt outstanding',dict(period_type='instant',source_group='balance_sheet')),
        ('debt_issuance','Debt issuance proceeds',dict(source_group='cash_flow')),
        ('debt_repayment','Debt principal repaid',dict(source_group='cash_flow')),
        ('interest_expense','Interest expense',dict(source_group='income_statement')),
    ])
    add('Equity and capital', 'equity', [
        ('equity','Common shareholders equity',dict(period_type='instant')),
        ('total_oci','Total other comprehensive income',{}),
        ('aoci','Accumulated other comprehensive income',dict(period_type='instant')),
        ('dividends','Common dividends',{}),
        ('buybacks','Share repurchases (authorization and employee separately)',{}),
        ('share_issuance','Share issuance and share-based compensation equity movements',{}),
        ('closing_shares','Period-end common shares',dict(period_type='instant',unit='million shares')),
        ('diluted_shares','Diluted weighted-average shares',dict(unit='million shares',source_group='income_statement')),
        ('statutory_surplus','Statutory capital and surplus (specified legal entity scope)',dict(period_type='instant',source_group='statutory',basis='statutory')),
    ])
    add('Statements and cash integration', 'balance_sheet', [
        ('cash','Cash including restricted cash, balance-sheet presentation',dict(period_type='instant')),
        ('premium_receivables','Premium receivables',dict(period_type='instant')),
        ('accrued_investment_income','Investment income accrued',dict(period_type='instant')),
        ('other_assets','Other assets with disclosed child lines',dict(period_type='instant')),
        ('other_liabilities','Other liabilities with disclosed child lines',dict(period_type='instant')),
        ('total_assets','Reported total assets control',dict(period_type='instant')),
        ('total_liabilities','Reported total liabilities control',dict(period_type='instant')),
        ('net_income','Net income',dict(source_group='income_statement')),
        ('fee_other_income','Fee and other revenue (disclosed child lines)',dict(source_group='income_statement')),
        ('cfo','Cash flow from operations',dict(source_group='cash_flow')),
        ('cfi','Cash flow from investing',dict(source_group='cash_flow')),
        ('cff','Cash flow from financing',dict(source_group='cash_flow')),
        ('cash_fx','Exchange-rate effect on cash',dict(source_group='cash_flow')),
        ('cash_flow_closing','Cash/restricted cash at end of cash-flow statement',dict(period_type='instant',source_group='cash_flow')),
    ])
    return result


def excel_column(number):
    text = ''
    while number:
        number, remainder = divmod(number-1, 26)
        text = chr(65+remainder)+text
    return text


def workbook_contract(actual_years, forecast_years):
    years = list(actual_years)+list(forecast_years)
    if not actual_years or not forecast_years or years != list(range(years[0], years[-1]+1)):
        raise ValueError('Actual and forecast years must be nonempty, ordered and consecutive')
    rows, row_number, last_section = [], 28, None
    for metric in metric_catalog():
        if metric.section != last_section:
            row_number += 3
            last_section = metric.section
        rows.append(dict(asdict(metric), sheet='Model', row=row_number,
                         opening_required=metric.period_type=='instant'))
        row_number += 1
    return dict(schema_version=1, status='specification_not_rendered_model',
                tabs=['Cover','Summary','Assumptions','Scenarios','Model','Output','Sources'],
                actual_years=list(actual_years),forecast_years=list(forecast_years),
                opening_year=actual_years[0]-1, opening_column='G',
                period_columns={str(year):excel_column(8+i) for i,year in enumerate(years)},
                scenario_selector='Scenarios!D6', rows=rows,
                segment_policy='Repeat requested metrics in blocks after consolidated schedules; disclose gaps, never allocate by invented shares',
                boundary='Coordinates reserve primary metric rows; add opening/movement/check child rows through a versioned renderer mapping before formula authoring')
