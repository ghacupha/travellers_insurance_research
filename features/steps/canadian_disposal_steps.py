# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

import json
from pathlib import Path

from behave import given, then, when

from bizplan.insurance.disposal import build_disposal_bridge


ROOT = Path(__file__).resolve().parents[2] / 'examples/travelers'


@given('the Travelers Canadian disposal disclosures')
def sources(context):
    context.disposal_inputs = [json.loads((ROOT / name).read_text()) for name in (
        'canadian_disposal_sources.json', 'historical_actuals.json',
        'statement_controls.json', 'historical_integration.json')]


@when('the Canadian disposal bridge is built at the February 2026 cutoff')
def february(context):
    context.disposal = build_disposal_bridge(*context.disposal_inputs, '2026-02-12')


@when('the Canadian disposal bridge is built at the April 2026 cutoff')
def april(context):
    context.disposal = build_disposal_bridge(*context.disposal_inputs, '2026-04-16')


@then('the bridge shows 2008 million of held-for-sale book net assets')
def book_net_assets(context):
    assert context.disposal['derived']['disposed_net_assets_book'] == 2008


@then('April 2026 reserve and premium facts are absent')
def no_look_ahead(context):
    assert len(context.disposal['facts']) == 10
    assert 'continuing_net_claim_reserves_opening' not in context.disposal['derived']


@then('continuing opening net claims reserves are 58219 million')
def reserves(context):
    assert context.disposal['derived']['continuing_net_claim_reserves_opening'] == 58219


@then('the divested 2025 net written and earned premiums are 989 and 1035 million')
def premium(context):
    facts = {item['metric']: item['value'] for item in context.disposal['facts']}
    assert facts['divested_nwp_total_2025'] == 989
    assert facts['divested_nep_total_2025'] == 1035


@then('cash proceeds less December book net assets remains a diagnostic')
def no_fake_gain(context):
    assert context.disposal['derived']['cash_proceeds_less_2025_disposal_book_net_assets_diagnostic'] == 376
    assert 'gain' not in context.disposal['derived']
