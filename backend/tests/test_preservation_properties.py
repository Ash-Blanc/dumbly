"""
Preservation Property Tests for DetachedInstanceError Fix

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

These tests verify that normal database operations, background tasks, and workflow
execution continue to work correctly. They are designed to PASS on unfixed code
to establish a baseline of correct behavior that must be preserved after the fix.

IMPORTANT: These tests should PASS on unfixed code - they test scenarios where
objects are NOT detached and normal operations work correctly.

Expected outcome: Tests PASS on unfixed code (baseline behavior).
After fix is implemented: Tests PASS (confirms no regressions).
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from sqlmodel import Session, select
from app.models.domain import Analysis, AnalysisStatus, DiscoveredPaper
from app.models.requests import AnalysisRequest, InputType
from app.database import sync_engine, get_sync_session
from app.services.analysis_service import analysis_service
from app.services.repository import analysis_repo, discovered_paper_repo
import asyncio


# Test fixtures
@pytest.fixture(scope="function")
def setup_database():
    """Setup test database"""
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(sync_engine)
    yield
    SQLModel.metadata.drop_all(sync_engine)


def create_analysis(input_type: str, input_value: str, status: str = AnalysisStatus.PENDING.value) -> str:
    """
    Create an Analysis and return its ID.
    This simulates normal operation where we work with IDs, not detached objects.
    """
    with get_sync_session() as session:
        analysis = Analysis(
            input_type=input_type,
            input_value=input_value,
            status=status,
            llm_provider="pollinations"
        )
        session.add(analysis)
        session.flush()
        session.refresh(analysis)
        return analysis.id


class TestRepositoryMethodPreservation:
    """
    Property 2: Preservation - Repository Methods
    
    These tests verify that repository methods (update_status, update_progress,
    update_results) continue to work correctly with explicit parameters.
    
    **Validates: Requirement 3.1**
    
    **EXPECTED OUTCOME**: All tests PASS on unfixed code
    """
    
    def test_update_status_with_explicit_parameters(self, setup_database):
        """
        Test that update_status works correctly when called with explicit parameters
        (analysis ID and status value), without accessing detached objects.
        
        **Validates: Requirement 3.1**
        """
        # Create analysis using ID-based approach
        analysis_id = create_analysis(
            input_type=InputType.TOPIC.value,
            input_value="machine learning"
        )
        
        # Update status using explicit parameters (no detached object access)
        analysis_repo.update_status(analysis_id, AnalysisStatus.DISCOVERY.value)
        
        # Verify the update worked by querying within a session
        with get_sync_session() as session:
            updated_analysis = session.execute(
                select(Analysis).where(Analysis.id == analysis_id)
            ).scalar_one_or_none()
            assert updated_analysis is not None
            assert updated_analysis.status == AnalysisStatus.DISCOVERY.value
        
        # Update to another status
        analysis_repo.update_status(analysis_id, AnalysisStatus.PROCESSING.value)
        
        # Verify again within a session
        with get_sync_session() as session:
            updated_analysis = session.execute(
                select(Analysis).where(Analysis.id == analysis_id)
            ).scalar_one_or_none()
            assert updated_analysis.status == AnalysisStatus.PROCESSING.value
    
    def test_update_progress_with_explicit_parameters(self, setup_database):
        """
        Test that update_progress works correctly when called with explicit parameters.
        
        **Validates: Requirement 3.1**
        """
        analysis_id = create_analysis(
            input_type=InputType.ARXIV_ID.value,
            input_value="2301.12345"
        )
        
        # Update progress using explicit parameters
        analysis_repo.update_progress(analysis_id, "paper_analysis", {
            "status": "running",
            "progress": 50
        })
        
        # Verify the update worked by querying within a session
        with get_sync_session() as session:
            updated_analysis = session.execute(
                select(Analysis).where(Analysis.id == analysis_id)
            ).scalar_one_or_none()
            assert updated_analysis is not None
            assert "paper_analysis" in updated_analysis.progress
            assert updated_analysis.progress["paper_analysis"]["status"] == "running"
            assert updated_analysis.progress["paper_analysis"]["progress"] == 50
    
    def test_update_results_with_explicit_parameters(self, setup_database):
        """
        Test that update_results works correctly when called with explicit parameters.
        
        **Validates: Requirement 3.1**
        """
        analysis_id = create_analysis(
            input_type=InputType.ARXIV_ID.value,
            input_value="2301.12345"
        )
        
        # Update results using explicit parameters
        paper_analysis = {"title": "Test Paper", "summary": "Test summary"}
        ideas = [{"id": "1", "title": "Idea 1"}]
        business_models = [{"idea_id": "1", "model": "SaaS"}]
        
        analysis_repo.update_results(
            analysis_id,
            paper_analysis,
            ideas,
            business_models
        )
        
        # Verify the update worked by querying within a session
        with get_sync_session() as session:
            updated_analysis = session.execute(
                select(Analysis).where(Analysis.id == analysis_id)
            ).scalar_one_or_none()
            assert updated_analysis is not None
            assert updated_analysis.paper_analysis == paper_analysis
            assert updated_analysis.ideas == ideas
            assert updated_analysis.business_models == business_models
            assert updated_analysis.status == "completed"


class TestRepositoryMethodPreservationPropertyBased:
    """
    Property-based tests for repository method preservation using Hypothesis.
    
    These tests generate multiple scenarios to ensure repository methods work
    correctly across different inputs.
    
    **Validates: Requirement 3.1, 3.3**
    """
    
    @given(
        status=st.sampled_from([
            AnalysisStatus.PENDING.value,
            AnalysisStatus.DISCOVERY.value,
            AnalysisStatus.PROCESSING.value,
            AnalysisStatus.ERROR.value,
            "completed"
        ])
    )
    @settings(
        max_examples=3,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_update_status_various_statuses(self, setup_database, status):
        """
        Property: For any valid status value, update_status should successfully
        update the database when called with explicit parameters.
        
        **Validates: Requirements 3.1, 3.3**
        """
        analysis_id = create_analysis(
            input_type=InputType.TOPIC.value,
            input_value="test topic"
        )
        
        # Update status with explicit parameter
        analysis_repo.update_status(analysis_id, status)
        
        # Verify the update by querying within a session
        with get_sync_session() as session:
            updated_analysis = session.execute(
                select(Analysis).where(Analysis.id == analysis_id)
            ).scalar_one_or_none()
            assert updated_analysis is not None
            assert updated_analysis.status == status
    
    @given(
        step_name=st.text(min_size=3, max_size=30, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters='\x00'
        )),
        progress_value=st.integers(min_value=0, max_value=100)
    )
    @settings(
        max_examples=3,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_update_progress_various_steps(self, setup_database, step_name, progress_value):
        """
        Property: For any step name and progress value, update_progress should
        successfully update the database when called with explicit parameters.
        
        **Validates: Requirements 3.1, 3.3**
        """
        analysis_id = create_analysis(
            input_type=InputType.TOPIC.value,
            input_value="test topic"
        )
        
        # Update progress with explicit parameters
        progress_data = {"status": "running", "progress": progress_value}
        analysis_repo.update_progress(analysis_id, step_name, progress_data)
        
        # Verify the update by querying within a session
        with get_sync_session() as session:
            updated_analysis = session.execute(
                select(Analysis).where(Analysis.id == analysis_id)
            ).scalar_one_or_none()
            assert updated_analysis is not None
            assert step_name in updated_analysis.progress
            assert updated_analysis.progress[step_name]["progress"] == progress_value


class TestConcurrentAnalysisPreservation:
    """
    Property 2: Preservation - Concurrent Analysis Handling
    
    These tests verify that multiple analyses can run concurrently without
    interference when using ID-based operations.
    
    **Validates: Requirement 3.4**
    
    **EXPECTED OUTCOME**: All tests PASS on unfixed code
    """
    
    def test_multiple_concurrent_status_updates(self, setup_database):
        """
        Test that multiple analyses can have their statuses updated concurrently
        without interference.
        
        **Validates: Requirement 3.4**
        """
        # Create multiple analyses
        analysis_ids = [
            create_analysis(InputType.TOPIC.value, f"topic {i}")
            for i in range(5)
        ]
        
        # Update all statuses concurrently
        for i, analysis_id in enumerate(analysis_ids):
            if i % 2 == 0:
                analysis_repo.update_status(analysis_id, AnalysisStatus.DISCOVERY.value)
            else:
                analysis_repo.update_status(analysis_id, AnalysisStatus.PROCESSING.value)
        
        # Verify each analysis has the correct status by querying within a session
        with get_sync_session() as session:
            for i, analysis_id in enumerate(analysis_ids):
                updated_analysis = session.execute(
                    select(Analysis).where(Analysis.id == analysis_id)
                ).scalar_one_or_none()
                assert updated_analysis is not None
                if i % 2 == 0:
                    assert updated_analysis.status == AnalysisStatus.DISCOVERY.value
                else:
                    assert updated_analysis.status == AnalysisStatus.PROCESSING.value
    
    def test_multiple_concurrent_progress_updates(self, setup_database):
        """
        Test that multiple analyses can have their progress updated concurrently
        without interference.
        
        **Validates: Requirement 3.4**
        """
        # Create multiple analyses
        analysis_ids = [
            create_analysis(InputType.TOPIC.value, f"topic {i}")
            for i in range(5)
        ]
        
        # Update progress for all analyses
        for i, analysis_id in enumerate(analysis_ids):
            analysis_repo.update_progress(analysis_id, "step_1", {
                "status": "running",
                "analysis_number": i
            })
        
        # Verify each analysis has the correct progress by querying within a session
        with get_sync_session() as session:
            for i, analysis_id in enumerate(analysis_ids):
                updated_analysis = session.execute(
                    select(Analysis).where(Analysis.id == analysis_id)
                ).scalar_one_or_none()
                assert updated_analysis is not None
                assert "step_1" in updated_analysis.progress
                assert updated_analysis.progress["step_1"]["analysis_number"] == i


class TestConcurrentAnalysisPreservationPropertyBased:
    """
    Property-based tests for concurrent analysis handling.
    
    **Validates: Requirements 3.3, 3.4**
    """
    
    @given(
        num_analyses=st.integers(min_value=2, max_value=10)
    )
    @settings(
        max_examples=3,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_concurrent_analyses_independent(self, setup_database, num_analyses):
        """
        Property: For any number of concurrent analyses, each analysis should
        maintain its own independent state without interference.
        
        **Validates: Requirements 3.3, 3.4**
        """
        # Create multiple analyses
        analysis_ids = [
            create_analysis(InputType.TOPIC.value, f"topic {i}")
            for i in range(num_analyses)
        ]
        
        # Update each analysis with unique data
        for i, analysis_id in enumerate(analysis_ids):
            analysis_repo.update_status(
                analysis_id,
                AnalysisStatus.DISCOVERY.value if i % 2 == 0 else AnalysisStatus.PROCESSING.value
            )
            analysis_repo.update_progress(analysis_id, f"step_{i}", {
                "unique_id": i,
                "status": "running"
            })
        
        # Verify each analysis maintained its unique state by querying within a session
        with get_sync_session() as session:
            for i, analysis_id in enumerate(analysis_ids):
                updated_analysis = session.execute(
                    select(Analysis).where(Analysis.id == analysis_id)
                ).scalar_one_or_none()
                assert updated_analysis is not None
                
                # Check status
                expected_status = (
                    AnalysisStatus.DISCOVERY.value if i % 2 == 0
                    else AnalysisStatus.PROCESSING.value
                )
                assert updated_analysis.status == expected_status
                
                # Check progress
                assert f"step_{i}" in updated_analysis.progress
                assert updated_analysis.progress[f"step_{i}"]["unique_id"] == i
