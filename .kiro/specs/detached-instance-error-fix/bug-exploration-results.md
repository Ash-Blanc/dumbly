# Bug Exploration Test Results

## Test Execution Summary

**Date**: 2026-02-22  
**Status**: ✅ Bug Successfully Reproduced  
**Test File**: `backend/tests/test_detached_instance_bug.py`

## Counterexamples Found

### Primary Counterexample

**Error Type**: `sqlalchemy.orm.exc.DetachedInstanceError`

**Error Message**:
```
Instance <Analysis at 0x713cec42d450> is not bound to a Session; 
attribute refresh operation cannot proceed
```

**Location**: `app/services/analysis_service.py:40`

**Trigger**: Accessing `analysis.status` on a detached Analysis object in the `start_analysis` method

### Test Case: Discovery Mode Detached Access

**Test**: `test_discovery_mode_detached_access`

**Scenario**:
1. Create an Analysis object with input_type="topic" and input_value="machine learning optimization"
2. Retrieve the Analysis in a database session
3. Close the session (Analysis becomes detached)
4. Call `start_analysis(analysis, request)` with discovery input
5. Code attempts to access `analysis.status` at line 37: `analysis_repo.update_status(analysis.id, analysis.status)`

**Result**: ❌ FAILED with DetachedInstanceError (Expected - confirms bug exists)

**Stack Trace Key Points**:
```
app/services/analysis_service.py:40: in start_analysis
    analysis_repo.update_status(analysis.id, analysis.status)
                                ^^^^^^^^^^^
.venv/lib/python3.12/site-packages/sqlalchemy/orm/attributes.py:569: in __get__
    return self.impl.get(state, dict_)
.venv/lib/python3.12/site-packages/sqlalchemy/orm/attributes.py:1096: in get
    value = self._fire_loader_callables(state, key, passive)
.venv/lib/python3.12/site-packages/sqlalchemy/orm/state.py:828: in _load_expired
    self.manager.expired_attribute_loader(self, toload, passive)
.venv/lib/python3.12/site-packages/sqlalchemy/orm/loading.py:1607: DetachedInstanceError
```

### Expected Additional Failures

Based on the code analysis, the following test cases are also expected to fail with the same error:

1. **test_direct_analysis_detached_access**
   - Location: Line 44 in `start_analysis`
   - Code: `analysis_repo.update_status(analysis.id, analysis.status)`
   - Scenario: Direct arXiv ID input with detached Analysis object

2. **test_select_paper_detached_access**
   - Location: Line 99 in `select_paper`
   - Code: `analysis_repo.update_status(analysis_id, analysis.status)`
   - Scenario: Paper selection after discovery with detached Analysis object

## Root Cause Confirmation

The bug exploration test confirms the hypothesized root cause:

1. ✅ **Session Lifecycle Mismatch**: Analysis objects are retrieved in one session but accessed after that session closes
2. ✅ **Lazy Loading Failure**: SQLAlchemy cannot lazy-load `analysis.status` attribute without an active session
3. ✅ **Redundant Attribute Access**: The code reads `analysis.status` just to pass it to `update_status`, which is unnecessary

## Fix Validation Criteria

When the fix is implemented, these same tests should:
- ✅ PASS without DetachedInstanceError
- ✅ Successfully update the analysis status in the database
- ✅ Use only `analysis.id` (eagerly loaded) and explicit status values
- ✅ Avoid accessing `analysis.status` on detached objects

## Property-Based Test Coverage

The test suite includes property-based tests using Hypothesis to generate:
- Various topic strings (5-100 characters)
- Various arXiv ID formats
- Multiple test scenarios to ensure comprehensive coverage

These tests will provide strong guarantees that the fix works across all input variations.
