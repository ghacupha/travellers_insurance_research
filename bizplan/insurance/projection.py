# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

"""Explicit illustrative annual premium/loss projection; no implicit bank defaults."""
from dataclasses import dataclass, asdict
from .schedules import PremiumInputs, ReserveInputs, premiums, reserves, finite, fraction


@dataclass(frozen=True)
class Drivers:
    gwp_growth: float
    ceded_share: float
    closing_upr_share: float
    attritional_loss_ratio: float
    catastrophe_loss_ratio: float
    development_share_opening_reserves: float
    current_year_paid_share: float
    prior_year_paid_share: float
    unpaid_recoverable_share_gross: float
    expense_ratio: float


def project(opening, drivers, years):
    """Flat annual drivers; all output is modeled, not disclosed.

    GWP includes assumed business. No separate assumed growth or treaty layers yet.
    Prior development is signed and separate from current accident-year catastrophes.
    """
    finite(**asdict(drivers))
    fraction(**{k: v for k, v in asdict(drivers).items()
                if k in ('ceded_share', 'closing_upr_share', 'current_year_paid_share',
                         'prior_year_paid_share', 'unpaid_recoverable_share_gross')})
    if drivers.gwp_growth <= -1 or drivers.unpaid_recoverable_share_gross >= 1:
        raise ValueError('Invalid growth or recoverable share')
    if min(drivers.attritional_loss_ratio, drivers.catastrophe_loss_ratio, drivers.expense_ratio) < 0:
        raise ValueError('Loss and expense ratios must be nonnegative')
    if not years or years != list(range(years[0], years[0]+len(years))):
        raise ValueError('Projection years must be consecutive and nonempty')
    state = dict(opening)
    results = []
    for year in years:
        gwp = state['gwp'] * (1 + drivers.gwp_growth)
        ceded = gwp * drivers.ceded_share
        gross_upr = gwp * drivers.closing_upr_share
        ceded_upr = ceded * drivers.closing_upr_share
        p = premiums(PremiumInputs(gwp, 0, ceded, state['gross_upr'], gross_upr,
                                   state['ceded_upr'], ceded_upr, 0, 0))
        net_open = state['gross_reserves'] - state['unpaid_recoverables']
        current = p['nep'] * (drivers.attritional_loss_ratio + drivers.catastrophe_loss_ratio)
        development = net_open * drivers.development_share_opening_reserves
        paid_current = current * drivers.current_year_paid_share
        paid_prior = net_open * drivers.prior_year_paid_share
        net_close = net_open + current + development - paid_current - paid_prior
        recoverable = net_close * drivers.unpaid_recoverable_share_gross / (1-drivers.unpaid_recoverable_share_gross)
        r = reserves(ReserveInputs(state['gross_reserves'], state['unpaid_recoverables'],
                                   current, development, paid_current, paid_prior, 0, recoverable))
        if p['nep'] <= 0:
            raise ValueError('Projection NEP must be positive')
        expense = p['nep'] * drivers.expense_ratio
        results.append(dict(year=year, status='modeled', premiums=p, reserves=r,
                            underwriting_expenses=expense,
                            underwriting_result=p['nep']-r['incurred_net']-expense,
                            combined_ratio=(r['incurred_net']+expense)/p['nep']))
        state = dict(gwp=gwp, gross_upr=gross_upr, ceded_upr=ceded_upr,
                     gross_reserves=r['closing_gross'], unpaid_recoverables=recoverable)
    return results
