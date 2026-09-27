import json
from pathlib import Path

from behave import given, then, when

from bizplan.insurance.sec_parity import check_sec_parity


ROOT = Path(__file__).resolve().parents[2] / 'examples/travelers'


@given('the selected original SEC Travelers disclosure rows')
def selected_rows(context):
    context.sec_tables = json.loads((ROOT / 'sec_parity_tables.json').read_text())
    context.history = json.loads((ROOT / 'historical_actuals.json').read_text())
    context.statements = json.loads((ROOT / 'statement_controls.json').read_text())


@when('the SEC row comparisons run at the February 2026 cutoff')
def compare(context):
    context.parity = check_sec_parity(context.sec_tables, context.history,
                                      context.statements, '2026-02-12')


@then('all 88 selected SEC rows match the sourced historical facts')
def all_match(context):
    assert context.parity['checked_rows'] == 88
    assert all(row['status'] == 'match' for row in context.parity['results'])


@then('the 2025 continuing P&C reserve is 65734 million after held-for-sale classification')
def continuing_reserve(context):
    row = next(row for row in context.parity['results']
               if row['year'] == 2025 and row['metric'] == 'pc_reserves_continuing')
    assert row['pdf_value'] == row['sec_value'] == 65734
    assert row['comparison_basis'] == 'gross P&C reserve less P&C reserve held for sale'


@then('2020 and 2021 remain outside this SEC row comparison')
def older_years(context):
    assert {row['year'] for row in context.parity['results']} == {2022, 2023, 2024, 2025}
