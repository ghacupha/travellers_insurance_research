# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

"""SEC acquisition and point-in-time selection. No LLM is a numeric data provider."""
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen
from .schedules import finite

def companyfacts_url(cik):
    digits = str(cik)
    if not digits.isdigit() or not 0 < int(digits) < 10**10:
        raise ValueError('CIK must be a positive identifier of at most ten digits')
    return f'https://data.sec.gov/api/xbrl/companyfacts/CIK{int(digits):010d}.json'

# Initial consolidated candidates only. Insurer custom/segment tags require filing tables.
STANDARD_TAGS = {
    'assets': ('Assets', 'instant'),
    'liabilities': ('Liabilities', 'instant'),
    'equity': ('StockholdersEquity', 'instant'),
    'net_income': ('NetIncomeLoss', 'duration'),
    'operating_cash_flow': ('NetCashProvidedByUsedInOperatingActivities', 'duration'),
}


def fetch_companyfacts(cik, cache_dir, user_agent):
    """One request; caller supplies a real descriptive SEC contact User-Agent.

    Content-addressed raw bytes plus retrieval manifest. HTTP errors propagate.
    """
    if not user_agent or '@' not in user_agent:
        raise ValueError('Set SEC_USER_AGENT to your application name and contact email')
    url = companyfacts_url(cik)
    request = Request(url, headers={'User-Agent': user_agent,
                                               'Accept': 'application/json'})
    with urlopen(request, timeout=45) as response:
        raw = response.read()
    payload = json.loads(raw)
    if int(payload['cik']) != int(cik):
        raise ValueError('Unexpected issuer in SEC response')
    digest = sha256(raw).hexdigest()
    directory = Path(cache_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f'{digest}.json'
    if not path.exists():
        path.write_bytes(raw)
    manifest = dict(url=url, cik=str(cik), sha256=digest, raw_file=path.name,
                    retrieved_at=datetime.now(timezone.utc).isoformat())
    (directory / f'{digest}.manifest.json').write_text(json.dumps(manifest, indent=2))
    return path


def select_annual(payload, tag, year, as_of, kind, unit='USD', expected_cik=None):
    """Select exact period and latest known filing; reject ambiguous same-filing facts.

    Filter by period dates, not SEC 'fy' (comparatives can carry a later filing year).
    USD is normalized to USD millions; provenance retains the original unit/value.
    """
    url = companyfacts_url(payload['cik'])
    if expected_cik is not None and int(payload['cik']) != int(expected_cik):
        raise ValueError('SEC snapshot issuer does not match configured CIK')
    if kind not in ('instant', 'duration'):
        raise ValueError('kind must be instant or duration')
    date.fromisoformat(as_of)
    end, start = f'{year}-12-31', f'{year}-01-01'
    candidates = []
    for fact in payload.get('facts', {}).get('us-gaap', {}).get(tag, {}).get('units', {}).get(unit, []):
        if fact.get('end') != end or fact.get('filed', '9999') > as_of:
            continue
        if fact.get('form') not in ('10-K', '10-K/A'):
            continue
        if kind == 'duration' and fact.get('start') != start:
            continue
        if kind == 'instant' and fact.get('start'):
            continue
        candidates.append(fact)
    if not candidates:
        raise ValueError(f'Missing {tag} {year} {unit} as of {as_of}')
    newest = max(f['filed'] for f in candidates)
    latest = [f for f in candidates if f['filed'] == newest]
    if len({f['val'] for f in latest}) != 1:
        raise ValueError(f'Ambiguous {tag} for {year} filed {newest}; review filing')
    fact = sorted(latest, key=lambda f: f['accn'])[-1]
    finite(value=fact['val'])
    return dict(value=fact['val']/1e6 if unit == 'USD' else fact['val'],
                unit='USD million' if unit == 'USD' else unit, year=year,
                period_start=fact.get('start'), period_end=end, status='disclosed',
                source=dict(url=url, tag=f'us-gaap:{tag}',
                            accession=fact['accn'], filed=fact['filed'],
                            original_value=fact['val'], original_unit=unit))
