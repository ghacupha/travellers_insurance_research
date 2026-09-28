# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

import json
from pathlib import Path

from behave import given, then, when

from bizplan.insurance.operating_movements import build_operating_movements


ROOT = Path(__file__).resolve().parents[2] / 'examples/travelers'


@given('the Travelers audited cash-flow and equity rows for 2020 through 2025')
def audited_rows(context):
    context.raw = json.loads((ROOT / 'operating_movement_tables.json').read_text())
    context.inventory = json.loads((ROOT / 'source_inventory.json').read_text())
    context.history = json.loads((ROOT / 'historical_actuals.json').read_text())
    context.statements = json.loads((ROOT / 'statement_controls.json').read_text())


@when('the operating schedules are built at the February 2026 cutoff')
def build(context):
    context.operating = build_operating_movements(context.raw, context.inventory,
                                                   context.history, context.statements,
                                                   '2026-02-12')


@then('all 30 equity and financing controls reconcile')
def controls(context):
    assert len(context.operating['checks']) == 30
    assert all(check['status'] == 'pass' for check in context.operating['checks'])


@then('the 2025 DAC stock bridge remains an open 83 million decrease')
def dac_gap(context):
    row = next(row for row in context.operating['bridges']
               if row['year'] == 2025 and row['metric'] == 'dac_stock_gap')
    assert row['difference'] == -83 and row['status'] == 'open'


@then('the 2025 investment cash proxy remains a diagnostic, not a balancing entry')
def investment_gap(context):
    row = next(row for row in context.operating['bridges']
               if row['year'] == 2025 and row['metric'] == 'investment_cash_proxy_gap')
    assert row['difference'] == -304
    assert row['treatment'] == 'diagnostic_only_no_balancing_entry'
