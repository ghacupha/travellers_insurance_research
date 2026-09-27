"""Issuer identity is configuration; accounting and business models are capabilities."""
from dataclasses import dataclass
from .sources import companyfacts_url


@dataclass(frozen=True)
class Company:
    name: str
    ticker: str
    cik: str
    accounting_basis: str
    insurer_type: str
    ratio_adapter: str

    def validate(self):
        if not self.name.strip() or not self.ticker.strip():
            raise ValueError('Company name and ticker are required')
        companyfacts_url(self.cik)
        if (self.accounting_basis, self.insurer_type) != ('US_GAAP', 'property_casualty'):
            raise ValueError('Research schedules currently support US_GAAP property_casualty only; life and IFRS require separate engines')
        if self.ratio_adapter not in ('travelers_reported', 'standard_pc'):
            raise ValueError('Unknown ratio adapter')
        return self
