# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

"""Pure P&C schedules; monetary inputs share one currency/unit.

Positive development means adverse; recoverables here cover UNPAID claims only.
No missing inputs are silently converted to zero.
"""
from dataclasses import dataclass, asdict
from math import isfinite


def finite(**values):
    for name, value in values.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
            raise ValueError(f"{name} must be a finite number")


def nonnegative(**values):
    finite(**values)
    for name, value in values.items():
        if value < 0:
            raise ValueError(f"{name} must be nonnegative")


def fraction(**values):
    nonnegative(**values)
    if any(value > 1 for value in values.values()):
        raise ValueError("Fractions must be between zero and one")


@dataclass(frozen=True)
class PremiumInputs:
    direct_written: float
    assumed_written: float
    ceded_written: float
    opening_gross_upr: float
    closing_gross_upr: float
    opening_ceded_upr: float
    closing_ceded_upr: float
    gross_upr_other_change: float
    ceded_upr_other_change: float


def premiums(p: PremiumInputs):
    v = asdict(p)
    finite(**v)
    nonnegative(**{k: x for k, x in v.items() if 'other_change' not in k})
    if p.opening_ceded_upr > p.opening_gross_upr or p.closing_ceded_upr > p.closing_gross_upr:
        raise ValueError("Ceded UPR exceeds gross UPR")
    gwp = p.direct_written + p.assumed_written
    nwp = gwp - p.ceded_written
    gep = gwp + p.opening_gross_upr - p.closing_gross_upr + p.gross_upr_other_change
    cep = p.ceded_written + p.opening_ceded_upr - p.closing_ceded_upr + p.ceded_upr_other_change
    nonnegative(nwp=nwp, gross_earned=gep, ceded_earned=cep, nep=gep-cep)
    return dict(gwp=gwp, ceded_written=p.ceded_written, nwp=nwp,
                gross_earned=gep, ceded_earned=cep, nep=gep-cep,
                closing_net_upr=p.closing_gross_upr-p.closing_ceded_upr)


@dataclass(frozen=True)
class ReserveInputs:
    opening_gross: float
    opening_unpaid_recoverables: float
    current_accident_year_incurred_net: float
    prior_year_development_net: float
    paid_current_year_net: float
    paid_prior_years_net: float
    other_net_change: float
    closing_unpaid_recoverables: float


def reserves(r: ReserveInputs):
    finite(**asdict(r))
    nonnegative(**{k: v for k, v in asdict(r).items()
                   if k not in ('prior_year_development_net', 'other_net_change')})
    opening_net = r.opening_gross - r.opening_unpaid_recoverables
    incurred = r.current_accident_year_incurred_net + r.prior_year_development_net
    paid = r.paid_current_year_net + r.paid_prior_years_net
    closing_net = opening_net + incurred - paid + r.other_net_change
    nonnegative(opening_net=opening_net, closing_net=closing_net)
    return dict(opening_net=opening_net, incurred_net=incurred, paid_net=paid,
                prior_year_development_net=r.prior_year_development_net,
                closing_net=closing_net,
                closing_gross=closing_net+r.closing_unpaid_recoverables,
                closing_unpaid_recoverables=r.closing_unpaid_recoverables)


def travelers_ratios(nep, claims, policyholder_dividends, loss_allocated_fees,
                     dac_amortization, general_admin, noninsurance_admin,
                     expense_allocated_fees, billing_fees_other, catastrophe_losses,
                     prior_year_development):
    """Travelers earnings-release ratio bridge, distinct from GAAP underwriting profit."""
    finite(**locals())
    if nep <= 0:
        raise ValueError("NEP must be positive")
    loss_numerator = claims - policyholder_dividends - loss_allocated_fees
    expense_numerator = (dac_amortization + general_admin - noninsurance_admin
                         - expense_allocated_fees - billing_fees_other)
    loss = loss_numerator / nep
    expense = expense_numerator / nep
    combined = loss + expense
    return dict(loss_numerator=loss_numerator, expense_numerator=expense_numerator,
                loss_ratio=loss, expense_ratio=expense, combined_ratio=combined,
                underlying_combined_ratio=combined-(catastrophe_losses+prior_year_development)/nep)


def investment_portfolio(opening, purchases, disposals_at_carrying_value,
                         valuation_change, other_change, net_yield):
    """Average carrying balance yield approximation, not a bond-level cash-flow model.

    Yield is net of investment expenses; realized gains belong in a separate schedule.
    """
    finite(**locals())
    nonnegative(opening=opening, purchases=purchases, disposals=disposals_at_carrying_value)
    closing = opening + purchases - disposals_at_carrying_value + valuation_change + other_change
    nonnegative(closing=closing)
    average = (opening + closing) / 2
    return dict(closing=closing, average=average, net_investment_income=average*net_yield)


def equity(opening, net_income, oci, dividends, buybacks, issuance, other_change):
    finite(**locals())
    nonnegative(opening=opening, dividends=dividends, buybacks=buybacks, issuance=issuance)
    closing = opening + net_income + oci - dividends - buybacks + issuance + other_change
    return dict(closing=closing, distributions=dividends+buybacks)
