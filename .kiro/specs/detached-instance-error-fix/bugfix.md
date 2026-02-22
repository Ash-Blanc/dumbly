# Bugfix Requirements Document

## Introduction

The backend analysis service crashes with a `DetachedInstanceError` when attempting to access the `analysis.status` attribute in the `start_analysis` method. This occurs because the `Analysis` object is retrieved from the database within a session context manager, but is then accessed outside of that session after it has been closed. When SQLAlchemy objects are detached from their session, lazy-loaded attributes cannot be accessed, causing the application to crash during background task execution.

This bug affects the core analysis workflow, preventing analyses from starting properly and causing a poor user experience.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN `start_analysis` is called with an `Analysis` object that was retrieved from a database session THEN the system crashes with `DetachedInstanceError` when accessing `analysis.status` at line 49

1.2 WHEN the `Analysis` object is passed to background tasks (`_run_discovery` or `_run_workflow`) THEN the system cannot access any lazy-loaded attributes on the detached object

1.3 WHEN `analysis_repo.update_status(analysis.id, analysis.status)` is called at lines 37 and 44 THEN the system crashes because `analysis.status` triggers a database query on a detached instance

### Expected Behavior (Correct)

2.1 WHEN `start_analysis` is called with an `Analysis` object THEN the system SHALL successfully access the analysis ID without triggering a `DetachedInstanceError`

2.2 WHEN updating the analysis status THEN the system SHALL use only the analysis ID (which is already loaded) and the new status value, without accessing the current `analysis.status` attribute

2.3 WHEN passing the `Analysis` object to background tasks THEN the system SHALL only use the analysis ID for subsequent database operations, avoiding detached instance errors

### Unchanged Behavior (Regression Prevention)

3.1 WHEN `update_status` is called with an analysis ID and status value THEN the system SHALL CONTINUE TO update the database record correctly

3.2 WHEN background tasks execute workflow steps THEN the system SHALL CONTINUE TO process analyses and emit events correctly

3.3 WHEN the repository methods are called within their own session contexts THEN the system SHALL CONTINUE TO perform database operations successfully

3.4 WHEN multiple analyses run concurrently THEN the system SHALL CONTINUE TO handle them independently without interference
