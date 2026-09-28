"""Source-led Travelers research-status PDF from validated insurance outputs."""
from datetime import date
from hashlib import sha256
from html import escape
import json
from pathlib import Path


def collect_report_data(root, run_dir):
    root, run_dir = Path(root), Path(run_dir)
    base = root / 'examples/travelers'
    read = lambda path: json.loads(Path(path).read_text())
    history = read(base / 'historical_actuals.json')
    statements = read(base / 'statement_controls.json')
    integrated = read(base / 'historical_integration.json')
    operating = read(base / 'operating_movements.json')
    early = read(base / 'canadian_disposal_2026-02-12.json')
    later = read(base / 'canadian_disposal_2026-04-16.json')
    forecast = read(base / 'operating_forecast_reference.json')
    inventory = read(base / 'source_inventory.json')
    fingerprint = sha256()
    source_paths = sorted((root / 'bizplan/insurance').glob('*.py'))
    source_paths += sorted(base.glob('*.json'))
    for path in source_paths:
        fingerprint.update(str(path.relative_to(root)).encode())
        fingerprint.update(path.read_bytes())
    research = read(run_dir / 'research.json')
    manifest = read(run_dir / 'manifest.json')
    if (manifest['status'] != 'complete' or research['valuation'] is not None or
            research['status'] != 'partial_historical_research'):
        raise ValueError('Research run is not a validated partial insurance run')
    for document in (history, statements, integrated, operating):
        if document['company'] != 'TRV' or document['as_of'] != '2026-02-12':
            raise ValueError('Inconsistent historical issuer or cutoff')
        if any(check['status'] not in ('pass', 'open') for check in document['checks'] if 'status' in check):
            raise ValueError('Historical accounting check failed')
    if (early['as_of'] != '2026-02-12' or later['as_of'] != '2026-04-16' or
            forecast['forecast_scope'] != 'constant_fy2025_perimeter_excludes_2026_canadian_disposal'):
        raise ValueError('Disposal or forecast information boundary mismatch')
    for document in (early, later):
        if any(check['status'] != 'pass' for check in document['checks']):
            raise ValueError('Disposal check failed')
    h = {(item['year'], item['metric']): item['value'] for item in history['facts']}
    s = {(item['year'], item['metric']): item['value'] for item in statements['facts']}
    annual = []
    source_inventory = {item['id']: item for item in inventory['sources']}
    source_rows = []

    def source_ref(fact):
        source = source_inventory[fact['source_id']]
        if source['url'] != fact['source_pdf_url']:
            raise ValueError('Report fact does not match the source inventory')
        return dict(label=f"FY{source['fiscal_year']} report, p.{fact['pdf_page']}",
                    url=source['url'], source_id=fact['source_id'])

    source_rows.append(dict(year=2019, premium=None,
                            reserves=source_ref(next(item for item in history['facts']
                                                     if item['year'] == 2019 and item['metric'] == 'net_reserves')),
                            income=None))
    for year in range(2020, 2026):
        annual.append(dict(year=year, gwp=h[year, 'gwp'], nwp=h[year, 'nwp'],
                           nep=h[year, 'nep'], net_reserves=h[year, 'net_reserves'],
                           net_income=s[year, 'net_income']))
        premiums = [source_ref(next(item for item in history['facts']
                                    if item['year'] == year and item['metric'] == metric))
                    for metric in ('gwp', 'nwp', 'nep')]
        if len({(item['source_id'], item['label']) for item in premiums}) != 1:
            raise ValueError('Report premiums do not share one cited source page')
        source_rows.append(dict(year=year, premium=premiums[0],
                                reserves=source_ref(next(item for item in history['facts']
                                                         if item['year'] == year and item['metric'] == 'net_reserves')),
                                income=source_ref(next(item for item in statements['facts']
                                                       if item['year'] == year and item['metric'] == 'net_income'))))
    cited_ids = {ref['source_id'] for row in source_rows for ref in
                 (row['premium'], row['reserves'], row['income']) if ref}
    annual_sources = [source_inventory[source_id] for source_id in sorted(
        cited_ids, key=lambda source_id: source_inventory[source_id]['fiscal_year'])]
    ratios = next(row['ratios'] for row in research['historical'] if row['year'] == 2025)
    scenarios = {name: case[-1] for name, case in forecast['cases'].items()}
    if set(scenarios) != {'Base', 'Upside', 'Downside'}:
        raise ValueError('Incomplete illustrative cases')
    return dict(as_of=history['as_of'], later_as_of=later['as_of'],
                generated=date.today().isoformat(), run_id=manifest['run_id'],
                source_fingerprint=fingerprint.hexdigest(),
                annual=annual, annual_source_rows=source_rows,
                annual_sources=annual_sources,
                ratios_2025=ratios, scenarios_2030=scenarios,
                opening_2019=h[2019, 'net_reserves'],
                investments_2025=s[2025, 'total_investments'],
                cash_2025=s[2025, 'cash'],
                book_net_assets=early['derived']['disposed_net_assets_book'],
                continuing_net_reserves=later['derived']['continuing_net_claim_reserves_opening'],
                continuing_nwp=later['derived']['continuing_2025_nwp_comparable'],
                continuing_nep=later['derived']['continuing_2025_nep_comparable'],
                disposed_recovery_implied=later['derived']['disposed_unpaid_claim_recoverables_implied'],
                disposal_cash_proceeds=next(item['value'] for item in later['facts']
                                             if item['metric'] == 'cash_proceeds_q1_2026'),
                controls=dict(historical=sum(check.get('status') == 'pass'
                                             for document in (history, statements, integrated, operating)
                                             for check in document['checks']),
                              open=sum(check.get('status') == 'open'
                                       for document in (history, statements, integrated, operating)
                                       for check in document['checks']),
                              disposal_feb=len(early['checks']), disposal_apr=len(later['checks'])),
                warning='2026-2030 scenarios retain the FY2025 business perimeter and exclude the Canadian sale.',
                sources=(
                    ('FY2025 Form 10-K', 'https://www.sec.gov/Archives/edgar/data/86312/000008631226000065/trv-20251231.htm'),
                    ('Q1 2026 Form 10-Q', 'https://www.sec.gov/Archives/edgar/data/86312/000008631226000111/trv-20260331.htm'),
                    ('Q1 2026 webcast presentation', 'https://s26.q4cdn.com/410417801/files/doc_financials/2026/q1/1Q26-Webcast-FINAL.pdf')))


def render_report(data, output_path):
    """Render the reviewed status report; reportlab is only needed for PDF output."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    navy, blue, pale, gray = colors.HexColor('#16324F'), colors.HexColor('#245A81'), colors.HexColor('#E7F0F6'), colors.HexColor('#52606D')
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TitleTRV', parent=styles['Title'], fontName='Helvetica-Bold',
                              fontSize=21, leading=25, textColor=navy, spaceAfter=11))
    styles.add(ParagraphStyle(name='DeckTRV', parent=styles['Normal'], fontName='Helvetica',
                              fontSize=10, leading=15, textColor=gray, spaceAfter=13))
    styles.add(ParagraphStyle(name='SectionTRV', parent=styles['Heading2'], fontName='Helvetica-Bold',
                              fontSize=12.5, leading=16, textColor=navy, spaceBefore=14, spaceAfter=7))
    styles.add(ParagraphStyle(name='BodyTRV', parent=styles['Normal'], fontName='Helvetica',
                              fontSize=9, leading=13.5, textColor=colors.HexColor('#23303D'), spaceAfter=8))
    styles.add(ParagraphStyle(name='SmallTRV', parent=styles['Normal'], fontName='Helvetica',
                              fontSize=7.5, leading=10.5, textColor=gray, spaceAfter=5))
    styles.add(ParagraphStyle(name='CalloutTRV', parent=styles['Normal'], fontName='Helvetica-Bold',
                              fontSize=10, leading=14, textColor=navy))
    styles.add(ParagraphStyle(name='TableHeadTRV', parent=styles['Normal'], fontName='Helvetica-Bold',
                              fontSize=8.3, leading=10.5, textColor=colors.white))
    body = lambda t: Paragraph(t, styles['BodyTRV'])
    small = lambda t: Paragraph(t, styles['SmallTRV'])
    section = lambda t: Paragraph(t, styles['SectionTRV'])
    n = lambda x: f'{x:,.0f}'

    def table(rows, widths, header=True):
        if header:
            rows = [[Paragraph(str(cell).replace('&', '&amp;'), styles['TableHeadTRV'])
                     for cell in rows[0]]] + rows[1:]
        result = Table(rows, colWidths=widths, repeatRows=1 if header else 0, hAlign='LEFT')
        commands = [('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 7),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 7),
                    ('TOPPADDING', (0, 0), (-1, -1), 7),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
                    ('LINEBELOW', (0, -1), (-1, -1), .5, colors.HexColor('#B9C8D4'))]
        if header:
            commands += [('BACKGROUND', (0, 0), (-1, 0), navy),
                         ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                         ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, pale])]
        result.setStyle(TableStyle(commands))
        return result

    story = [Paragraph('THE TRAVELERS COMPANIES', styles['TitleTRV']),
             Paragraph('Equity research status | P&amp;C operating model | NYSE: TRV', styles['DeckTRV']),
             table([[Paragraph('RESEARCH STATUS', styles['CalloutTRV']),
                     Paragraph('Historical analysis only. No rating, price target or investment recommendation.', styles['BodyTRV'])]],
                   [1.5*inch, 5.2*inch], header=False), Spacer(1, 11),
             body(f"The model uses audited annual history through FY2025 with an information cutoff of {data['as_of']}. "
                  f"A separately dated Canadian disposal bridge incorporates disclosures available by {data['later_as_of']}; "
                  "those later facts are not inserted into the February workbook forecast."),
             section('Six-year financial history'),
             small('USD millions. Net P&amp;C reserves are reserve-rollforward amounts; 2025 includes the disposal group before the January 2026 sale.'),
             table([['Fiscal year', 'GWP', 'NWP', 'NEP', 'Net P&C reserves', 'Net income']] +
                   [[str(r['year']), n(r['gwp']), n(r['nwp']), n(r['nep']),
                     n(r['net_reserves']), n(r['net_income'])] for r in data['annual']],
                   [.78*inch, 1.05*inch, 1.05*inch, 1.05*inch, 1.55*inch, 1.2*inch]),
             Spacer(1, 10),
             body(f"FY2025 gross written premiums were ${n(data['annual'][-1]['gwp'])}m, "
                  f"net earned premiums ${n(data['annual'][-1]['nep'])}m and net income "
                  f"${n(data['annual'][-1]['net_income'])}m. The Travelers-specific calculated "
                  f"combined ratio was {data['ratios_2025']['combined_ratio']:.1%}."),
             section('What the historical model establishes'),
             body(f"The 2019 opening net P&amp;C claims reserve was ${n(data['opening_2019'])}m. "
                  f"At FY2025, the audited balance sheet reported ${n(data['investments_2025'])}m "
                  f"of investments and ${n(data['cash_2025'])}m of cash. "
                  "Premium, claims-reserve, income, balance-sheet, cash and equity controls are "
                  "reconciled in the source-linked workbook; unresolved stock movements remain visible."),
             PageBreak(),
             Paragraph('CANADIAN DISPOSAL', styles['TitleTRV']),
             Paragraph('A dated bridge, not an assumed sale gain', styles['DeckTRV']),
             section('Information available by February 12, 2026'),
             body(f"The FY2025 Form 10-K classified $4,550m of assets and $2,542m of "
                  f"liabilities as held for sale, or ${n(data['book_net_assets'])}m of book net assets. "
                  "The disclosed classes include $3,243m of fixed maturities, $285m of "
                  "reinsurance recoverables, $1,909m of gross claims reserves and $514m of "
                  "gross unearned premiums. The consolidated investments, cash and gross UPR "
                  "balance-sheet lines already exclude these separately presented items."),
             section('Subsequent April 16, 2026 evidence'),
             body(f"The Q1 2026 Form 10-Q reported $1,627m of net claims reserves disposed "
                  f"and ${n(data['disposal_cash_proceeds'])}m of cash proceeds. Applying the "
                  f"reserve disposal movement to FY2025 produces a ${n(data['continuing_net_reserves'])}m "
                  "continuing opening net P&amp;C reserve basis. Comparing the December gross "
                  f"and Q1 net reserve measures implies ${n(data['disposed_recovery_implied'])}m "
                  "of recoverables on unpaid claims; this split is inferred across dates."),
             table([['FY2025 premium basis (USD m)', 'Reported consolidated', 'Divested', 'Comparable continuing'],
                    ['Net written', n(data['annual'][-1]['nwp']), '989', n(data['continuing_nwp'])],
                    ['Net earned', n(data['annual'][-1]['nep']), '1,035', n(data['continuing_nep'])]],
                   [2.08*inch, 1.5*inch, 1.05*inch, 2.07*inch]), Spacer(1, 10),
             small('Divested premium amounts come from the Travelers Q1 2026 webcast presentation, PDF page 19. Comparable continuing values are analytical comparisons, not restated GAAP actuals.'),
             body('Cash proceeds less December book net assets is $376m, but this is not the reported accounting gain. '
                  'Closing adjustments, tax, transaction costs and foreign-currency translation remain to be reconciled.'),
             PageBreak(),
             Paragraph('MODEL OUTLOOK AND GATES', styles['TitleTRV']),
             Paragraph('Illustrative operating cases only', styles['DeckTRV']),
             body(data['warning']),
             table([['2030 illustrative case', 'Net earned premiums', 'Net P&C reserves', 'Combined ratio']] +
                   [[case, n(value['premiums']['nep']), n(value['reserves']['closing_net']),
                     f"{value['combined_ratio']:.1%}"]
                    for case, value in data['scenarios_2030'].items()],
                   [1.65*inch, 1.65*inch, 1.8*inch, 1.6*inch]), Spacer(1, 12),
             section('Valuation and research status'),
             body('No share-price input, calibrated catastrophe distribution, integrated forecast three statements, '
                  'capital constraint or reconciled transaction gain is in this run. The report therefore makes '
                  'no valuation, price target or investment recommendation. The current operating cases cannot '
                  'be treated as a Travelers-specific post-disposal forecast.'),
             section('Validation and provenance'),
             body(f"The release build passed {data['controls']['historical']} historical controls, "
                  f"{data['controls']['disposal_feb']} February disposal checks and "
                  f"{data['controls']['disposal_apr']} later disposal checks. "
                  f"{data['controls']['open']} premium-earning bridges remain open. The workbook also "
                  "compares 135 forecast cell values with the Python operating projection across three cases."),
             small(f"Run ID: {data['run_id']} | Source fingerprint: {data['source_fingerprint'][:12]} | Generated: {data['generated']}"),
             section('Primary sources')]
    for title, url in data['sources']:
        story.append(small(f'<link href="{url}" color="#245A81">{title}</link><br/>{url}'))
    story.append(small('Full line-level provenance and unresolved bridges are in the accompanying workbook and repository source JSON.'))
    story += [PageBreak(), Paragraph('HISTORICAL SOURCE MAP', styles['TitleTRV']),
              Paragraph('Direct source pages for the six-year table', styles['DeckTRV']),
              body('The historical table on page 1 combines comparative figures from several annual reports. '
                   'Each linked page below identifies the source used for that year and metric. GWP is derived '
                   'from the direct and assumed written premium rows on the cited page.'),
              small('The 2019 row supports the opening net P&amp;C reserve only. Premium source applies to GWP, NWP and NEP.'),
              table([['Fiscal year', 'Premiums', 'Net P&C reserves', 'Net income']] +
                    [[str(row['year'])] +
                     [Paragraph(f'<link href="{escape(ref["url"], quote=True)}" color="#245A81">'
                                f'{escape(ref["label"])}</link>', styles['SmallTRV']) if ref else '-'
                      for ref in (row['premium'], row['reserves'], row['income'])]
                     for row in data['annual_source_rows']],
                    [.72*inch, 2*inch, 2.05*inch, 1.93*inch]),
              section('Annual report documents')]
    for source in data['annual_sources']:
        story.append(small(f'<link href="{escape(source["url"], quote=True)}" color="#245A81">'
                           f'FY{source["fiscal_year"]} issuer annual report</link>: '
                           f'{escape(source["url"])}'))
    story.append(small('These are issuer annual-report PDF copies. Selected 2022-2025 rows have been '
                       'compared with original SEC HTML; remaining original-row checks and exact PDF posting dates '
                       'are pending. The report does not promote those open rows to a valuation.'))

    def page(canvas, document):
        canvas.saveState()
        width, height = document.pagesize
        canvas.setStrokeColor(colors.HexColor('#B9C8D4'))
        canvas.line(43, 42, width-43, 42)
        canvas.setFont('Helvetica', 7.5)
        canvas.setFillColor(gray)
        canvas.drawString(43, 29, 'TRV | Historical research status | USD millions unless noted')
        canvas.drawRightString(width-43, 29, f'{document.page}')
        canvas.restoreState()

    doc = SimpleDocTemplate(str(output_path), pagesize=(612, 792),
                            leftMargin=43, rightMargin=43, topMargin=42, bottomMargin=54,
                            title='Travelers Equity Research Status',
                            author='Insurance research harness')
    doc.build(story, onFirstPage=page, onLaterPages=page)
    return output_path
