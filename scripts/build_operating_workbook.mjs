/** Formula-linked P&C actuals and illustrative operating forecast. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root = path.resolve(import.meta.dirname, '..');
const outputPath = path.resolve(process.argv[2] || path.join(root, 'output/travelers_operating_model.xlsx'));
const read = async name => JSON.parse(await fs.readFile(path.join(root, 'examples/travelers', name), 'utf8'));
const [history, statements, operating, integrated, scenarioInputs, forecastReference] = await Promise.all([
  read('historical_actuals.json'), read('statement_controls.json'), read('operating_movements.json'),
  read('historical_integration.json'),
  read('operating_scenarios.json'), read('operating_forecast_reference.json'),
]);
const runId = createHash('sha256').update(JSON.stringify({history:history.input_hashes,
  statements:statements.input_hashes,operating:operating.input_hashes,
  integrated:integrated.input_hashes,
  scenarios:scenarioInputs,forecast:forecastReference})).digest('hex').slice(0,12);
if (history.company !== statements.company || history.company !== operating.company ||
    history.company !== integrated.company || history.company !== scenarioInputs.company ||
    history.company !== forecastReference.company || history.as_of !== '2026-02-12' ||
    statements.as_of !== '2026-02-12' || operating.as_of !== '2026-02-12' ||
    integrated.as_of !== '2026-02-12' ||
    scenarioInputs.forecast_scope !== 'constant_fy2025_perimeter_excludes_2026_canadian_disposal' ||
    forecastReference.forecast_scope !== scenarioInputs.forecast_scope) {
  throw new Error('Workbook input issuer/cutoff mismatch');
}

const sections = [
  ['Premiums and earning', [
    ['direct_written','Direct written premiums'],['assumed_written','Assumed written premiums'],
    ['gwp','Gross written premiums'],['ceded_written','Ceded written premiums'],
    ['nwp','Net written premiums'],['gross_upr','Gross unearned premiums'],
    ['ceded_upr','Ceded unearned premiums'],['net_upr','Net unearned premiums'],
    ['held_for_sale_upr','Gross UPR held for sale'],['gross_earned','Gross earned premiums'],
    ['ceded_earned','Ceded earned premiums'],['nep','Net earned premiums'],
    ['gross_premium_earning_gap','Gross premium earning difference'],
    ['ceded_premium_earning_gap','Ceded premium earning difference'],
    ['net_premium_earning_gap','Net premium earning difference'],
  ]],
  ['Claims and P&C reserves', [
    ['current_incurred','Current accident-year incurred'],
    ['reserve_prior_incurred','Prior accident-year incurred adjustment'],
    ['reported_total_incurred','Total reserve-table incurred'],
    ['paid_current','Paid current-year claims'],['paid_prior','Paid prior-year claims'],
    ['reported_total_paid','Total claims paid'],['reserve_fx_other','Reserve FX and other'],
    ['adoption_change','Accounting adoption adjustment'],['net_reserves','Net P&C claims reserves'],
    ['unpaid_recoverables','Recoverables on unpaid P&C claims'],
    ['gross_reserves','Gross P&C claims reserves'],
    ['reserve_rollforward_check','Reserve rollforward difference'],
  ]],
  ['Reinsurance presentation', [
    ['total_recoverables','Balance-sheet reinsurance recoverables'],
    ['recoverable_scope_difference','Total less unpaid recoverables; scopes differ'],
    ['held_for_sale_recoverables','Recoverables held for sale'],
  ]],
  ['Acquisition costs and GAAP expenses', [
    ['dac','Deferred acquisition costs'],['dac_cash_additions','Cash-flow DAC additions'],
    ['dac_amortization','DAC amortization'],['dac_stock_gap','DAC stock difference'],
    ['general_admin','General and administrative expenses'],['claims','GAAP claims and LAE'],
    ['underwriting_expense_proxy','Illustrative forecast underwriting expenses'],
  ]],
  ['Investment portfolio', [
    ['fixed_maturity_fair','Fixed maturities at fair value'],
    ['equity_investments','Equity securities'],['real_estate_investments','Real estate investments'],
    ['short_term_investments','Short-term investments'],['other_investments','Other investments'],
    ['total_investments','Total investments'],['investment_cash_purchases','Investment cash purchases'],
    ['investment_cash_proceeds','Investment maturity and sale proceeds'],
    ['short_term_net_sales','Net sales of short-term securities'],
    ['investment_cash_proxy_gap','Investment balance less cash proxy'],
    ['investment_income','Net investment income'],['average_investments','Average invested assets'],
    ['investment_yield','Investment income / average investments'],
  ]],
  ['Common equity', [
    ['opening_equity','Opening common equity'],['net_income','Net income'],
    ['total_oci','Other comprehensive income'],['employee_shares_equity','Employee share issuances'],
    ['stock_comp_and_other_equity','Share compensation and other'],
    ['retained_earnings_other','Other retained earnings'],['adoption_equity','Accounting adoption'],
    ['equity_dividends','Declared dividends'],['equity_buybacks_authorized','Authorized buybacks'],
    ['equity_employee_treasury','Employee treasury shares'],['closing_equity','Closing common equity'],
    ['equity_rollforward_check','Equity rollforward difference'],['closing_shares','Ending common shares, millions'],
  ]],
  ['Debt and cash', [
    ['debt','Debt outstanding'],['debt_issuance','Cash debt issuance'],
    ['debt_repayment','Cash debt repayment'],['debt_stock_gap','Debt stock difference'],
    ['cfo','Cash from operations'],['cfi','Cash from investing'],
    ['cff','Cash from financing'],['cash_fx','FX effect on cash'],
    ['cash_held_for_sale_reclassification','Cash held for sale'],['cash','Balance-sheet cash'],
    ['cash_rollforward_check','Cash rollforward difference'],
  ]],
  ['GAAP income statement integration', [
    ['fee_income','Fee income'],['realized_gains','Net realized investment gains / losses'],
    ['other_revenue','Other revenues'],['total_revenue','Total revenues'],
    ['interest_expense','Interest expense'],['total_expenses','Total claims and expenses'],
    ['pretax_income','Income before tax'],['tax_expense','Income tax expense'],
    ['income_revenue_check','Revenue line difference'],
    ['income_expense_check','Expense line difference'],
    ['income_net_check','Net income line difference'],
    ['income_cash_check','Income versus cash-flow net income'],
  ]],
  ['GAAP balance sheet integration', [
    ['accrued_investment_income','Investment income accrued'],
    ['premium_receivables','Premium receivables'],
    ['deferred_tax_asset','Deferred tax assets'],
    ['contractholder_receivables','Contractholder receivables'],
    ['goodwill','Goodwill'],['intangible_assets','Other intangible assets'],
    ['other_assets','Other assets'],['assets_held_for_sale','Assets held for sale'],
    ['total_assets','Total assets'],
    ['balance_sheet_claim_reserves','Balance-sheet claims reserves'],
    ['contractholder_payables','Contractholder payables'],
    ['reinsurance_premium_payables','Reinsurance premium payables'],
    ['deferred_tax_liability','Deferred tax liabilities'],
    ['other_liabilities','Other liabilities'],
    ['liabilities_held_for_sale','Liabilities held for sale'],
    ['total_liabilities','Total liabilities'],
    ['common_stock','Common stock'],['retained_earnings','Retained earnings'],
    ['aoci','Accumulated other comprehensive income'],
    ['treasury_stock','Treasury stock at cost'],
    ['balance_assets_check','Asset line difference'],
    ['balance_liabilities_check','Liability line difference'],
    ['balance_equity_check','Equity component difference'],
    ['balance_equation_check','Assets less liabilities and equity'],
  ]],
];
const row = {}, layout = [];
let nextRow = 10;
for (const [section, metrics] of sections) {
  layout.push({section, row: nextRow++});
  for (const [id, label] of metrics) {
    if (row[id]) throw new Error(`Duplicate model row ${id}`);
    row[id] = nextRow;
    layout.push({id, label, section, row: nextRow++});
  }
  nextRow += 2;
}
const col = y => String.fromCharCode('G'.charCodeAt(0) + y - 2019);
const book = Workbook.create();
for (const name of ['Cover','Summary','Assumptions','Scenarios','Model','Output','Sources']) book.worksheets.add(name);
const sheet = name => book.worksheets.getItem(name);
const put = (s, address, value) => s.getRange(address).values = [[value]];
const formula = (s, address, value) => s.getRange(address).formulas = [[value]];
const link = (y, metric) => {
  const index = sourceRows.get(`${y}|${metric}`);
  if (!index) throw new Error(`Missing source fact ${y} ${metric}`);
  return `=Sources!C${index}`;
};
const model = sheet('Model');
const sources = sheet('Sources');
const sourceRows = new Map();
const sourceFacts = new Map();
for (const fact of [...history.facts, ...statements.facts, ...operating.facts, ...integrated.facts]) {
  const key = `${fact.year}|${fact.metric}`;
  if (sourceFacts.has(key)) {
    if (sourceFacts.get(key).value !== fact.value) throw new Error(`Conflicting source facts ${key}`);
    continue;
  }
  sourceFacts.set(key, fact);
}
const orderedFacts = [...sourceFacts.values()].sort((a,b) => a.year-b.year || a.metric.localeCompare(b.metric));
sources.getRange('A1:J1').values = [['Year','Metric ID','Value','Status','Source ID','PDF page','SEC filed','Annual report PDF','SEC filing','PDF SHA-256']];
const ledger = orderedFacts.map((f,i) => {
  sourceRows.set(`${f.year}|${f.metric}`, i+2);
  return [f.year,f.metric,f.value,f.status,f.source_id || '',f.pdf_page || '',
          f.sec_filing_date || '',f.source_pdf_url || '',f.sec_filing_url || '',f.source_pdf_sha256 || ''];
});
sources.getRange(`A2:J${ledger.length+1}`).values = ledger;
sources.getRange(`C2:C${ledger.length+1}`).setNumberFormat('#,##0.0;(#,##0.0);–');
sources.getRange('A:A').format.columnWidth = 11;
sources.getRange('B:B').format.columnWidth = 39;
sources.getRange('C:C').format.columnWidth = 16;
sources.getRange('D:F').format.columnWidth = 15;
sources.getRange('G:G').format.columnWidth = 15;
sources.getRange('H:J').format.columnWidth = 38;
sources.freezePanes.freezeRows(1);

const navy = '#16324F', blue = '#245A81', pale = '#E7F0F6', orange = '#B65A22';
for (const name of ['Cover','Summary','Assumptions','Scenarios','Model','Output','Sources']) {
  const s = sheet(name); s.showGridLines = false;
  s.getRange('A1:R8').format.font = {name:'Arial', size:10, color:'#202C38'};
}
sources.getRange('A1:J1').format = {fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'}};
put(model,'C2','Travelers P&C operating model');
put(model,'C3','USD millions except shares and ratios · FY2020–25 actual · FY2026–30 illustrative');
formula(model,'C4','=Scenarios!D6');
model.getRange('C2').format.font = {name:'Arial',size:15,bold:true,color:navy};
model.getRange('C:C').format.columnWidth = 49;
model.getRange('D:F').format.columnWidth = 3;
model.getRange('G:R').format.columnWidth = 14;
model.getRange('G7:R7').values = [Array.from({length:12},(_,i)=>2019+i)];
model.getRange('G8:R8').values = [Array.from({length:12},(_,i)=>i===0?'Opening':i<=6?'Actual':'Forecast')];
model.getRange('G7:R8').format = {fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'}};
model.getRange(`G10:R${nextRow}`).setNumberFormat('#,##0.0;(#,##0.0);–');
model.freezePanes.freezeRows(8);
for (const item of layout) {
  put(model,`C${item.row}`,item.label || item.section);
  if (!item.id) model.getRange(`C${item.row}:R${item.row}`).format = {
    fill:pale,font:{name:'Arial',size:10,bold:true,color:navy}};
  else if (['gwp','nwp','nep','gross_reserves','net_reserves','total_investments','closing_equity','cash'].includes(item.id))
    model.getRange(`C${item.row}:R${item.row}`).format.font = {name:'Arial',size:10,bold:true,color:navy};
}
model.getRange(`N9:R${nextRow}`).format.borders = {left:{style:'thin',color:'#9DB7C9'}};

const f = (y,id,expr) => formula(model,`${col(y)}${row[id]}`,expr);
const v = (y,id) => `${col(y)}${row[id]}`;
const prior = (y,id) => `${col(y-1)}${row[id]}`;
const sourceActual = (y,id,sourceId=id) => {
  f(y,id,link(y,sourceId));
  model.getRange(`${col(y)}${row[id]}`).format.font = {name:'Arial',size:10,color:'#24704A'};
};
const stockIds = ['gross_upr','ceded_upr','net_upr','net_reserves','unpaid_recoverables',
  'gross_reserves','total_recoverables','dac','fixed_maturity_fair','equity_investments',
  'real_estate_investments','short_term_investments','other_investments','total_investments',
  'closing_equity','debt','cash'];
const detailIds = ['deferred_tax_asset','contractholder_receivables','goodwill',
  'intangible_assets','other_assets','assets_held_for_sale','contractholder_payables',
  'reinsurance_premium_payables','deferred_tax_liability','other_liabilities',
  'liabilities_held_for_sale','common_stock','retained_earnings','aoci','treasury_stock'];
const balanceControlIds = ['accrued_investment_income','premium_receivables',
  'total_assets','balance_sheet_claim_reserves','total_liabilities'];
const sumRefs = (y,ids) => `SUM(${ids.map(id=>v(y,id)).join(',')})`;
function addBalanceIntegration(y) {
  for (const id of [...detailIds,...balanceControlIds]) {
    if (sourceRows.has(`${y}|${id}`)) sourceActual(y,id);
  }
  const assets = ['total_investments','cash','accrued_investment_income',
    'premium_receivables','total_recoverables','ceded_upr','dac',
    'deferred_tax_asset','contractholder_receivables','goodwill','intangible_assets',
    'other_assets','assets_held_for_sale'];
  const liabilities = ['balance_sheet_claim_reserves','gross_upr','debt',
    'contractholder_payables','reinsurance_premium_payables','deferred_tax_liability',
    'other_liabilities','liabilities_held_for_sale'];
  f(y,'balance_assets_check',`=${sumRefs(y,assets)}-${v(y,'total_assets')}`);
  f(y,'balance_liabilities_check',`=${sumRefs(y,liabilities)}-${v(y,'total_liabilities')}`);
  f(y,'balance_equity_check',`=${sumRefs(y,['common_stock','retained_earnings','aoci','treasury_stock'])}-${v(y,'closing_equity')}`);
  f(y,'balance_equation_check',`=${v(y,'total_assets')}-${v(y,'total_liabilities')}-${v(y,'closing_equity')}`);
}
for (const id of stockIds) {
  if (id==='net_upr') f(2019,id,`=${v(2019,'gross_upr')}-${v(2019,'ceded_upr')}`);
  else if (id==='gross_reserves') f(2019,id,`=${v(2019,'net_reserves')}+${v(2019,'unpaid_recoverables')}`);
  else if (id==='total_investments') f(2019,id,`=SUM(${v(2019,'fixed_maturity_fair')},${v(2019,'equity_investments')},${v(2019,'real_estate_investments')},${v(2019,'short_term_investments')},${v(2019,'other_investments')})`);
  else sourceActual(2019,id,id==='closing_equity'?'equity':id);
}
addBalanceIntegration(2019);
for (let y=2020;y<=2025;y++) {
  for (const id of ['direct_written','assumed_written','ceded_written','gross_upr','ceded_upr',
    'gross_earned','ceded_earned','current_incurred','reserve_prior_incurred','paid_current',
    'paid_prior','reserve_fx_other','adoption_change','net_reserves','unpaid_recoverables',
    'total_recoverables','dac','dac_cash_additions','dac_amortization','general_admin','claims',
    'fixed_maturity_fair','equity_investments','real_estate_investments',
    'short_term_investments','other_investments','investment_income',
    'net_income','total_oci','employee_shares_equity','stock_comp_and_other_equity',
    'retained_earnings_other','adoption_equity','equity_dividends','equity_buybacks_authorized',
    'equity_employee_treasury','closing_equity','closing_shares','debt','debt_issuance',
    'debt_repayment','cfo','cfi','cff','cash_fx','cash']) sourceActual(y,id);
  f(y,'opening_equity',`=${prior(y,'closing_equity')}`);
  for (const id of ['held_for_sale_upr','held_for_sale_recoverables']) {
    if (y===2025) sourceActual(y,id);
  }
  if (y===2025) sourceActual(y,'cash_held_for_sale_reclassification');
  f(y,'gwp',`=${v(y,'direct_written')}+${v(y,'assumed_written')}`);
  f(y,'nwp',`=${v(y,'gwp')}-${v(y,'ceded_written')}`);
  f(y,'net_upr',`=${v(y,'gross_upr')}-${v(y,'ceded_upr')}`);
  f(y,'nep',`=${v(y,'gross_earned')}-${v(y,'ceded_earned')}`);
  f(y,'gross_premium_earning_gap',`=${v(y,'gross_earned')}-(${v(y,'gwp')}+${prior(y,'gross_upr')}-${v(y,'gross_upr')})`);
  f(y,'ceded_premium_earning_gap',`=${v(y,'ceded_earned')}-(${v(y,'ceded_written')}+${prior(y,'ceded_upr')}-${v(y,'ceded_upr')})`);
  f(y,'net_premium_earning_gap',`=${v(y,'gross_premium_earning_gap')}-${v(y,'ceded_premium_earning_gap')}`);
  f(y,'reported_total_incurred',`=${v(y,'current_incurred')}+${v(y,'reserve_prior_incurred')}`);
  f(y,'reported_total_paid',`=${v(y,'paid_current')}+${v(y,'paid_prior')}`);
  f(y,'gross_reserves',`=${v(y,'net_reserves')}+${v(y,'unpaid_recoverables')}`);
  f(y,'reserve_rollforward_check',`=${prior(y,'net_reserves')}+${v(y,'adoption_change')}+${v(y,'reported_total_incurred')}-${v(y,'reported_total_paid')}+${v(y,'reserve_fx_other')}-${v(y,'net_reserves')}`);
  f(y,'recoverable_scope_difference',`=${v(y,'total_recoverables')}-${v(y,'unpaid_recoverables')}`);
  f(y,'dac_stock_gap',`=${v(y,'dac')}-(${prior(y,'dac')}+${v(y,'dac_cash_additions')}-${v(y,'dac_amortization')})`);
  f(y,'total_investments',`=SUM(${v(y,'fixed_maturity_fair')},${v(y,'equity_investments')},${v(y,'real_estate_investments')},${v(y,'short_term_investments')},${v(y,'other_investments')})`);
  f(y,'investment_cash_purchases',`=SUM(${['fixed_maturity_purchases','equity_security_purchases','real_estate_purchases','other_investment_purchases'].map(id=>link(y,id).slice(1)).join(',')})`);
  f(y,'investment_cash_proceeds',`=SUM(${['fixed_maturity_maturities','fixed_maturity_sale_proceeds','equity_security_sale_proceeds','real_estate_sale_proceeds','other_investment_sale_proceeds'].map(id=>link(y,id).slice(1)).join(',')})`);
  sourceActual(y,'short_term_net_sales');
  f(y,'investment_cash_proxy_gap',`=${v(y,'total_investments')}-${prior(y,'total_investments')}-(${v(y,'investment_cash_purchases')}-${v(y,'investment_cash_proceeds')}-${v(y,'short_term_net_sales')})`);
  f(y,'average_investments',`=(${v(y,'total_investments')}+${prior(y,'total_investments')})/2`);
  f(y,'investment_yield',`=${v(y,'investment_income')}/${v(y,'average_investments')}`);
  f(y,'equity_rollforward_check',`=${v(y,'opening_equity')}+SUM(${v(y,'net_income')},${v(y,'total_oci')},${v(y,'employee_shares_equity')},${v(y,'stock_comp_and_other_equity')},${v(y,'retained_earnings_other')},${v(y,'adoption_equity')})-SUM(${v(y,'equity_dividends')},${v(y,'equity_buybacks_authorized')},${v(y,'equity_employee_treasury')})-${v(y,'closing_equity')}`);
  f(y,'debt_stock_gap',`=${v(y,'debt')}-(${prior(y,'debt')}+${v(y,'debt_issuance')}-${v(y,'debt_repayment')})`);
  const hfs = y===2025 ? `-${v(y,'cash_held_for_sale_reclassification')}` : '';
  f(y,'cash_rollforward_check',`=${prior(y,'cash')}+SUM(${v(y,'cfo')},${v(y,'cfi')},${v(y,'cff')},${v(y,'cash_fx')})${hfs}-${v(y,'cash')}`);
  for (const id of ['fee_income','realized_gains','other_revenue',
                    'interest_expense','tax_expense']) sourceActual(y,id);
  f(y,'total_revenue',`=${sumRefs(y,['nep','investment_income','fee_income','realized_gains','other_revenue'])}`);
  f(y,'total_expenses',`=${sumRefs(y,['claims','dac_amortization','general_admin','interest_expense'])}`);
  f(y,'pretax_income',`=${v(y,'total_revenue')}-${v(y,'total_expenses')}`);
  f(y,'income_revenue_check',`=${v(y,'total_revenue')}-${link(y,'total_revenue').slice(1)}`);
  f(y,'income_expense_check',`=${v(y,'total_expenses')}-${link(y,'total_expenses').slice(1)}`);
  f(y,'income_net_check',`=${v(y,'pretax_income')}-${v(y,'tax_expense')}-${v(y,'net_income')}`);
  f(y,'income_cash_check',`=${v(y,'net_income')}-${link(y,'cash_flow_net_income').slice(1)}`);
  addBalanceIntegration(y);
}

const assumptions = sheet('Assumptions');
put(assumptions,'C2','Illustrative P&C forecast drivers');
put(assumptions,'C3','Analyst scenarios; not Travelers guidance or a valuation forecast');
formula(assumptions,'C5','=Scenarios!D6');
assumptions.getRange('C:C').format.columnWidth = 42;
assumptions.getRange('D:M').format.columnWidth = 3;
assumptions.getRange('N:R').format.columnWidth = 14;
assumptions.getRange('N7:R7').values = [[2026,2027,2028,2029,2030]];
assumptions.getRange('N7:R7').format = {fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'}};
const scenarioNames = ['Base','Upside','Downside'];
const drivers = [
  ['gwp_growth','GWP growth'],
  ['ceded_share','Ceded written / GWP'],
  ['closing_upr_share','Closing gross UPR / GWP'],
  ['attritional_loss_ratio','Current accident-year attritional loss / NEP'],
  ['catastrophe_loss_ratio','Current accident-year catastrophe loss / NEP'],
  ['development_share_opening_reserves','Prior-year incurred / opening net reserves'],
  ['current_year_paid_share','Current accident-year paid / incurred'],
  ['prior_year_paid_share','Prior accident-year paid / opening net reserves'],
  ['unpaid_recoverable_share_gross','Unpaid recoverables / gross reserves'],
  ['expense_ratio','Illustrative underwriting expense / NEP'],
];
const driverRow = {};
let ar = 9;
for (const [id,label] of drivers) {
  const scenarioValues = scenarioNames.map(name => scenarioInputs.cases[name][id]);
  if (scenarioValues.some(x=>typeof x!=='number')) throw new Error(`Missing scenario driver ${id}`);
  driverRow[id]=ar;
  put(assumptions,`C${ar}`,label);
  for (let i=0;i<3;i++) put(assumptions,`C${ar+1+i}`,['Base','Upside','Downside'][i]);
  for (let y=2026;y<=2030;y++) {
    const c=col(y);
    for (let i=0;i<3;i++) put(assumptions,`${c}${ar+1+i}`,scenarioValues[i]);
    formula(assumptions,`${c}${ar}`,`=IF(Scenarios!$D$6="Base",${c}${ar+1},IF(Scenarios!$D$6="Upside",${c}${ar+2},${c}${ar+3}))`);
  }
  assumptions.getRange(`N${ar}:R${ar+3}`).setNumberFormat('0.0%;(0.0%);–');
  assumptions.getRange(`C${ar}:R${ar}`).format.fill = pale;
  assumptions.getRange(`N${ar+1}:R${ar+3}`).format.font = {name:'Arial',size:10,color:orange};
  ar+=5;
}
const a = (y,id) => `Assumptions!${col(y)}${driverRow[id]}`;
for (let y=2026;y<=2030;y++) {
  f(y,'gwp',`=${prior(y,'gwp')}*(1+${a(y,'gwp_growth')})`);
  f(y,'ceded_written',`=${v(y,'gwp')}*${a(y,'ceded_share')}`);
  f(y,'nwp',`=${v(y,'gwp')}-${v(y,'ceded_written')}`);
  f(y,'gross_upr',`=${v(y,'gwp')}*${a(y,'closing_upr_share')}`);
  f(y,'ceded_upr',`=${v(y,'ceded_written')}*${a(y,'closing_upr_share')}`);
  f(y,'net_upr',`=${v(y,'gross_upr')}-${v(y,'ceded_upr')}`);
  f(y,'gross_earned',`=${v(y,'gwp')}+${prior(y,'gross_upr')}-${v(y,'gross_upr')}`);
  f(y,'ceded_earned',`=${v(y,'ceded_written')}+${prior(y,'ceded_upr')}-${v(y,'ceded_upr')}`);
  f(y,'nep',`=${v(y,'gross_earned')}-${v(y,'ceded_earned')}`);
  f(y,'current_incurred',`=${v(y,'nep')}*(${a(y,'attritional_loss_ratio')}+${a(y,'catastrophe_loss_ratio')})`);
  f(y,'reserve_prior_incurred',`=${prior(y,'net_reserves')}*${a(y,'development_share_opening_reserves')}`);
  f(y,'reported_total_incurred',`=${v(y,'current_incurred')}+${v(y,'reserve_prior_incurred')}`);
  f(y,'paid_current',`=${v(y,'current_incurred')}*${a(y,'current_year_paid_share')}`);
  f(y,'paid_prior',`=${prior(y,'net_reserves')}*${a(y,'prior_year_paid_share')}`);
  f(y,'reported_total_paid',`=${v(y,'paid_current')}+${v(y,'paid_prior')}`);
  f(y,'net_reserves',`=${prior(y,'net_reserves')}+${v(y,'reported_total_incurred')}-${v(y,'reported_total_paid')}`);
  f(y,'unpaid_recoverables',`=${v(y,'net_reserves')}*${a(y,'unpaid_recoverable_share_gross')}/(1-${a(y,'unpaid_recoverable_share_gross')})`);
  f(y,'gross_reserves',`=${v(y,'net_reserves')}+${v(y,'unpaid_recoverables')}`);
  f(y,'reserve_rollforward_check',`=${prior(y,'net_reserves')}+${v(y,'reported_total_incurred')}-${v(y,'reported_total_paid')}-${v(y,'net_reserves')}`);
  f(y,'underwriting_expense_proxy',`=${v(y,'nep')}*${a(y,'expense_ratio')}`);
}
model.getRange(`H${row.investment_yield}:M${row.investment_yield}`).setNumberFormat('0.0%');
model.getRange(`C${row.investment_yield}:R${row.investment_yield}`).format.font.italic = true;
for (const id of ['gross_premium_earning_gap','ceded_premium_earning_gap','net_premium_earning_gap',
  'dac_stock_gap','investment_cash_proxy_gap','debt_stock_gap']) {
  model.getRange(`H${row[id]}:M${row[id]}`).format.font = {name:'Arial',size:10,color:orange};
}

const scenarios = sheet('Scenarios');
put(scenarios,'C2','Forecast scenario');
put(scenarios,'C6','Selected case'); put(scenarios,'D6','Base');
scenarios.getRange('D6').dataValidation = {rule:{type:'list',values:['Base','Upside','Downside']}};
put(scenarios,'C9','Base, upside and downside are illustrative analyst inputs. Changing D6 updates the same forecast schedules.');
put(scenarios,'C10','Forecast holds the FY2025 operating perimeter constant; the January 2026 Canadian sale is not reflected.');
scenarios.getRange('C:C').format.columnWidth = 87;
scenarios.getRange('D:D').format.columnWidth = 18;
scenarios.getRange('D6').format = {fill:'#FFF0D9',font:{name:'Arial',size:12,bold:true,color:orange}};

const summary = sheet('Summary');
put(summary,'C2','Travelers operating history and illustrative outlook');
summary.getRange('C2').format.font = {name:'Arial',size:14,bold:true,color:navy};
put(summary,'C3','Actuals: 2020–2025 · forecast: 2026–2030 · USD millions');
formula(summary,'C5','=Scenarios!D6');
summary.getRange('C:C').format.columnWidth = 40;
summary.getRange('D:F').format.columnWidth = 3;
summary.getRange('G:R').format.columnWidth = 14;
summary.getRange('G7:R7').values = [Array.from({length:12},(_,i)=>2019+i)];
summary.getRange('G7:R7').format = {fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'}};
const summaries = [
  ['Gross written premiums','gwp'],['Net written premiums','nwp'],
  ['Net earned premiums','nep'],['Net P&C claims reserves','net_reserves'],
  ['P&C reserve-table incurred','reported_total_incurred'],
  ['Illustrative underwriting expense','underwriting_expense_proxy'],
  ['Illustrative combined ratio',null],
  ['Total investments','total_investments'],['Net investment income','investment_income'],
  ['Common equity','closing_equity'],['Net income','net_income'],['Closing cash','cash'],
];
let sr=9;
for (const [label,id] of summaries) {
  put(summary,`C${sr}`,label);
  for (let y=2019;y<=2030;y++) {
    const available = y===2019 ? ['net_reserves','total_investments','closing_equity','cash'].includes(id) :
      y<=2025 ? id && id!=='underwriting_expense_proxy' :
      ['gwp','nwp','nep','net_reserves','reported_total_incurred','underwriting_expense_proxy'].includes(id);
    if (available) formula(summary,`${col(y)}${sr}`,`=Model!${v(y,id)}`);
    else if (!id && y>=2026) formula(summary,`${col(y)}${sr}`,
      `=(Model!${v(y,'reported_total_incurred')}+Model!${v(y,'underwriting_expense_proxy')})/Model!${v(y,'nep')}`);
  }
  sr++;
}
summary.getRange(`N15:R15`).setNumberFormat('0.0%');
summary.getRange('G9:R20').setNumberFormat('#,##0.0;(#,##0.0);–');
summary.getRange('N15:R15').setNumberFormat('0.0%');
put(summary,'C23','Illustrative forecast excludes the January 2026 Canadian sale; investment income, equity, cash and valuation remain unmodeled.');
put(summary,'C25','Master Check');
const openTerms = ['net_premium_earning_gap','dac_stock_gap','investment_cash_proxy_gap','debt_stock_gap']
  .flatMap(id => Array.from({length:6},(_,i)=>`ABS(Model!${v(2020+i,id)})`));
formula(summary,'M25',`=IF(SUM(${openTerms.join(',')})>0.01,"OPEN: historical stock bridges","PASS")`);
summary.getRange('C25:M25').format.font = {name:'Arial',size:10,bold:true,color:navy};
summary.getRange('M25').conditionalFormats.add('containsText',
  {text:'OPEN',format:{fill:'#FDE8E7',font:{bold:true,color:'#B42318'}}});

const cover = sheet('Cover');
put(cover,'C3','The Travelers Companies'); put(cover,'C4','P&C operating model');
put(cover,'C6','Fiscal 2020–2025 actuals · 2019 opening · 2026–2030 illustrative forecast');
put(cover,'C8','Information cutoff'); put(cover,'D8','2026-02-12');
put(cover,'C9','Status'); put(cover,'D9','Integrated historical statements; forecast and valuation pending');
put(cover,'C10','Run ID'); put(cover,'D10',runId);
put(cover,'C11','Historical detail uses annual-report PDFs and filing dates; selected SEC rows have independent parity checks.');
put(cover,'C12','2026 forecast is illustrative and excludes the January 2 Canadian disposal.');
cover.getRange('C:C').format.columnWidth = 73; cover.getRange('D:D').format.columnWidth = 54;
cover.getRange('C3').format.font = {name:'Arial',size:16,bold:true,color:navy};

const output = sheet('Output');
put(output,'C2','Research output status');
output.getRange('C2').format.font = {name:'Arial',size:14,bold:true,color:navy};
put(output,'C5','Price target'); put(output,'D5','Pending integrated forecast and market input review');
put(output,'C7','Historical controls'); put(output,'D7','Premium, reserve, audited income, balance sheet, cash, equity and financing checks');
put(output,'C8','Open work'); put(output,'D8','Canada disposal perimeter; UPR/DAC/investment/debt bridges; forecast statements');
put(output,'C9','Forecast scope'); put(output,'D9','Illustrative constant FY2025 perimeter; excludes January 2, 2026 Canadian sale');
put(output,'C10','Scenario result'); formula(output,'D10','=Scenarios!D6');
put(output,'C11','2030 net earned premiums'); formula(output,'D11',`=Model!${v(2030,'nep')}`);
put(output,'C12','2030 net P&C reserves'); formula(output,'D12',`=Model!${v(2030,'net_reserves')}`);
output.getRange('C:C').format.columnWidth = 30; output.getRange('D:D').format.columnWidth = 76;
output.getRange('D11:D12').setNumberFormat('#,##0.0');

book.recalculate();
const numberAt = (s,address) => s.getRange(address).values[0][0];
const actual2025 = numberAt(model,v(2025,'nep'));
if (numberAt(model,v(2025,'net_premium_earning_gap')) !== -412 ||
    numberAt(model,v(2025,'dac_stock_gap')) !== -83 ||
    numberAt(model,v(2025,'equity_rollforward_check')) !== 0 ||
    numberAt(model,v(2025,'reserve_rollforward_check')) !== 0) {
  throw new Error('Workbook actual bridges disagree with normalized controls');
}
if (numberAt(summary,'M25') !== 'OPEN: historical stock bridges')
  throw new Error('Master Check failed to report open historical bridges');
for (let y=2019;y<=2025;y++) {
  for (const id of ['balance_assets_check','balance_liabilities_check',
                    'balance_equity_check','balance_equation_check']) {
    if (numberAt(model,v(y,id)) !== 0) throw new Error(`Historical balance control failed ${y} ${id}`);
  }
  if (y>2019) for (const id of ['income_revenue_check','income_expense_check',
                               'income_net_check','income_cash_check']) {
    if (numberAt(model,v(y,id)) !== 0) throw new Error(`Historical income control failed ${y} ${id}`);
  }
}
for (const name of scenarioNames) {
  put(scenarios,'D6',name); book.recalculate();
  for (let i=0;i<5;i++) {
    const y=2026+i, expected=forecastReference.cases[name][i];
    const pairs = [
      ['gwp',expected.premiums.gwp],['nwp',expected.premiums.nwp],
      ['nep',expected.premiums.nep],['net_upr',expected.premiums.closing_net_upr],
      ['reported_total_incurred',expected.reserves.incurred_net],
      ['reported_total_paid',expected.reserves.paid_net],
      ['net_reserves',expected.reserves.closing_net],
      ['gross_reserves',expected.reserves.closing_gross],
      ['underwriting_expense_proxy',expected.underwriting_expenses],
    ];
    for (const [id,target] of pairs) {
      const actual = numberAt(model,v(y,id));
      if (typeof actual !== 'number' || Math.abs(actual-target)>1e-9*Math.max(1,Math.abs(target)))
        throw new Error(`Python/workbook forecast mismatch ${name} ${y} ${id}: ${actual} vs ${target}`);
    }
  }
  if (numberAt(model,v(2025,'nep')) !== actual2025)
    throw new Error('Scenario selector changed historical actuals');
}
put(scenarios,'D6','Base'); book.recalculate();
for (const [name,range] of [['Model',`C7:R24`],['Summary','C2:R25'],['Assumptions','C2:R23'],
                            ['Scenarios','C2:D10'],['Output','C2:D12'],['Cover','C3:D12'],['Sources','A1:J10']]) {
  const info = await book.inspect({kind:'table',range:`${name}!${range}`,include:'values,formulas',
                                   tableMaxRows:20,tableMaxCols:15,maxChars:1900});
  console.log(`${name}: ${info.ndjson.slice(0,1900)}`);
}
const integratedView = await book.inspect({kind:'table',
  range:`Model!C${row.fee_income-1}:M${row.balance_equation_check}`,include:'values,formulas',
  tableMaxRows:42,tableMaxCols:11,maxChars:2000});
console.log(`Integrated actuals: ${integratedView.ndjson.slice(0,2000)}`);
const errors = await book.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',
  options:{useRegex:true,maxResults:50},summary:'final formula error scan',maxChars:3000});
console.log(`Errors: ${errors.ndjson}`);
await fs.mkdir(path.dirname(outputPath),{recursive:true});
for (const name of ['Cover','Summary','Assumptions','Scenarios','Model','Output','Sources']) {
  const preview = await book.render({sheetName:name,range:name==='Model'?'C2:R24':name==='Sources'?'A1:G12':
    name==='Assumptions'?'C2:R23':name==='Summary'?'C2:R25':name==='Cover'?'C3:D12':name==='Output'?'C2:D12':'C2:D10',scale:1,format:'png'});
  await fs.writeFile(path.join(path.dirname(outputPath),`${name.toLowerCase()}_preview.png`),
                     new Uint8Array(await preview.arrayBuffer()));
}
for (const [name,range] of [
  ['income_integration',`C${row.fee_income-1}:M${row.income_cash_check}`],
  ['balance_integration',`C${row.accrued_investment_income-1}:M${row.balance_equation_check}`],
]) {
  const preview = await book.render({sheetName:'Model',range,scale:1,format:'png'});
  await fs.writeFile(path.join(path.dirname(outputPath),`${name}_preview.png`),
                     new Uint8Array(await preview.arrayBuffer()));
}
const xlsx = await SpreadsheetFile.exportXlsx(book);
await xlsx.save(outputPath);
const mapPath = path.join(root,'docs/model_spec/rendered_row_map.json');
await fs.writeFile(mapPath,JSON.stringify({schema_version:1,status:'partial_operating_workbook',
  sheet:'Model',opening_column:'G',period_columns:Object.fromEntries(Array.from({length:11},(_,i)=>[2020+i,col(2020+i)])),
  layout},null,2)+'\n');
console.log(`Saved ${outputPath}`);
