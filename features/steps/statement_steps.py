# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

import json
from pathlib import Path

from behave import given, when, then

from bizplan.insurance.statement_controls import build_statement_controls


ROOT = Path(__file__).resolve().parents[2]


@given('the 2019–2025 Travelers statement controls')
def statements(context):
    context.statement_tables = json.loads((ROOT / 'examples/travelers/statement_control_tables.json').read_text())
    context.inventory = json.loads((ROOT / 'examples/travelers/source_inventory.json').read_text())
    context.history = json.loads((ROOT / 'examples/travelers/historical_actuals.json').read_text())


@when('the audited statement control checks run')
def checks(context):
    context.statements = build_statement_controls(context.statement_tables, context.inventory,
                                                  context.history, '2026-02-12')
    context.checks = {(x['year'], x['check']): x for x in context.statements['checks']}
    context.facts = {(x['year'], x['metric']): x for x in context.statements['facts']}


@then('2025 net income agrees between the income and cash-flow statements')
def income_cash(context):
    assert context.checks[2025, 'income_to_cash_flow']['status'] == 'pass'
    assert context.facts[2025, 'net_income']['value'] == 6288


@then('2025 cash includes a separately disclosed 171 million held-for-sale reclassification')
def cash_held_for_sale(context):
    assert context.facts[2025, 'cash_held_for_sale_reclassification']['value'] == 171
    assert context.checks[2025, 'cash_flow_closing']['status'] == 'pass'


@then('the 2025 balance sheet and investment asset classes balance')
def balance_sheet(context):
    assert context.checks[2025, 'balance_sheet']['status'] == 'pass'
    assert context.checks[2025, 'investment_asset_classes']['status'] == 'pass'
