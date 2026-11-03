"""One prepared study per test run, independent copies for mutable fixtures."""
from copy import deepcopy
from functools import lru_cache
from study_app import Study

@lru_cache(maxsize=1)
def reference_study(): return Study()

def study_copy(): return deepcopy(reference_study())

@lru_cache(maxsize=1)
def _adoption_reference():
    from core_adoption_reference import load_reference
    from validate_stacks import ROOT
    return load_reference(ROOT)

def active_reference():
    """Independent copy of the reviewed, frozen adoption reference."""
    return deepcopy(_adoption_reference())


def adopted_effort(unit):
    """Project the adopted unit independently of the current pricing references."""
    return {**unit, 'roles': [
        {key: value for key, value in role.items() if key != 'rate_ref'}
        for role in unit['roles']
    ]}
