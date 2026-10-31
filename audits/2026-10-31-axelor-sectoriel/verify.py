"""Reproduce the Axelor evidence checks and canonical cost sensitivities.
These checks verify source identity, scope and arithmetic. They do not execute Axelor
or certify the functional hypotheses. Run from the repository root.
"""
from pathlib import Path
import sys, json, gzip, base64, hashlib, time, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from estimation_calculation import formula,calculate
from model_context import model_session
from validate_stacks import read


def main():
    started=time.perf_counter();checks=[]
    report=json.loads((ROOT/'sources/qualification-axelor-secteur-2026-10-31.json').read_text(encoding='utf-8'))
    archive=(ROOT/report['source_archive']).read_bytes()
    assert hashlib.sha256(archive).hexdigest()==report['source_archive_sha256']
    source=json.loads(gzip.decompress(archive));assert source['commit']==report['source_commit']
    files={}
    for name,item in source['files'].items():
        raw=base64.b64decode(item['base64'],validate=True)
        assert hashlib.sha256(raw).hexdigest()==item['sha256']==report['source_files'][name]['sha256']
        assert hashlib.sha256(raw.replace(b'\r\n',b'\n')).hexdigest()==report['source_files'][name]['git_blob_sha256']
        files[name]=raw.decode('utf-8');checks.append('source:'+name)
    for path,digest in report['calculation_dependencies'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest;checks.append('snapshot:'+path)
    for evidence in report['requirements']:
        assert hashlib.sha256((ROOT/evidence['path']).read_bytes()).hexdigest()==evidence['sha256']
        checks.append('requirement:'+evidence['path'])
    def code(suffix):return next(text for name,text in files.items() if name.endswith(suffix))
    ns={'d':'http://axelor.com/xml/ns/domain-models'}
    fields=lambda suffix:{e.attrib['name'] for e in ET.fromstring(code(suffix)).findall('.//d:entity/*',ns) if 'name' in e.attrib}
    assert {'applicationBeginDate','applicationEndDate'}<=fields('/PriceList.xml')
    assert not {'season','channel'} & fields('/StockRules.xml')
    assert '.order("reservationDateTime")' in code('/ReservedQtyServiceImpl.java')
    assert '.order("stockMove.estimatedDate")' in code('/ReservedQtyServiceImpl.java')
    assert 'leftQtyToAllocateStockMove.min(neededQtyToAllocate)' in code('/ReservedQtyServiceImpl.java')
    assert 'priceLists.size() == 1' in code('/PartnerPriceListServiceImpl.java')
    assert 'self.outsourcing = false' in code('/MachineServiceImpl.java')
    assert {'estimatedDate','realDate','statusSelect'}<=fields('/StockMove.xml')
    assert 'purchaseOrderLine' in fields('/StockMoveLine.xml')
    future=code('/StockLocationLineServiceImpl.java')
    assert 'computeFutureQty' in future and 'STATUS_PLANNED' in future
    assert 'futureQty.add(incConverted)' in future and 'futureQty.subtract(outConverted)' in future
    assert '.order("maturityDate")' in code('/MrpServiceImpl.java')
    checks.append('planned-moves-and-future-projection-are-relevant-primitives')
    checks.append('bounded-source-observations-not-product-tests')
    registry=read(ROOT/'source/calculs-estimation-core.yaml');mechanisms={m['id'] for m in registry['mechanisms']}
    for item in report['complements']:
        assert set(item['reuse_funding'])<=mechanisms
        assert item['incremental_jh'] is None;checks.append('funding-boundary:'+item['id'])
    impact=report['estimation_consequences'];units=read(ROOT/'source/estimations-core-retenues.yaml')['units']
    assert sum(u['total_jh'] for u in units)==impact['active_total_jh']
    assert impact['delta_jh'] is None and impact['revised_total_jh'] is None and impact['adoption'] is False
    baseline=json.loads((ROOT/impact['baseline_evidence']).read_text(encoding='utf-8'));c=baseline['cocomo']
    with model_session():
        E=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum'])
        def effort(size):return formula('cocomo_effort',A=c['A'],KSLOC=size/1000,E=E,EM=c['other_EM'],SCED=c['SCED'],month_hours=c['month_hours'],day_hours=c['day_hours'],effort_phase_factor=c['effort_phase_factor'])
        for scenario in impact['sensitivity']:
            unit=next(u for u in baseline['units'] if u['id']==scenario['unit_id'])
            actual=calculate({'id':unit['calculation']})
            assert abs(actual['alignment']['reference_jh']-scenario['base_jh'])<1e-8
            assert abs(effort(scenario['base_units'])-scenario['base_jh'])<1e-8
            delta=effort(scenario['base_units']+scenario['extra_units'])-scenario['base_jh']
            assert abs(delta-scenario['delta_jh'])<1e-8;checks.append('canonical-sensitivity:'+scenario['unit_id'])
    result=dict(status='passed',seconds=round(time.perf_counter()-started,3),checks=checks,
                scope='Evidence consistency and canonical arithmetic, not an Axelor runtime or independent methodological review.')
    (Path(__file__).parent/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],checks=len(checks),seconds=result['seconds'])))

if __name__=='__main__':main()
