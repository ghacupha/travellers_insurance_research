# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

from pathlib import Path
from behave import given, when, then
from bizplan.insurance.pipeline import load_actuals
from bizplan.insurance.schedules import PremiumInputs, ReserveInputs, premiums, reserves, travelers_ratios

ROOT = Path(__file__).resolve().parents[2]


@given('annual gross written premium of 100 with 20 ceded')
def premium_input(context):
    context.gwp, context.ceded = 100, 20


@when('three months of uniform coverage have elapsed')
def earn(context):
    context.p = premiums(PremiumInputs(context.gwp, 0, context.ceded, 0, 75, 0, 15, 0, 0))


@then('net written premium is 80 and net earned premium is 20')
def check_premium(context):
    assert context.p['nwp'] == 80 and context.p['nep'] == 20


@given('a covered repair estimated at 15000')
def repair(context):
    context.incurred = 15000


@when('the insurer has paid only 5000')
def pay(context):
    context.r = reserves(ReserveInputs(0, 0, context.incurred, 0, 5000, 0, 0, 0))


@then('incurred losses are 15000 and the outstanding reserve is 10000')
def check_repair(context):
    assert context.r['incurred_net'] == 15000 and context.r['closing_net'] == 10000


@given('opening net claims reserves of 100 and current year incurred losses of 40')
def opening(context):
    context.opening, context.current = 100, 40


@when('prior year development is {development:g} and paid losses are 30')
def develop(context, development):
    context.r = reserves(ReserveInputs(context.opening, 0, context.current, development, 10, 20, 0, 0))


@then('closing net reserves are {reserve:g} and total incurred is {incurred:g}')
def check_development(context, reserve, incurred):
    assert context.r['closing_net'] == reserve and context.r['incurred_net'] == incurred


@given('the verified Travelers 2025 annual disclosures')
def actuals(context):
    context.facts = load_actuals(ROOT/'examples/travelers/actuals.json', '2026-02-12')['periods'][1]['facts']


@when('the reported ratio adjustments are applied')
def ratio(context):
    names = ('nep', 'claims', 'policyholder_dividends', 'loss_allocated_fees',
             'dac_amortization', 'general_admin', 'noninsurance_admin',
             'expense_allocated_fees', 'billing_fees_other', 'catastrophe_losses', 'prior_year_development')
    context.ratio = travelers_ratios(**{name: context.facts[name]['value'] for name in names})


@then('the loss numerator is 26990 and the expense numerator is 12501')
def numerators(context):
    assert context.ratio['loss_numerator'] == 26990 and context.ratio['expense_numerator'] == 12501


@then('the combined ratio rounds to 89.9 percent')
def combined(context):
    assert round(100*context.ratio['combined_ratio'], 1) == 89.9


@given('an information cutoff of 2025-12-31')
def cutoff(context):
    context.cutoff = '2025-12-31'


@when('the 2025 earnings release published in January 2026 is loaded')
def unavailable(context):
    context.error = None
    try:
        load_actuals(ROOT/'examples/travelers/actuals.json', context.cutoff)
    except ValueError as exc:
        context.error = str(exc)


@then('the research run is rejected for unavailable information')
def rejection(context):
    assert context.error and 'not available' in context.error
