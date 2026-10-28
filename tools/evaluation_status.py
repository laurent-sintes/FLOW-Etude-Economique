"""Canonical application status, shared by methods and their current results."""
from copy import deepcopy
from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read

SOURCE = 'source/statut-evaluation.yaml'
TEXT = {'type': 'string', 'minLength': 1}
SCHEMA = {'type': 'object', 'additionalProperties': False, 'required': ['version', 'core'],
          'properties': {'version': {'const': 1}, 'core': {
              'type': 'object', 'additionalProperties': False,
              'required': ['method_status', 'qualification_status', 'calibration_status',
                           'title', 'producer', 'summary', 'text', 'active_source'],
              'properties': {'method_status': {'const': 'defined'},
                             'qualification_status': {'const': 'partial'},
                             'calibration_status': {'const': 'legacy_unrecalibrated'},
                             'title': TEXT, 'producer': TEXT, 'summary': TEXT, 'text': TEXT,
                             'active_source': {'const': 'source/recalibration-metier.yaml'}}}}}


def load_status(ref='core'):
    document = read(ROOT / SOURCE)
    errors = list(Draft202012Validator(SCHEMA).iter_errors(document))
    if errors or ref != 'core':
        raise ValueError('ERR_EVALUATION_STATUS:' + (errors[0].message if errors else str(ref)))
    return deepcopy(document[ref])


def status_notice(ref):
    status = load_status(ref)
    return {key: status[key] for key in ('title', 'text')}
