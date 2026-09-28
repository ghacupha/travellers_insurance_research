# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

"""Normalize transcribed P&C history and expose every reconciliation residual."""
from collections import Counter
from datetime import date
from hashlib import sha256
import json
from pathlib import Path

from .schedules import ReserveInputs, reserves


PREMIUM_ROWS = ('direct_written', 'assumed_written', 'ceded_written', 'reported_nwp',
                'direct_earned', 'assumed_earned', 'ceded_earned', 'reported_nep')
RESERVE_ROWS = ('opening_gross', 'opening_unpaid_recoverables', 'adoption_change',
                'reported_opening_net_after_adoption', 'current_incurred',
                'reserve_prior_incurred', 'reported_total_incurred', 'paid_current',
                'paid_prior', 'reported_total_paid', 'reserve_fx_other', 'closing_net',
                'closing_unpaid_recoverables', 'closing_gross')


def _fact(year, metric, value, source, page, row, table, kind='disclosed', filing=None):
    return dict(year=year, metric=metric, value=value, unit='USD million', scope='consolidated',
                status=kind, source_id=source['id'], source_pdf_url=source['url'],
                source_pdf_sha256=source['sha256'], pdf_page=page, table=table, row=row,
                sec_filing_accession=filing['accession'], sec_filing_date=filing['filed'],
                sec_filing_url=filing['url'],
                cutoff_status='filing_date_verified_pdf_copy_row_parity_pending')


def build_history(raw, inventory, as_of, release_actuals=None):
    """Check provenance and identities; missing earning movements remain open issues."""
    date.fromisoformat(as_of)
    if raw['company'] != inventory['company'] or raw['unit'] != 'USD million':
        raise ValueError('Issuer or unit mismatch')
    sources = {s['fiscal_year']: s for s in inventory['sources']}
    if len(sources) != len(inventory['sources']):
        raise ValueError('Duplicate source report year')
    for year, filing in raw['filings'].items():
        if int(year) not in sources or date.fromisoformat(filing['filed']) > date.fromisoformat(as_of):
            raise ValueError(f'Filing unavailable at cutoff: {year}')
        if filing['accession'].replace('-', '') not in filing['url']:
            raise ValueError(f'Filing URL and accession mismatch: {year}')
    facts, checks, issues = [], [], []
    seen = set()

    def add(year, metric, value, report_year, page, row, table, kind='disclosed'):
        key = (year, metric)
        if key in seen:
            raise ValueError(f'Duplicate historical fact: {key}')
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f'Non-numeric historical fact: {key}')
        source = sources[report_year]
        if report_year < year or raw['filings'][str(report_year)]['filed'] > as_of:
            raise ValueError(f'Source not eligible: {key}')
        group = {'premium': 'earned_reinsurance', 'upr': 'balance_sheet',
                 'balance_sheet': 'balance_sheet',
                 'reserve': 'claims_rollforward', 'held_for_sale': 'held_for_sale'}[table]
        if source['reviewed_tables'][group]['pdf_page'] != page:
            raise ValueError(f'Page does not match reviewed table: {key}')
        seen.add(key)
        facts.append(_fact(year, metric, value, source, page, row, table, kind,
                           raw['filings'][str(report_year)]))

    def check(year, name, actual, expected):
        difference = actual-expected
        checks.append(dict(year=year, check=name, actual=actual, expected=expected,
                           difference=difference, status='pass' if difference == 0 else 'fail'))
        if difference != 0:
            raise ValueError(f'{name} mismatch in {year}: {difference}')

    premiums = {}
    for table in raw['premium_tables']:
        years = table['columns']
        if len(years) != len(set(years)) or set(table['rows']) != set(PREMIUM_ROWS):
            raise ValueError('Premium table columns or rows invalid')
        for row in PREMIUM_ROWS:
            values = table['rows'][row]
            if len(values) != len(years):
                raise ValueError(f'Premium row width invalid: {row}')
            for year, value in zip(years, values):
                if year in premiums and row in premiums[year]:
                    raise ValueError(f'Duplicate premium year/row: {year} {row}')
                premiums.setdefault(year, {})[row] = value
                if row not in ('reported_nwp', 'reported_nep'):
                    add(year, row, value, table['report_year'], table['pdf_page'], row, 'premium')
        for year in years:
            p = premiums[year]
            check(year, 'written_premium', p['direct_written']+p['assumed_written']-p['ceded_written'], p['reported_nwp'])
            check(year, 'earned_premium', p['direct_earned']+p['assumed_earned']-p['ceded_earned'], p['reported_nep'])
            add(year, 'gwp', p['direct_written']+p['assumed_written'], table['report_year'], table['pdf_page'],
                'direct_written + assumed_written', 'premium', 'derived')
            add(year, 'nwp', p['reported_nwp'], table['report_year'], table['pdf_page'], 'reported_nwp', 'premium')
            add(year, 'gross_earned', p['direct_earned']+p['assumed_earned'], table['report_year'], table['pdf_page'],
                'direct_earned + assumed_earned', 'premium', 'derived')
            add(year, 'nep', p['reported_nep'], table['report_year'], table['pdf_page'], 'reported_nep', 'premium')

    if release_actuals is not None:
        if release_actuals['company']['ticker'] != raw['company']:
            raise ValueError('Release issuer mismatch')
        for period in release_actuals['periods']:
            year = period['year']
            if year not in premiums:
                continue
            for key, source_key in (('nwp', 'reported_nwp'), ('nep', 'reported_nep')):
                release_fact = period['facts'][key]
                release_source = release_actuals['sources'][release_fact['source_id']]
                if release_source['published'] <= as_of:
                    check(year, f'{key}_to_independent_earnings_release',
                          premiums[year][source_key], release_fact['value'])

    upr = {}
    for table in raw['upr_balance_tables']:
        year = table['year']
        if year in upr or table['report_year'] != year:
            raise ValueError(f'Duplicate/non-original UPR stock: {year}')
        if table['gross_upr'] < table['ceded_upr'] or table['ceded_upr'] < 0:
            raise ValueError(f'Invalid gross/ceded UPR stock: {year}')
        upr[year] = table
        for row in ('gross_upr', 'ceded_upr'):
            add(year, row, table[row], table['report_year'], table['pdf_page'], row, 'upr')
        add(year, 'net_upr', table['gross_upr']-table['ceded_upr'], table['report_year'],
            table['pdf_page'], 'gross_upr - ceded_upr', 'upr', 'derived')

    held_for_sale = raw['held_for_sale_2025']
    hfs_year = held_for_sale['report_year']
    for row, metric in (('unearned_premium_reserves', 'held_for_sale_upr'),
                        ('claims_reserves', 'held_for_sale_reserves'),
                        ('reinsurance_recoverables', 'held_for_sale_recoverables')):
        add(2025, metric, held_for_sale[row], hfs_year, held_for_sale['pdf_page'], row, 'held_for_sale')
    presentation = raw['reserve_presentation_2025']
    add(2025, 'other_insurance_reserves', presentation['other_insurance_claim_reserves'],
        presentation['report_year'], presentation['reserve_pdf_page'],
        'other_insurance_claim_reserves', 'reserve')
    add(2025, 'balance_sheet_claim_reserves', presentation['balance_sheet_claim_reserves'],
        presentation['report_year'], presentation['balance_sheet_pdf_page'],
        'balance_sheet_claim_reserves', 'balance_sheet')

    for year in sorted(premiums):
        if year-1 not in upr or year not in upr:
            raise ValueError(f'Missing opening or closing UPR: {year}')
        p, opening, closing = premiums[year], upr[year-1], upr[year]
        opening_net = opening['gross_upr']-opening['ceded_upr']
        closing_net = closing['gross_upr']-closing['ceded_upr']
        expected = p['reported_nwp'] + opening_net-closing_net
        difference = p['reported_nep']-expected
        checks.append(dict(year=year, check='net_premium_earning_from_reported_upr',
                           actual=p['reported_nep'], expected=expected, difference=difference,
                           status='pass' if difference == 0 else 'open'))
        if difference:
            issues.append(dict(year=year, issue='upr_earning_movement_unexplained',
                               difference=difference, unit='USD million',
                               note='NEP minus NWP/opening/closing net UPR bridge; do not plug into other movement without source evidence.'))
        if year == 2025:
            issues.append(dict(year=year, issue='held_for_sale_net_upr_unknown',
                               disclosed_gross_upr=held_for_sale['unearned_premium_reserves'],
                               unit='USD million',
                               note='Held-for-sale gross UPR is disclosed; corresponding ceded UPR is not separately disclosed. Do not subtract gross amount from a net bridge.'))

    reserve_rows = {}
    for table in raw['reserve_tables']:
        year = table['year']
        if year in reserve_rows:
            raise ValueError(f'Duplicate reserve year: {year}')
        reserve_rows[year] = table
        if year == 2019:
            for row, metric in (('closing_gross', 'gross_reserves'),
                                ('closing_unpaid_recoverables', 'unpaid_recoverables'),
                                ('closing_net', 'net_reserves')):
                add(year, metric, table[row], table['report_year'], table['pdf_page'], row, 'reserve')
            check(year, 'net_reserve_stock', table['closing_gross']-table['closing_unpaid_recoverables'], table['closing_net'])
            continue
        if set(table) != set(RESERVE_ROWS) | {'year', 'report_year', 'pdf_page'}:
            raise ValueError(f'Reserve row set invalid: {year}')
        for row, metric in (('closing_gross', 'gross_reserves'),
                            ('closing_unpaid_recoverables', 'unpaid_recoverables'),
                            ('closing_net', 'net_reserves'),
                            ('current_incurred', 'current_incurred'),
                            ('reserve_prior_incurred', 'reserve_prior_incurred'),
                            ('paid_current', 'paid_current'), ('paid_prior', 'paid_prior'),
                            ('reserve_fx_other', 'reserve_fx_other')):
            add(year, metric, table[row], table['report_year'], table['pdf_page'], row, 'reserve')
        for row in ('adoption_change', 'reported_opening_net_after_adoption',
                    'reported_total_incurred', 'reported_total_paid'):
            add(year, row, table[row], table['report_year'], table['pdf_page'], row, 'reserve')
        add(year, 'reserve_total_incurred', table['current_incurred']+table['reserve_prior_incurred'],
            table['report_year'], table['pdf_page'], 'current_incurred + reserve_prior_incurred', 'reserve', 'derived')
        check(year, 'reserve_opening_after_adoption',
              table['opening_gross']-table['opening_unpaid_recoverables']+table['adoption_change'],
              table['reported_opening_net_after_adoption'])
        check(year, 'reserve_incurred', table['current_incurred']+table['reserve_prior_incurred'],
              table['reported_total_incurred'])
        check(year, 'reserve_paid', table['paid_current']+table['paid_prior'], table['reported_total_paid'])
        kernel = reserves(ReserveInputs(table['opening_gross'], table['opening_unpaid_recoverables'],
                                        table['current_incurred'], table['reserve_prior_incurred'],
                                        table['paid_current'], table['paid_prior'],
                                        table['reserve_fx_other']+table['adoption_change'],
                                        table['closing_unpaid_recoverables']))
        check(year, 'reserve_rollforward', kernel['closing_net'], table['closing_net'])
        check(year, 'gross_net_reserve', kernel['closing_gross'], table['closing_gross'])
        previous = reserve_rows.get(year-1)
        if previous:
            check(year, 'reserve_prior_close_to_open_gross', previous['closing_gross'], table['opening_gross'])
            check(year, 'reserve_prior_close_to_open_unpaid_recoverables',
                  previous['closing_unpaid_recoverables'], table['opening_unpaid_recoverables'])
    if set(premiums) != set(range(2020, 2026)) or set(reserve_rows) != set(range(2019, 2026)):
        raise ValueError('Historical coverage window is incomplete')
    check(2025, 'claims_reserve_balance_sheet_presentation',
          reserve_rows[2025]['closing_gross']+presentation['other_insurance_claim_reserves']
          -held_for_sale['claims_reserves'], presentation['balance_sheet_claim_reserves'])
    return dict(schema_version=1, company=raw['company'], as_of=as_of,
                status='premium_and_reserve_pdf_rows_reconciled_with_open_upr_movements',
                unit=raw['unit'], facts=sorted(facts, key=lambda f: (f['year'], f['metric'])),
                checks=sorted(checks, key=lambda c: (c['year'], c['check'])), issues=issues,
                counts=dict(Counter(c['status'] for c in checks)), filings=raw['filings'],
                source_boundary='Numeric rows match issuer annual-report PDF copies; SEC accession dates verified. Exact row parity to original SEC HTML and PDF posting times are not independently certified.')


def write_history(raw_path, inventory_path, output_path, as_of, release_path=None):
    raw = json.loads(Path(raw_path).read_text())
    inventory = json.loads(Path(inventory_path).read_text())
    release = json.loads(Path(release_path).read_text()) if release_path else None
    history = build_history(raw, inventory, as_of, release)
    paths = (raw_path, inventory_path)+((release_path,) if release_path else ())
    history['input_hashes'] = {str(Path(path)): sha256(Path(path).read_bytes()).hexdigest()
                               for path in paths}
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(history, indent=2, allow_nan=False)+'\n')
    return history
