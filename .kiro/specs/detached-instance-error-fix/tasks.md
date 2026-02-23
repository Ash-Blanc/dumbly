# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Fault Condition** - Status Update Without Detached Access
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the DetachedInstanceError exists
  - **Scoped PBT Approach**: Scope the property to concrete failing cases - detached Analysis objects with discovery input and direct arXiv ID input
  - Test that start_analysis successfully updates status using only analysis ID and explicit status values (AnalysisStatus.DISCOVERY.value or AnalysisStatus.PROCESSING.value) without accessing analysis.status on detached objects
  - Test discovery mode: Create Analysis, retrieve in session, close session, call start_analysis with discovery input
  - Test direct analysis mode: Create Analysis, retrieve in session, close session, call start_analysis with direct arXiv ID
  - Test select_paper: Create Analysis with discovered papers, retrieve in session, close session, call select_paper
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS with DetachedInstanceError (this is correct - it proves the bug exists)
  - Document counterexamples found (e.g., "DetachedInstanceError: Instance <Analysis at 0x...> is not bound to a Session")
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Database Operations and Background Tasks
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs (normal database operations, background tasks, workflow execution)
  - Write property-based tests capturing observed behavior patterns:
    - Repository methods (update_status, update_progress, update_results) work correctly with explicit parameters
    - Background tasks (_run_discovery, _run_workflow) execute correctly and emit proper events
    - Workflow steps (paper analysis, idea generation, market research) execute correctly
    - Multiple concurrent analyses run independently without interference
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 3. Fix for detached instance error in analysis service

  - [x] 3.1 Implement the fix in start_analysis method
    - Remove redundant status assignment on line 36: Delete `analysis.status = AnalysisStatus.DISCOVERY.value`
    - Pass explicit status value on line 37: Change `analysis_repo.update_status(analysis.id, analysis.status)` to `analysis_repo.update_status(analysis.id, AnalysisStatus.DISCOVERY.value)`
    - Remove redundant status assignment on line 43: Delete `analysis.status = AnalysisStatus.PROCESSING.value`
    - Pass explicit status value on line 44: Change `analysis_repo.update_status(analysis.id, analysis.status)` to `analysis_repo.update_status(analysis.id, AnalysisStatus.PROCESSING.value)`
    - _Bug_Condition: isBugCondition(input) where input.analysis.is_detached_from_session() AND input.attribute_name == "status" AND code_attempts_to_access(input.analysis.status)_
    - _Expected_Behavior: For any detached Analysis object, start_analysis SHALL successfully update status using only analysis.id and explicit status values without accessing analysis.status_
    - _Preservation: All database operations, background tasks, workflow execution, and concurrent analysis handling that do NOT involve accessing lazy-loaded attributes on detached objects SHALL remain unchanged_
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4_

  - [x] 3.2 Implement the fix in select_paper method
    - Remove redundant status assignment on line 97: Delete `analysis.status = AnalysisStatus.PROCESSING.value`
    - Pass explicit status value on line 98: Change `analysis_repo.update_status(analysis_id, analysis.status)` to `analysis_repo.update_status(analysis_id, AnalysisStatus.PROCESSING.value)`
    - _Bug_Condition: Same as 3.1_
    - _Expected_Behavior: Same as 3.1_
    - _Preservation: Same as 3.1_
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4_

  - [x] 3.3 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Status Update Without Detached Access
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 3.4 Verify preservation tests still pass
    - **Property 2: Preservation** - Database Operations and Background Tasks
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix (no regressions)
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
