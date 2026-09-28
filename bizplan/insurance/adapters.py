# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

"""Explicit issuer-specific disclosure bridges; no issuer logic in acquisition."""
from .schedules import finite, travelers_ratios


def calculate_ratios(facts, adapter):
    if adapter == 'travelers_reported':
        names = ('nep', 'claims', 'policyholder_dividends', 'loss_allocated_fees',
                 'dac_amortization', 'general_admin', 'noninsurance_admin',
                 'expense_allocated_fees', 'billing_fees_other', 'catastrophe_losses',
                 'prior_year_development')
        return travelers_ratios(**{name: facts[name]['value'] for name in names})
    if adapter == 'standard_pc':
        # Inputs must already be reconciled to this issuer's published definition.
        nep = facts['nep']['value']
        loss = facts['loss_ratio_numerator']['value']
        expense = facts['expense_ratio_numerator']['value']
        finite(nep=nep, loss=loss, expense=expense)
        if nep <= 0:
            raise ValueError('NEP must be positive')
        return dict(loss_numerator=loss, expense_numerator=expense,
                    loss_ratio=loss/nep, expense_ratio=expense/nep,
                    combined_ratio=(loss+expense)/nep)
    raise ValueError(f'Unsupported ratio adapter: {adapter}')
