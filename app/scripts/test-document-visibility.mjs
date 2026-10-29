import assert from 'node:assert/strict';
import {test} from 'node:test';
import {isModelDataReference} from '../src/documentVisibility.ts';

test('model YAML is hidden through reader links, fragments and download endpoints',()=>{
 for(const source of [
  'source/calibration-couts.yaml','source/recalibration-metier.yaml#lots/demo',
  'sources/client/cartographie.yml','source/MODELE.YAML?version=1#detail',
  'source/calibration-couts%2Eyaml',
  '/api/file?path=source%2Fcalibration-couts.yaml',
  '/api/document?path=source%2Frecalibration-metier.yaml%23lots%2Fdemo',
 ])assert.equal(isModelDataReference(source),true,source);
});

test('original evidence, reader notes and personal scenario exports stay available',()=>{
 for(const source of [
  'sources/client/microsoft-1.pdf#page=38','sources/client/sap-questionnaire.xlsx',
  'source/offres-synvance.md','source/offres-synvance.md#pieces',
  'sources/client/rfi-questions-reponses.pptx','flow-study-scenario.json',
  '/api/file?path=sources%2Fclient%2Fmicrosoft-1.pdf',
  '/api/file?path=source%2Foffres-synvance.md',
 ])assert.equal(isModelDataReference(source),false,source);
});

test('external documentation formats are not treated as internal model data',()=>{
 for(const source of [
  'https://example.org/specification.yaml','https://example.org/documentation?file=example.yml',
  '//example.org/specification.yaml','source/offres-synvance.md?example=model.yaml',
 ])assert.equal(isModelDataReference(source),false,source);
});
