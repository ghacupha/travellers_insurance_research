import json
from pathlib import Path

from behave import given, then, when

from bizplan.insurance.historical_integration import build_historical_integration


ROOT = Path(__file__).resolve().parents[2] / 'examples/travelers'


@given('the Travelers 2019 through 2025 detailed balance-sheet rows')
def detailed_rows(context):
    context.balance_details = json.loads((ROOT / 'balance_sheet_detail_tables.json').read_text())
    context.inventory = json.loads((ROOT / 'source_inventory.json').read_text())
    context.history = json.loads((ROOT / 'historical_actuals.json').read_text())
    context.statements = json.loads((ROOT / 'statement_controls.json').read_text())


@when('the audited balance-sheet detail is integrated at the February 2026 cutoff')
def integrate(context):
    context.integrated = build_historical_integration(context.balance_details,
                                                       context.inventory, context.history,
                                                       context.statements, '2026-02-12')


@then('all 28 asset, liability, equity and accounting-equation controls pass')
def controls(context):
    assert len(context.integrated['checks']) == 28
    assert all(check['status'] == 'pass' for check in context.integrated['checks'])


@then('2025 held-for-sale assets and liabilities remain separate')
def held_for_sale(context):
    facts = {(fact['year'], fact['metric']): fact['value'] for fact in context.integrated['facts']}
    assert facts[2025, 'assets_held_for_sale'] == 4550
    assert facts[2025, 'liabilities_held_for_sale'] == 2542
