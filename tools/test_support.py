"""One prepared study per test run, independent copies for mutable fixtures."""
from copy import deepcopy
from functools import lru_cache
from study_app import Study

@lru_cache(maxsize=1)
def reference_study(): return Study()

def study_copy(): return deepcopy(reference_study())
