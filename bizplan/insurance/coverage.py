# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

"""Coverage planning is evidence tracking, not a data-imputation step."""
from collections import Counter
from datetime import date
from hashlib import sha256
import json
from pathlib import Path

from .specification import workbook_contract

SEGMENTS = ('business_insurance', 'bond_specialty', 'personal_insurance')


def build_coverage(contract, inventory, actuals, as_of, history=None, statements=None,
                   movements=None):
    date.fromisoformat(as_of)
    if inventory['company'] != actuals['company']['ticker']:
        raise ValueError('Source inventory issuer differs from actuals')
    documents = {s['fiscal_year']:s for s in inventory['sources']}
    if len(documents) != len(inventory['sources']):
        raise ValueError('Duplicate source fiscal year')
    actual_periods = {p['year']:p for p in actuals['periods']}
    historical_facts = {}
    if history is not None:
        if history['company'] != inventory['company']:
            raise ValueError('History issuer differs from inventory')
        for fact in history['facts']:
            key = (fact['metric'], fact['scope'], fact['year'])
            if key in historical_facts:
                raise ValueError(f'Duplicate historical coverage fact: {key}')
            historical_facts[key] = fact
    statement_facts = {}
    if statements is not None:
        if statements['company'] != inventory['company']:
            raise ValueError('Statement issuer differs from inventory')
        for fact in statements['facts']:
            key = (fact['metric'], fact['scope'], fact['year'])
            if key in statement_facts:
                raise ValueError(f'Duplicate statement coverage fact: {key}')
            statement_facts[key] = fact
    movement_facts = {}
    movement_map = {'aoci': 'closing_aoci', 'dividends': 'equity_dividends'}
    if movements is not None:
        if movements['company'] != inventory['company']:
            raise ValueError('Operating movement issuer differs from inventory')
        for fact in movements['facts']:
            metric = next((target for target, source in movement_map.items()
                           if source == fact['metric']), fact['metric'])
            key = (metric, 'consolidated', fact['year'])
            if key in movement_facts:
                raise ValueError(f'Duplicate operating coverage fact: {key}')
            movement_facts[key] = fact
    records = []
    for row in contract['rows']:
        scopes = ('consolidated',)+SEGMENTS if row['segment_detail'] else ('consolidated',)
        years = ([contract['opening_year']] if row['opening_required'] else [])+contract['actual_years']
        for scope in scopes:
            for year in years:
                document = documents.get(year)
                candidates = document.get('candidate_pages', {}).get(row['source_group'], []) if document else []
                record = dict(metric=row['id'], label=row['label'],section=row['section'],
                              year=year,scope=scope,basis=row['basis'],unit=row['unit'],
                              period_type=row['period_type'], role='opening' if year==contract['opening_year'] else 'actual',
                              status='document_indexed' if document else 'source_missing',
                              source_id=document['id'] if document else None,
                              candidate_pdf_pages=[c['pdf_page'] for c in candidates],
                              value=None, cutoff_eligibility='unverified',
                              note='Page hits are search candidates, not proof of metric/scope disclosure or cutoff eligibility.')
                if scope != 'consolidated':
                    record['note'] += ' Segment detail is requested; availability has not been assumed.'
                table = document.get('reviewed_tables', {}).get(row['source_group']) if document else None
                if table and scope == 'consolidated':
                    record.update(status='table_located', reviewed_table_pdf_page=table['pdf_page'],
                                  note='Relevant consolidated table located; specific row/value extraction and source-cutoff verification pending.')
                fact = actual_periods.get(year, {}).get('facts', {}).get(row['actual_key']) if scope=='consolidated' else None
                if fact:
                    source = actuals['sources'][fact['source_id']]
                    date.fromisoformat(source['published'])
                    if fact['unit'] != row['unit']:
                        raise ValueError(f"Unit mismatch: {row['id']}")
                    eligible = source['published'] <= as_of
                    record.update(status='extracted_unreconciled' if eligible else 'after_cutoff',
                                  source_id=fact['source_id'],candidate_pdf_pages=[],
                                  value=fact['value'],locator=fact['locator'],
                                  cutoff_eligibility='eligible' if eligible else 'ineligible',
                                  note='Existing disclosed input; full schedule and filing reconciliation pending.')
                    if row['id']=='reported_loss_ratio' and year==2025 and eligible:
                        record.update(status='issue_open',note='Stored issuer ratio differs from calculated release bridge; investigation pending.')
                historical = historical_facts.get((row['id'], scope, year))
                statement = statement_facts.get((row['id'], scope, year))
                movement = movement_facts.get((row['id'], scope, year))
                if historical and statement and historical['value'] != statement['value']:
                    raise ValueError(f"Statement/history value mismatch: {row['id']} {year}")
                for overlap in (historical, statement):
                    if overlap and movement and overlap['value'] != movement['value']:
                        raise ValueError(f"Movement/previous source mismatch: {row['id']} {year}")
                if historical:
                    if historical['unit'] != row['unit']:
                        raise ValueError(f"Historical unit mismatch: {row['id']}")
                    eligible = historical['sec_filing_date'] <= as_of
                    status = ('pdf_extracted' if historical['table'] in ('upr', 'balance_sheet', 'held_for_sale')
                              else 'pdf_reconciled') if eligible else 'after_cutoff'
                    record.update(status=status, source_id=historical['source_id'],
                                  value=historical['value'], reviewed_table_pdf_page=historical['pdf_page'],
                                  locator=f"{historical['table']}:{historical['row']}; FY{year}",
                                  fact_status=historical['status'],
                                  sec_filing_accession=historical['sec_filing_accession'],
                                  sec_filing_date=historical['sec_filing_date'],
                                  cutoff_eligibility=historical['cutoff_status'] if eligible else 'ineligible',
                                  note=('Premium/reserve PDF arithmetic reconciled; original SEC filing date verified. '
                                        'Selected SEC row parity is tracked separately; PDF posting date pending.' if status=='pdf_reconciled' else
                                        'Row transcribed from issuer PDF; broader schedule movement or presentation bridge pending. '
                                        'Original SEC filing date verified; selected SEC row parity tracked separately.'))
                elif statement:
                    if statement['unit'] != row['unit']:
                        raise ValueError(f"Statement unit mismatch: {row['id']}")
                    eligible = statement['sec_filing_date'] <= as_of
                    record.update(status='statement_control_checked' if eligible else 'after_cutoff',
                                  source_id=statement['source_id'],value=statement['value'],
                                  reviewed_table_pdf_page=statement['pdf_page'],
                                  locator=f"{statement['statement']}:{statement['metric']}; FY{year}",
                                  sec_filing_accession=statement['sec_filing_accession'],
                                  sec_filing_date=statement['sec_filing_date'],
                                  cutoff_eligibility=statement['cutoff_status'] if eligible else 'ineligible',
                                  note='Selected audited-statement row passes its statement control checks; full line mapping and remaining SEC row parity pending.')
                elif movement:
                    if movement['unit'] != row['unit']:
                        raise ValueError(f"Operating movement unit mismatch: {row['id']}")
                    eligible = movement['sec_filing_date'] <= as_of
                    record.update(status='operating_control_checked' if eligible else 'after_cutoff',
                                  source_id=movement['source_id'],value=movement['value'],
                                  reviewed_table_pdf_page=movement['pdf_page'],
                                  locator=f"{movement['statement']}:{movement['metric']}; FY{year}",
                                  fact_status=movement['status'],
                                  sec_filing_date=movement['sec_filing_date'],
                                  cutoff_eligibility='filing_date_verified_pdf_copy' if eligible else 'ineligible',
                                  note='Selected audited cash-flow/equity row reconciled to control; exact SEC row parity pending.')
                records.append(record)
    return dict(schema_version=1,company=actuals['company'],as_of=as_of,
                actual_years=contract['actual_years'],opening_year=contract['opening_year'],
                status='coverage_inventory_not_validated_actuals',
                counts=dict(Counter(r['status'] for r in records)), records=records,
                release_sources=actuals['sources'])


def write_planning_outputs(inventory_path, actuals_path, output_dir, as_of,
                           history_path=None, statements_path=None, movements_path=None):
    contract=workbook_contract(list(range(2020,2026)),list(range(2026,2031)))
    inventory=json.loads(Path(inventory_path).read_text())
    actuals=json.loads(Path(actuals_path).read_text())
    history=json.loads(Path(history_path).read_text()) if history_path else None
    statements=json.loads(Path(statements_path).read_text()) if statements_path else None
    movements=json.loads(Path(movements_path).read_text()) if movements_path else None
    coverage=build_coverage(contract,inventory,actuals,as_of,history,statements,movements)
    coverage['input_hashes']={str(Path(p)):sha256(Path(p).read_bytes()).hexdigest()
                             for p in (inventory_path,actuals_path)+((history_path,) if history_path else ())+
                             ((statements_path,) if statements_path else ())+
                             ((movements_path,) if movements_path else ())}
    output=Path(output_dir)
    output.mkdir(parents=True,exist_ok=True)
    (output/'workbook_contract.json').write_text(json.dumps(contract,indent=2)+'\n')
    (output/'historical_coverage.json').write_text(json.dumps(coverage,indent=2,allow_nan=False)+'\n')
    codes={'document_indexed':'D','table_located':'T','source_missing':'M','extracted_unreconciled':'E',
           'pdf_extracted':'P','pdf_reconciled':'R','statement_control_checked':'C',
           'operating_control_checked':'O',
           'after_cutoff':'A','issue_open':'!'}
    lines=['# Historical coverage matrix', '',
           f"Issuer: {actuals['company']['name'].rstrip('.')}. Information cutoff: {as_of}.", '',
           '**D** = source PDF cached/indexed; row-level extraction and cutoff verification pending. '
           '**T** = relevant consolidated table located; specific row/value extraction still pending. '
           '**E** = release value extracted, schedule reconciliation pending. '
           '**P** = PDF row extracted, wider schedule/presentation unresolved. '
           '**R** = PDF premium/reserve arithmetic reconciled; selected SEC parity tracked separately. '
           '**C** = selected statement row passed statement control checks; full mapping pending. '
           '**O** = selected audited operating cash/equity row passed controls. '
           '**!** = open discrepancy. '
           '**A** = source after cutoff. **M** = source missing.', '',
           'No cell in this matrix is a fully certified historical statement. Source availability is not numeric completeness.', '',
           f"Coverage records: {len(coverage['records'])}; status counts: {coverage['counts']}.", '',
           '## Source files', '', '| FY | PDF pages | SHA-256 prefix | Source |', '|---|---:|---|---|']
    for s in inventory['sources']:
        lines.append(f"| {s['fiscal_year']} | {s['pages']} | {s['sha256'][:12]} | [Annual report]({s['url']}) |")
    lines += ['', 'Full hashes, cache paths and candidate page locators are in source_inventory.json.',
              'Original SEC filing dates for 2019–2025 are recorded in historical_tables.json. '
              'Issuer annual-report PDF posting dates remain unverified; selected SEC HTML row parity is in SEC_PARITY.md.', '',
              '## Reviewed table locations', '',
              'One-based PDF pages, not printed page numbers. Table presence does not certify every requested line.', '',
              '| FY | Income | Balance sheet | Equity | Cash flow | Premium/reinsurance | Reserve rollforward |',
              '|---|---:|---:|---:|---:|---:|---:|']
    for source in inventory['sources']:
        locations=source.get('reviewed_tables',{})
        pages=[str(locations.get(key,{}).get('pdf_page','pending')) for key in
               ('income_statement','balance_sheet','equity','cash_flow','earned_reinsurance','claims_rollforward')]
        lines.append(f"| {source['fiscal_year']} | "+' | '.join(pages)+' |')
    lines += ['',
              '## Consolidated metrics', '',
              '| Metric | Basis | 2019 opening | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |',
              '|---|---|---|---|---|---|---|---|---|']
    index={(r['metric'],r['scope'],r['year']):r for r in coverage['records']}
    for row in contract['rows']:
        states=[]
        for year in range(2019,2026):
            cell=index.get((row['id'],'consolidated',year))
            states.append(codes[cell['status']] if cell else '—')
        lines.append(f"| {row['label']} (`{row['id']}`) | {row['basis']} | "+' | '.join(states)+' |')
    lines += ['', '## Segment coverage', '',
              'Business Insurance, Bond & Specialty Insurance and Personal Insurance each have separate '
              'metric/year records in the JSON. None is marked extracted merely because a consolidated '
              'value exists. Opening records exist only for balance metrics.', '',
              '| Requested metric | Business Insurance | Bond & Specialty | Personal Insurance |',
              '|---|---|---|---|']
    for row in contract['rows']:
        if row['segment_detail']:
            lines.append(f"| {row['label']} | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |")
    lines += ['', '## Next extraction batches', '',
              '1. Verify transcribed PDF rows against the original SEC filing and explain net UPR earning movements.',
              '2. Extract the remaining statement openings, investment, expense/DAC, tax and equity detail.',
              '3. Add segment schedules and bridges; verify disclosure definitions before filling unavailable splits.']
    (output/'HISTORICAL_COVERAGE.md').write_text('\n'.join(lines)+'\n')
    return coverage
