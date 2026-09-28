# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

import json
from pathlib import Path
import tempfile

from behave import given, then, when

from bizplan.insurance.pipeline import build
from bizplan.insurance.report_pdf import collect_report_data


ROOT = Path(__file__).resolve().parents[2]


@given('a validated Travelers insurance research run')
def research_run(context):
    context.report_tmp = tempfile.TemporaryDirectory()
    context.add_cleanup(context.report_tmp.cleanup)
    context.report_dir = Path(context.report_tmp.name)
    build(ROOT / 'examples/travelers/actuals.json', context.report_dir, '2026-02-12')
    context.report_research = json.loads((context.report_dir / 'research.json').read_text())
    (context.report_dir / 'manifest.json').write_text(json.dumps({
        'status': 'complete', 'run_id': 'bdd-run', 'git_revision': 'bdd'}))


@when('the insurance report data is prepared')
def prepare(context):
    context.report_data = collect_report_data(ROOT, context.report_dir)


@then('six audited annual periods are included in the report')
def history(context):
    assert [row['year'] for row in context.report_data['annual']] == list(range(2020, 2026))


@then('the report distinguishes February history from April disposal evidence')
def cutoffs(context):
    assert context.report_data['as_of'] == '2026-02-12'
    assert context.report_data['later_as_of'] == '2026-04-16'


@then('no price target or rating is published')
def unrated(context):
    assert context.report_research['valuation'] is None
    assert context.report_data['warning'].startswith('2026-2030 scenarios')
