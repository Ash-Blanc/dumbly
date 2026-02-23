"""
Bug Condition Exploration Test for DetachedInstanceError

**Validates: Requirements 2.1, 2.2, 2.3**

This test is designed to FAIL on unfixed code to confirm the bug exists.
The test demonstrates that accessing analysis.status on a detached Analysis object
causes DetachedInstanceError.

CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists.
DO NOT attempt to fix the test or the code when it fails.

Expected outcome: Test FAILS with DetachedInstanceError on unfixed code.
After fix is implemented: Test PASSES, confirming the bug is resolved.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from sqlmodel import Session
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


def create_detached_analysis(input_type: str, input_value: str) -> Analysis:
    """
    Create an Analysis object and return it in a detached state.
    This simulates the production scenario where an Analysis is retrieved
    in one session but accessed after that session closes.
    """
    # Create analysis in a session
    with get_sync_session() as session:
        analysis = Analysis(
            input_type=input_type,
            input_value=input_value,
            status=AnalysisStatus.PENDING.value,
            llm_provider="pollinations"
        )
        session.add(analysis)
        session.flush()
        session.refresh(analysis)
        analysis_id = analysis.id
    
    # Session is now closed, retrieve the analysis again to get a detached object
    with get_sync_session() as session:
        analysis = session.get(Analysis, analysis_id)
        # Access id to ensure it's loaded
        _ = analysis.id
        # Expunge the object from the session to keep loaded attributes in memory
        session.expunge(analysis)
    
    # At this point, analysis is detached from its session
    # id is loaded in memory, but accessing status will trigger DetachedInstanceError
    return analysis


def create_detached_analysis_with_papers(topic: str, papers: list) -> Analysis:
    """
    Create an Analysis with discovered papers and return it in a detached state.
    """
    # Create analysis and papers in a session
    with get_sync_session() as session:
        analysis = Analysis(
            input_type=InputType.TOPIC.value,
            input_value=topic,
            status=AnalysisStatus.DISCOVERY.value,
            llm_provider="pollinations"
        )
        session.add(analysis)
        session.flush()
        session.refresh(analysis)
        analysis_id = analysis.id
        
        # Add discovered papers
        for paper in papers:
            db_paper = DiscoveredPaper(
                analysis_id=analysis_id,
                arxiv_id=paper["arxiv_id"],
                title=paper["title"],
                authors=paper.get("authors", []),
                summary=paper.get("summary", ""),
                relevance_score=paper.get("relevance_score", 0.8),
                novelty_score=paper.get("novelty_score", 0.7),
            )
            session.add(db_paper)
    
    # Retrieve in a new session and let it become detached
    with get_sync_session() as session:
        analysis = session.get(Analysis, analysis_id)
        # Access id to ensure it's loaded
        _ = analysis.id
        # Expunge the object from the session to keep loaded attributes in memory
        session.expunge(analysis)
    
    return analysis


class TestDetachedInstanceBug:
    """
    Property 1: Fault Condition - Status Update Without Detached Access
    
    These tests demonstrate the bug condition: accessing analysis.status on a
    detached Analysis object causes DetachedInstanceError.
    
    **EXPECTED OUTCOME ON UNFIXED CODE**: All tests FAIL with DetachedInstanceError
    **EXPECTED OUTCOME AFTER FIX**: All tests PASS
    """
    
    @pytest.mark.asyncio
    async def test_discovery_mode_detached_access(self, setup_database):
        """
        Test discovery mode: Create Analysis, retrieve in session, close session,
        call start_analysis with discovery input.
        
        **Validates: Requirements 2.1, 2.2, 2.3**
        
        Bug occurs at line 37: analysis_repo.update_status(analysis.id, analysis.status)
        """
        # Create a detached Analysis object
        analysis = create_detached_analysis(
            input_type=InputType.TOPIC.value,
            input_value="machine learning optimization"
        )
        
        # Create request for discovery mode
        request = AnalysisRequest(
            input="machine learning optimization",
            input_type=InputType.TOPIC,
            max_papers=3,
            auto_select=False,
            include_market_research=False,
            include_technical_assessment=False,
            include_business_model=False
        )
        
        # This should trigger the bug on unfixed code
        # Expected: DetachedInstanceError when accessing analysis.status at line 37
        # After fix: Should succeed without accessing analysis.status
        await analysis_service.start_analysis(analysis, request)
        
        # If we reach here after the fix, verify the status was updated correctly
        # Need to retrieve in a session context to avoid detached instance error
        with get_sync_session() as session:
            updated_analysis = session.get(Analysis, analysis.id)
            assert updated_analysis is not None
            assert updated_analysis.status == AnalysisStatus.DISCOVERY.value
    
    @pytest.mark.asyncio
    async def test_direct_analysis_detached_access(self, setup_database):
        """
        Test direct analysis mode: Create Analysis, retrieve in session, close session,
        call start_analysis with direct arXiv ID.
        
        **Validates: Requirements 2.1, 2.2, 2.3**
        
        Bug occurs at line 44: analysis_repo.update_status(analysis.id, analysis.status)
        """
        # Create a detached Analysis object
        analysis = create_detached_analysis(
            input_type=InputType.ARXIV_ID.value,
            input_value="2301.12345"
        )
        
        # Create request for direct analysis mode
        request = AnalysisRequest(
            input="2301.12345",
            input_type=InputType.ARXIV_ID,
            include_market_research=False,
            include_technical_assessment=False,
            include_business_model=False
        )
        
        # This should trigger the bug on unfixed code
        # Expected: DetachedInstanceError when accessing analysis.status at line 44
        # After fix: Should succeed without accessing analysis.status
        await analysis_service.start_analysis(analysis, request)
        
        # If we reach here after the fix, verify the status was updated correctly
        # Need to retrieve in a session context to avoid detached instance error
        with get_sync_session() as session:
            updated_analysis = session.get(Analysis, analysis.id)
            assert updated_analysis is not None
            assert updated_analysis.status == AnalysisStatus.PROCESSING.value
            assert updated_analysis.resolved_arxiv_id == "2301.12345"
    
    @pytest.mark.asyncio
    async def test_select_paper_detached_access(self, setup_database):
        """
        Test select_paper: Create Analysis with discovered papers, retrieve in session,
        close session, call select_paper.
        
        **Validates: Requirements 2.1, 2.2, 2.3**
        
        Bug occurs at line 99: analysis_repo.update_status(analysis_id, analysis.status)
        """
        # Create a detached Analysis with discovered papers
        papers = [
            {
                "arxiv_id": "2301.11111",
                "title": "Paper 1",
                "authors": ["Author A"],
                "summary": "Summary 1",
                "relevance_score": 0.9,
                "novelty_score": 0.8
            },
            {
                "arxiv_id": "2301.22222",
                "title": "Paper 2",
                "authors": ["Author B"],
                "summary": "Summary 2",
                "relevance_score": 0.85,
                "novelty_score": 0.75
            }
        ]
        
        analysis = create_detached_analysis_with_papers(
            topic="deep learning",
            papers=papers
        )
        
        # Create request
        request = AnalysisRequest(
            input="deep learning",
            input_type=InputType.TOPIC,
            include_market_research=False,
            include_technical_assessment=False,
            include_business_model=False
        )
        
        # This should trigger the bug on unfixed code
        # Expected: DetachedInstanceError when accessing analysis.status at line 99
        # After fix: Should succeed without accessing analysis.status
        await analysis_service.select_paper(analysis.id, "2301.11111", request)
        
        # If we reach here after the fix, verify the status was updated correctly
        # Need to retrieve in a session context to avoid detached instance error
        with get_sync_session() as session:
            updated_analysis = session.get(Analysis, analysis.id)
            assert updated_analysis is not None
            assert updated_analysis.status == AnalysisStatus.PROCESSING.value
            assert updated_analysis.resolved_arxiv_id == "2301.11111"


class TestDetachedInstanceBugPropertyBased:
    """
    Property-based tests for the bug condition using Hypothesis.
    
    These tests generate multiple scenarios to ensure the bug is consistently
    reproduced across different inputs.
    """
    
    @given(
        topic=st.text(min_size=5, max_size=100, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
            blacklist_characters='\x00'
        ))
    )
    @settings(
        max_examples=3,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @pytest.mark.asyncio
    async def test_property_discovery_mode_various_topics(self, setup_database, topic):
        """
        Property: For any topic input, start_analysis with a detached Analysis object
        should successfully update status without accessing analysis.status.
        
        **Validates: Requirements 2.1, 2.2, 2.3**
        
        On unfixed code: FAILS with DetachedInstanceError
        After fix: PASSES for all generated topics
        """
        # Create a detached Analysis object
        analysis = create_detached_analysis(
            input_type=InputType.TOPIC.value,
            input_value=topic
        )
        
        request = AnalysisRequest(
            input=topic,
            input_type=InputType.TOPIC,
            max_papers=3,
            auto_select=False,
            include_market_research=False,
            include_technical_assessment=False,
            include_business_model=False
        )
        
        # Should trigger bug on unfixed code, succeed after fix
        await analysis_service.start_analysis(analysis, request)
        
        # Verify status update
        with get_sync_session() as session:
            updated_analysis = session.get(Analysis, analysis.id)
            assert updated_analysis is not None
            assert updated_analysis.status == AnalysisStatus.DISCOVERY.value
    
    @given(
        arxiv_id=st.text(min_size=10, max_size=15).filter(
            lambda x: '.' in x and x.replace('.', '').replace('-', '').replace('/', '').isalnum()
        )
    )
    @settings(
        max_examples=3,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @pytest.mark.asyncio
    async def test_property_direct_analysis_various_arxiv_ids(self, setup_database, arxiv_id):
        """
        Property: For any arXiv ID input, start_analysis with a detached Analysis object
        should successfully update status without accessing analysis.status.
        
        **Validates: Requirements 2.1, 2.2, 2.3**
        
        On unfixed code: FAILS with DetachedInstanceError
        After fix: PASSES for all generated arXiv IDs
        """
        # Create a detached Analysis object
        analysis = create_detached_analysis(
            input_type=InputType.ARXIV_ID.value,
            input_value=arxiv_id
        )
        
        request = AnalysisRequest(
            input=arxiv_id,
            input_type=InputType.ARXIV_ID,
            include_market_research=False,
            include_technical_assessment=False,
            include_business_model=False
        )
        
        # Should trigger bug on unfixed code, succeed after fix
        await analysis_service.start_analysis(analysis, request)
        
        # Verify status update
        with get_sync_session() as session:
            updated_analysis = session.get(Analysis, analysis.id)
            assert updated_analysis is not None
            assert updated_analysis.status == AnalysisStatus.PROCESSING.value
