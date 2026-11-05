import test from 'node:test';
import assert from 'node:assert/strict';
import {economicDestination,economicHash,economicPeriod,phaseReadingHash,contextualEconomicLink} from '../src/economicNavigation.ts';
import {preStudyDestination} from '../src/preStudyNavigation.ts';

test('every old simulation entry opens the fixed reference and drops overrides',()=>{
 for(const page of ['simuler','simulations','simulation-hypotheses','simulation-depenses','se-projeter']){
  assert.deepEqual(economicDestination(page,new URLSearchParams('view=5&option=sap&budget=123&inflation_tjm=99')),{page:'comparer',option:'sap',view:'5'});
 }
});
test('economic deep links retain the lot, selected option and reading horizon together',()=>{
 const route=economicDestination('evaluation-core',new URLSearchParams('family=master-data-java-spring&option=java-spring&view=3'));
 assert.equal(economicHash(route),'#evaluation-core?option=java-spring&view=3&family=master-data-java-spring');
 assert.deepEqual(economicDestination('parametres',new URLSearchParams('detail=tarifs&option=microsoft&view=7')),{page:'parametres',option:'microsoft',view:'7',detail:'tarifs'});
});
test('old funding and project references stay economic while observations stay in pre-studies',()=>{
 for(const focus of ['G01','G01-detail','CB-JAVA-SERVICES','budgets'])assert.equal(economicDestination('etude-marche',new URLSearchParams({focus})).focus,focus);
 assert.equal(economicDestination('etude-marche',new URLSearchParams('view=references')).view,'transpositions');
 assert.deepEqual(economicDestination('etude-marche',new URLSearchParams('view=construction')),{page:'acquisition',option:'java-spring'});
 assert.equal(preStudyDestination('etude-marche',new URLSearchParams('view=offers')).page,'synvance');
 assert.equal(preStudyDestination('etude-marche',new URLSearchParams('focus=ba-stock~sap')).page,'preetude-solutions');
});
test('retired personal choices never silently become a Java simulation',()=>{
 for(const option of ['rust','dotnet'])assert.equal(preStudyDestination('simuler',new URLSearchParams({option})).page,'preetudes');
 assert.equal(economicDestination('comparer',new URLSearchParams('option=invalid&view=999')).option,undefined);
 assert.equal(economicDestination('comparer',new URLSearchParams('option=invalid&view=999')).view,undefined);
 assert.equal(economicHash({page:'vision'}),null);
});

test('the economic evidence register shows current options and preserves the historical record',async()=>{
 const {visibleBudgetReview}=await import('../src/applicationScope.ts');
 const ui={essential:{active_options:['java-spring','microsoft','sap']}};
 const stacks=['java-spring','dotnet','rust','microsoft','sap'];
 const budget={option_labels:Object.fromEntries(stacks.map(s=>[s,s])),summary:{unpriced_reserves:5,net_extra_initial_eur_ht:null},additions:stacks.map(stack=>({id:stack,stack,net_extra_initial_eur_ht:null,net_extra_annual_eur_ht:null})),reviews:[{addition_refs:stacks,non_budget_treatments:stacks.map(stack=>({stack,reason:'retained'}))}]};
 const before=structuredClone(budget),scoped=visibleBudgetReview(ui,budget);
 assert.deepEqual(scoped.additions.map(row=>row.stack),ui.essential.active_options);
 assert.deepEqual(scoped.reviews[0].addition_refs,ui.essential.active_options);
 assert.deepEqual(scoped.reviews[0].non_budget_treatments.map(row=>row.stack),ui.essential.active_options);
 assert.equal(scoped.summary.unpriced_reserves,3);
 assert.equal(scoped.summary.net_extra_initial_eur_ht,null);
 assert.deepEqual(budget,before);
});

test('expert details preserve an independent horizon and the original reading focus',()=>{
 for(const horizon of ['3','5','7','10'])for(const view of ['financements','transpositions']){
  const route=economicDestination('evaluation-core',new URLSearchParams({option:'microsoft',horizon,view,family:'master-data-java-spring',focus:'G01'}));
  assert.equal(economicPeriod(route),Number(horizon));
  const detailHash=economicHash(route);
  const loaded=economicDestination('evaluation-core',new URLSearchParams(detailHash.split('?')[1]));
  assert.deepEqual(loaded,route);
  const back={...loaded,view:undefined};
  assert.equal(economicPeriod(back),Number(horizon));
  assert.equal(back.option,'microsoft');assert.equal(back.focus,'G01');
  const assumptions=economicDestination('parametres',new URLSearchParams(economicHash({...back,page:'parametres'}).split('?')[1]));
  assert.equal(assumptions.family,route.family);assert.equal(economicPeriod(assumptions),Number(horizon));
 }
 assert.equal(economicPeriod({view:'3'}),3);
 assert.equal(economicPeriod({view:'financements'}),10);
 assert.equal(economicPeriod({horizon:'7',view:'3'}),7);
 assert.equal(economicPeriod({horizon:'bad'}),10);
});


test('phase shortcuts and phase changes preserve the chosen option and independent horizon',()=>{
 for(const option of ['java-spring','microsoft','sap'])for(const horizon of ['3','5','7','10']){
  for(const page of ['acquisition','integration','fonctionnement','scenarios','charges-acquisition','charges-integration','charges-fonctionnement','organisation-delivery','equipes-produit','integration-transverse']){
   const route={page,option,horizon},before=structuredClone(route);
   const hash=phaseReadingHash(route),params=new URLSearchParams(hash.split('?')[1]);
   assert.equal(params.get('option'),option);assert.equal(params.get('horizon'),horizon);
   assert.equal(hash.split('?')[0],'#'+page);assert.deepEqual(route,before);
  }
  for(const focus of ['method','summary']){
   const params=new URLSearchParams(phaseReadingHash({page:'acquisition',option,horizon,focus}).split('?')[1]);
   assert.equal(params.get('focus'),focus);assert.equal(params.get('option'),option);assert.equal(params.get('horizon'),horizon);
  }
 }
 assert.equal(phaseReadingHash({page:'glossaire'}),null);
 assert.equal(phaseReadingHash({page:'integration',option:'sap',horizon:'999'}),'#integration?option=sap');
 assert.equal(phaseReadingHash({page:'charges-acquisition',option:'java-spring',horizon:'5',focus:'master-data-java-spring',returnTo:'evaluation-core',family:'master-data-java-spring'}),'#charges-acquisition?option=java-spring&focus=master-data-java-spring&horizon=5&returnTo=evaluation-core&family=master-data-java-spring');
});

test('an option-specific evidence link never falls back to Java costs',()=>{
 for(const option of ['java-spring','microsoft','sap'])for(const horizon of ['3','5','7','10']){
  for(const href of ['#evaluation-core','#parametres','#comparer','#se-projeter','#etude-marche?view=references']){
   const hash=contextualEconomicLink(href,option,horizon),[page,query]=hash.slice(1).split('?');
   const loaded=economicDestination(page,new URLSearchParams(query));
   assert.equal(loaded.option,option);assert.equal(economicPeriod(loaded),Number(horizon));
  }
 }
 assert.equal(contextualEconomicLink('#evaluation-core?view=financements&horizon=7&focus=G01','sap'),'#evaluation-core?option=sap&horizon=7&view=financements&focus=G01');
 for(const href of ['#complexite','#synvance-microsoft','source/offres-synvance.md','https://example.org/proof'])assert.equal(contextualEconomicLink(href,'microsoft','3'),href);
});


test('all reading windows round-trip through pages and evidence without changing the option',async()=>{
 const {economicReadingContext,readingOrigin,shownOptions}=await import('../src/economicNavigation.ts');
 for(const horizon of ['1','6','15'])for(const origin of ['project','core','production']){
  const context={horizon,origin,options:'microsoft,sap'};
  for(const page of ['comparer','evaluation-core','parametres']){
   const route=economicDestination(page,new URLSearchParams({option:'sap',...context}));
   assert.equal(economicPeriod(route),Number(horizon));assert.equal(readingOrigin(route),origin);
   assert.deepEqual(shownOptions(route),['microsoft','sap']);
   assert.deepEqual(economicReadingContext(route),context);
   const loaded=economicDestination(page,new URLSearchParams(economicHash(route).split('?')[1]));
   assert.deepEqual(loaded,route);
   const proof=new URLSearchParams(phaseReadingHash({page:'charges-integration',option:'sap',...economicReadingContext(route)}).split('?')[1]);
   assert.equal(proof.get('origin'),origin);assert.equal(proof.get('options'),'microsoft,sap');assert.equal(proof.get('horizon'),horizon);
  }
 }
 for(const horizon of ['0','16','1.5','-1','NaN'])assert.equal(economicPeriod({horizon}),10);
 assert.equal(readingOrigin({origin:'unknown'}),'project');
 assert.deepEqual(shownOptions({options:'sap,sap,unknown,microsoft'}),['microsoft','sap']);
 assert.deepEqual(shownOptions({options:''}),['java-spring','microsoft','sap']);
});


test('method links preserve all reading criteria',()=>{
 const context={origin:'production',options:'microsoft,sap'};
 const url=contextualEconomicLink('#evaluation-core?view=financements','sap','15',context);
 const query=new URLSearchParams(url.split('?')[1]);
 assert.equal(query.get('horizon'),'15');assert.equal(query.get('origin'),'production');
 assert.equal(query.get('options'),'microsoft,sap');assert.equal(query.get('option'),'sap');
});

test('delivery routes preserve team phase and financial context without mutation',()=>{
 for(const page of ['organisation-cible','gouvernance-delivery','charges-equipes','couts-equipes','integration-transverse']){
  const route={page,option:'java-spring',horizon:'7',focus:'b2c',view:'integration',zone:'province'};
  const before={...route};
  const hash=phaseReadingHash(route);
  assert.equal(hash.split('?')[0],'#'+page);
  const params=new URLSearchParams(hash.split('?')[1]);
  for(const key of ['option','horizon','focus','view','zone'])assert.equal(params.get(key),route[key]);
  assert.deepEqual(route,before);
 }
});

test('framework map links preserve view object phase and financial reading context',()=>{
 const route={page:'schema-modele',option:'java-spring',horizon:'7',origin:'core',view:'teams',focus:'b2c',phase:'integration',zone:'province'};
 const before={...route},hash=phaseReadingHash(route),params=new URLSearchParams(hash.split('?')[1]);
 assert.equal(hash.split('?')[0],'#schema-modele');
 for(const key of ['option','horizon','origin','view','focus','phase','zone'])assert.equal(params.get(key),route[key]);
 assert.deepEqual(route,before);
});
