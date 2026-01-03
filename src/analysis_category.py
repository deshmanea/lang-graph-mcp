
from pydantic import BaseModel
from enum import Enum

class FailureCategory(str, Enum):
    DATA_ISSUE = "DATA_ISSUE"            # missing / invalid DB data
    REQUEST_ISSUE = "REQUEST_ISSUE"      # bad params, URL, headers
    AUTH_ISSUE = "AUTH_ISSUE"            # 401 / 403
    ASSERTION_MISMATCH = "ASSERTION_MISMATCH"
    TIMEOUT = "TIMEOUT"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    ENV_ISSUE = "ENV_ISSUE"
    TEST_BUG = "TEST_BUG"
    UNKNOWN = "UNKNOWN"


class FailureAnalysis(BaseModel):
    '''An analysis of a failure along with a possible fix.'''
    test_name: str
    failure: str
    category: FailureCategory
    analysis: str
    possible_fix: str