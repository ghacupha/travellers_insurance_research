# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

import json
from pathlib import Path

from behave import given, when, then

from bizplan.insurance.historical import build_history


ROOT = Path(__file__).resolve().parents[2]


@given('the 2019–2025 Travelers premium and reserve tables')
def source_tables(context):
    context.tables = json.loads((ROOT / 'examples/travelers/historical_tables.json').read_text())
    context.inventory = json.loads((ROOT / 'examples/travelers/source_inventory.json').read_text())
    context.release = json.loads((ROOT / 'examples/travelers/actuals.json').read_text())


@when('the historical schedules are reconciled at the February 2026 cutoff')
def reconcile(context):
    context.history = build_history(context.tables, context.inventory, '2026-02-12', context.release)
    context.checks = {(r['year'], r['check']): r for r in context.history['checks']}
    context.facts = {(f['year'], f['metric']): f for f in context.history['facts']}


@then('2020 reserves include a separately disclosed 53 million adoption movement')
def adoption(context):
    fact = context.facts[2020, 'adoption_change']
    assert fact['value'] == 53 and fact['status'] == 'disclosed'


@then('the 2020 reserve rollforward balances without a plug')
def reserve_balance(context):
    check = context.checks[2020, 'reserve_rollforward']
    assert check['status'] == 'pass' and check['difference'] == 0


@then('the 2025 claims reserve presentation bridges to 65737 million')
def reserve_presentation(context):
    check = context.checks[2025, 'claims_reserve_balance_sheet_presentation']
    assert check['actual'] == 65737 and check['difference'] == 0


@then('the 2025 net premium earning bridge retains a 412 million unresolved movement')
def premium_gap(context):
    check = context.checks[2025, 'net_premium_earning_from_reported_upr']
    assert check['difference'] == -412 and check['status'] == 'open'
    assert any(i['issue'] == 'held_for_sale_net_upr_unknown' for i in context.history['issues'])
    assert (2025, 'upr_other_change') not in context.facts
