"""Dated Canadian disposal bridge; never treats later evidence as earlier knowledge."""
from datetime import date
from hashlib import sha256
import json
from pathlib import Path


HFS_ASSETS = ('hfs_fixed_maturities', 'hfs_premium_receivables',
              'hfs_reinsurance_recoverables', 'hfs_goodwill', 'hfs_remaining_assets')
HFS_LIABILITIES = ('hfs_claim_reserves_gross', 'hfs_unearned_premium_gross',
                   'hfs_remaining_liabilities')
SEGMENTS = ('business', 'bond_specialty', 'personal')
BASE_METRICS = set(HFS_ASSETS + HFS_LIABILITIES +
                   ('hfs_assets_total', 'hfs_liabilities_total'))
LATER_METRICS = {'cash_proceeds_q1_2026', 'net_claim_reserves_disposed_q1_2026',
                 'divested_nwp_total_2025', 'divested_nep_total_2025'} | {
                     f'divested_{basis}_{segment}_2025'
                     for basis in ('nwp', 'nep') for segment in SEGMENTS}


def build_disposal_bridge(raw, history, statements, integrated, as_of):
    """Reconcile disclosed disposal facts to history without filling missing splits."""
    cutoff = date.fromisoformat(as_of)
    if (raw['company'] != history['company'] or raw['company'] != statements['company']
            or raw['company'] != integrated['company']):
        raise ValueError('Disposal issuer mismatch')
    if raw['unit'] != 'USD million' or raw['transaction_date'] != '2026-01-02':
        raise ValueError('Disposal unit or transaction date mismatch')
    sources = raw['sources']
    if set(sources) != {'fy2025_10k', 'q1_2026_10q', 'q1_2026_webcast'}:
        raise ValueError('Unexpected disposal sources')
    for source in sources.values():
        date.fromisoformat(source['available_at'])
        if not source['url'] or not source['locator']:
            raise ValueError('Missing disposal source provenance')
    all_facts = {}
    for fact in raw['facts']:
        metric, source_id, value = fact['metric'], fact['source'], fact['value']
        if metric in all_facts or source_id not in sources or (
                isinstance(value, bool) or not isinstance(value, (int, float))):
            raise ValueError(f'Invalid or duplicate disposal fact: {metric}')
        if metric in BASE_METRICS and source_id != 'fy2025_10k':
            raise ValueError(f'Wrong source for held-for-sale fact: {metric}')
        if metric in {'cash_proceeds_q1_2026', 'net_claim_reserves_disposed_q1_2026'} and source_id != 'q1_2026_10q':
            raise ValueError(f'Wrong source for quarterly fact: {metric}')
        if metric.startswith('divested_') and source_id != 'q1_2026_webcast':
            raise ValueError(f'Wrong source for premium fact: {metric}')
        all_facts[metric] = fact
    if set(all_facts) != BASE_METRICS | LATER_METRICS:
        raise ValueError('Disposal fact set incomplete or unexpected')
    available = {metric: fact['value'] for metric, fact in all_facts.items()
                 if date.fromisoformat(sources[fact['source']]['available_at']) <= cutoff}
    if not BASE_METRICS <= available.keys():
        raise ValueError('FY2025 disposal note unavailable at cutoff')
    checks = []

    def check(metric, actual, expected):
        difference = actual - expected
        checks.append(dict(metric=metric, actual=actual, expected=expected,
                           difference=difference, status='pass' if difference == 0 else 'fail'))
        if difference:
            raise ValueError(f'Disposal {metric} mismatch: {difference}')

    f = lambda metric: available[metric]
    controls = {(fact['year'], fact['metric']): fact['value']
                for fact in statements['facts'] + integrated['facts']}
    historical = {(fact['year'], fact['metric']): fact['value'] for fact in history['facts']}
    check('held_for_sale_asset_classes', sum(f(m) for m in HFS_ASSETS), f('hfs_assets_total'))
    check('held_for_sale_liability_classes', sum(f(m) for m in HFS_LIABILITIES), f('hfs_liabilities_total'))
    check('balance_sheet_hfs_assets', f('hfs_assets_total'), controls[2025, 'assets_held_for_sale'])
    check('balance_sheet_hfs_liabilities', f('hfs_liabilities_total'), controls[2025, 'liabilities_held_for_sale'])
    check('reserve_table_hfs_claims', f('hfs_claim_reserves_gross'), historical[2025, 'held_for_sale_reserves'])
    check('premium_table_hfs_upr', f('hfs_unearned_premium_gross'), historical[2025, 'held_for_sale_upr'])
    check('reinsurance_table_hfs_asset', f('hfs_reinsurance_recoverables'), historical[2025, 'held_for_sale_recoverables'])
    derived = {'disposed_net_assets_book': f('hfs_assets_total') - f('hfs_liabilities_total'),
               'continuing_gross_claim_reserves_opening':
                   historical[2025, 'gross_reserves'] - f('hfs_claim_reserves_gross'),
               'gross_upr_opening_already_excludes_hfs': historical[2025, 'gross_upr'],
               'investment_balance_opening_already_excludes_hfs': controls[2025, 'total_investments'],
               'cash_balance_opening_already_excludes_hfs': controls[2025, 'cash']}
    open_items = ['Exact transaction gain, tax and cash retained/reinvested',
                  'Divested gross written premiums and ceded written premiums',
                  'Divested ceded unearned premiums and other operating assets/liabilities']
    if LATER_METRICS <= available.keys():
        for basis in ('nwp', 'nep'):
            check(f'divested_{basis}_segments',
                  sum(f(f'divested_{basis}_{segment}_2025') for segment in SEGMENTS),
                  f(f'divested_{basis}_total_2025'))
        gross_disposed = f('hfs_claim_reserves_gross')
        net_disposed = f('net_claim_reserves_disposed_q1_2026')
        implied_unpaid_recovery = gross_disposed - net_disposed
        derived.update(
            disposed_unpaid_claim_recoverables_implied=implied_unpaid_recovery,
            held_for_sale_reinsurance_other_than_unpaid_implied=
                f('hfs_reinsurance_recoverables') - implied_unpaid_recovery,
            continuing_net_claim_reserves_opening=historical[2025, 'net_reserves'] - net_disposed,
            continuing_unpaid_claim_recoverables_opening=
                historical[2025, 'unpaid_recoverables'] - implied_unpaid_recovery,
            continuing_2025_nwp_comparable=historical[2025, 'nwp'] - f('divested_nwp_total_2025'),
            continuing_2025_nep_comparable=historical[2025, 'nep'] - f('divested_nep_total_2025'),
            cash_proceeds_less_2025_disposal_book_net_assets_diagnostic=
                f('cash_proceeds_q1_2026') - derived['disposed_net_assets_book'])
        check('continuing_gross_net_reinsurance',
              derived['continuing_net_claim_reserves_opening'] +
              derived['continuing_unpaid_claim_recoverables_opening'],
              derived['continuing_gross_claim_reserves_opening'])
        if implied_unpaid_recovery < 0 or derived['held_for_sale_reinsurance_other_than_unpaid_implied'] < 0:
            raise ValueError('Disposed reinsurance basis is inconsistent')
        status = 'post_cutoff_partial_operating_rebase_no_gain_or_forecast'
    else:
        status = 'cutoff_held_for_sale_balance_only'
        open_items.insert(0, 'Q1 net reserves disposed, cash proceeds and FY2025 premium carveout postdate cutoff')
    periods = {'fy2025_10k': ('instant', None, '2025-12-31'),
               'q1_2026_10q': ('duration', '2026-01-01', '2026-03-31'),
               'q1_2026_webcast': ('duration', '2025-01-01', '2025-12-31')}
    facts = []
    for metric, fact in all_facts.items():
        if metric not in available:
            continue
        period_type, period_start, period_end = periods[fact['source']]
        facts.append(dict(metric=metric, value=fact['value'], unit=raw['unit'],
                          period_type=period_type, period_start=period_start,
                          period_end=period_end, source_id=fact['source'],
                          **sources[fact['source']]))
    return dict(schema_version=1, company=raw['company'], as_of=as_of,
                transaction_date=raw['transaction_date'], status=status,
                facts=sorted(facts, key=lambda item: item['metric']),
                checks=checks, derived=derived, open_items=open_items,
                boundary='A later disclosure never enters an earlier cutoff. Cash proceeds less book net assets is not an accounting gain.')


def write_disposal_bridge(raw_path, history_path, statement_path, integrated_path,
                          output_path, as_of):
    paths = (raw_path, history_path, statement_path, integrated_path)
    raw, history, statements, integrated = (json.loads(Path(path).read_text()) for path in paths)
    result = build_disposal_bridge(raw, history, statements, integrated, as_of)
    result['input_hashes'] = {str(Path(path)): sha256(Path(path).read_bytes()).hexdigest()
                              for path in paths}
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    return result
