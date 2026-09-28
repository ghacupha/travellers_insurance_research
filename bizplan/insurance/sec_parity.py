# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

"""Selected original SEC HTML row comparisons against normalized issuer-PDF facts."""
from datetime import date
from hashlib import sha256
import json
from pathlib import Path


def check_sec_parity(sec_tables, history, statements, as_of):
    date.fromisoformat(as_of)
    if not sec_tables['company'] == history['company'] == statements['company']:
        raise ValueError('SEC parity issuer mismatch')
    if sec_tables['unit'] != 'USD million':
        raise ValueError('SEC parity unit mismatch')
    indexed = {(f['year'], f['metric']): f['value'] for f in history['facts']}
    for fact in statements['facts']:
        key = (fact['year'], fact['metric'])
        if key in indexed and indexed[key] != fact['value']:
            raise ValueError(f'Statement/history overlap mismatch: {key}')
        indexed[key] = fact['value']
    results = []
    seen = set()
    for table in sec_tables['tables']:
        filing = history['filings'][str(table['report_year'])]
        if filing['filed'] > as_of or table['url'].split('/R')[0] != filing['url'].rsplit('/', 1)[0]:
            raise ValueError(f'SEC parity filing unavailable or URL mismatch: {table["report_year"]}')
        columns = table['columns']
        if len(columns) != len(set(columns)) or any(year > table['report_year'] for year in columns):
            raise ValueError('Invalid SEC parity fiscal columns')
        for metric, values in table['rows'].items():
            if len(values) != len(columns):
                raise ValueError(f'Invalid SEC parity row width: {metric}')
            for year, sec_value in zip(columns, values):
                key = (table['url'], year, metric)
                if key in seen:
                    raise ValueError(f'Duplicate SEC parity row: {key}')
                seen.add(key)
                if metric == 'pc_reserves_continuing':
                    # Schedule VI excludes the P&C claims reserves classified as held for sale.
                    pdf_value = indexed[year, 'gross_reserves'] - indexed[year, 'held_for_sale_reserves']
                    basis = 'gross P&C reserve less P&C reserve held for sale'
                else:
                    pdf_value = indexed[year, metric]
                    basis = 'same normalized metric'
                if isinstance(sec_value, bool) or not isinstance(sec_value, (int, float)):
                    raise ValueError(f'Invalid SEC parity number: {key}')
                difference = pdf_value - sec_value
                results.append(dict(year=year, metric=metric, sec_value=sec_value,
                                    pdf_value=pdf_value, difference=difference,
                                    status='match' if difference == 0 else 'mismatch',
                                    comparison_basis=basis, sec_table=table['table'],
                                    sec_url=table['url'], sec_filing_date=filing['filed']))
                if difference:
                    raise ValueError(f'SEC parity mismatch: {metric} {year} at {table["url"]}')
    return dict(schema_version=1, company=history['company'], as_of=as_of,
                status='selected_sec_html_rows_matched_not_full_filing_parity',
                checked_rows=len(results), results=results,
                boundary='Manual SEC HTML transcription. Only enumerated rows are checked; 2020–2021 and most three-statement lines still await original SEC row parity.')


def write_sec_parity(sec_path, history_path, statement_path, output_path, as_of):
    paths = (sec_path, history_path, statement_path)
    sec, history, statements = (json.loads(Path(path).read_text()) for path in paths)
    result = check_sec_parity(sec, history, statements, as_of)
    result['input_hashes'] = {str(Path(path)): sha256(Path(path).read_bytes()).hexdigest()
                              for path in paths}
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    return result
