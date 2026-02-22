# backend/app/services/analysis_service.py

import asyncio
import json
import re
from typing import Dict, Optional
from datetime import datetime

from app.models.domain import Analysis, AnalysisStatus
from app.models.requests import AnalysisRequest
from app.agents.base import LLMProvider
from app.services.repository import analysis_repo, discovered_paper_repo
from app.services.stream_manager import stream_manager
from app.services.paper_service import paper_service
from app.agents import (
    create_paper_analyzer,
    create_saas_ideator,
    create_market_researcher,
    create_technical_architect,
    create_business_modeler,
    create_paper_discovery,
)


class AnalysisService:
    """Service for running and managing analyses"""

    def __init__(self):
        self._running_tasks: Dict[str, asyncio.Task] = {}

    async def start_analysis(self, analysis: Analysis, request: AnalysisRequest):
        """Start analysis workflow"""

        # Resolve input
        resolved = paper_service.resolve_input(request.input, request.input_type)

        if resolved.get("type") == "discovery":
            # Start paper discovery
            analysis.status = AnalysisStatus.DISCOVERY.value
            analysis_repo.update_status(analysis.id, analysis.status)

            task = asyncio.create_task(
                self._run_discovery(analysis, resolved["topic"], request)
            )
        else:
            # Direct analysis
            analysis.resolved_arxiv_id = resolved["arxiv_id"]
            analysis.status = AnalysisStatus.PROCESSING.value
            analysis_repo.update_status(analysis.id, analysis.status)

            task = asyncio.create_task(
                self._run_workflow(analysis, resolved["arxiv_id"], request)
            )

        self._running_tasks[analysis.id] = task

    async def _run_discovery(self, analysis: Analysis, topic: str, request: AnalysisRequest):
        """Run paper discovery for a topic"""
        try:
            await stream_manager.emit(analysis.id, "discovery_start", {
                "topic": topic,
                "max_papers": request.max_papers
            })

            # Run discovery agent
            provider = LLMProvider(request.llm_provider)
            agent = create_paper_discovery(provider=provider, api_key=request.llm_api_key)

            result = agent.run(f"Find {request.max_papers} papers about: {topic}")
            papers = self._parse_json_response(result.content)

            # Save discovered papers
            if papers:
                discovered_paper_repo.save_papers(analysis.id, papers)

            await stream_manager.emit(analysis.id, "discovery_complete", {
                "papers": papers
            })

            # Auto-select if enabled
            if request.auto_select and papers:
                await asyncio.sleep(3)  # Give user time to see options
                top_paper = max(papers, key=lambda p: p.get("relevance_score", 0) + p.get("novelty_score", 0))
                await self.select_paper(analysis.id, top_paper["arxiv_id"], request)

        except Exception as e:
            await stream_manager.emit(analysis.id, "error", {"error": str(e)})
            analysis_repo.update_status(analysis.id, AnalysisStatus.ERROR.value)

    async def select_paper(self, analysis_id: str, arxiv_id: str, request: AnalysisRequest):
        """Select a paper from discovery and start analysis"""
        discovered_paper_repo.select_paper(analysis_id, arxiv_id)

        analysis = analysis_repo.get(analysis_id)
        analysis.resolved_arxiv_id = arxiv_id
        analysis.status = AnalysisStatus.PROCESSING.value
        analysis_repo.update_status(analysis_id, analysis.status)

        await stream_manager.emit(analysis_id, "status", {
            "status": "processing",
            "arxiv_id": arxiv_id
        })

        task = asyncio.create_task(
            self._run_workflow(analysis, arxiv_id, request)
        )
        self._running_tasks[analysis_id] = task

    async def _run_workflow(self, analysis: Analysis, arxiv_id: str, request: AnalysisRequest):
        """Run the full analysis workflow"""
        try:
            provider = LLMProvider(request.llm_provider)

            # Step 1: Paper Analysis
            paper_analysis = await self._run_step(
                analysis.id, "paper_analysis",
                "PaperAnalyzer",
                create_paper_analyzer(provider=provider, api_key=request.llm_api_key),
                f"Analyze arXiv paper: {arxiv_id}"
            )

            if paper_analysis:
                analysis.paper_analysis = paper_analysis

            # Step 2: Idea Generation
            ideas = await self._run_step(
                analysis.id, "idea_generation",
                "SaaSIdeator",
                create_saas_ideator(provider=provider, api_key=request.llm_api_key),
                f"Generate SaaS ideas from this paper analysis: {json.dumps(analysis.paper_analysis or {})}"
            )

            if ideas:
                analysis.ideas = ideas
            ideas = analysis.ideas or []

            # Step 3: Market Research for top ideas
            if request.include_market_research:
                for idea in ideas[:3]:
                    market_result = await self._run_step(
                        analysis.id, f"market_{idea.get('id', 'unknown')}",
                        "MarketResearcher",
                        create_market_researcher(provider=provider, api_key=request.llm_api_key),
                        f"Research market for: {idea.get('title', '')} - {idea.get('description', '')}",
                        store_result=False
                    )
                    if market_result:
                        idea["market_insights"] = market_result

            # Step 4: Technical Assessment for top ideas
            if request.include_technical_assessment:
                for idea in ideas[:3]:
                    tech_result = await self._run_step(
                        analysis.id, f"tech_{idea.get('id', 'unknown')}",
                        "TechnicalArchitect",
                        create_technical_architect(provider=provider, api_key=request.llm_api_key),
                        f"Assess technical requirements for: {idea.get('title', '')} - {idea.get('description', '')}",
                        store_result=False
                    )
                    if tech_result:
                        idea["technical_assessment"] = tech_result

            # Step 5: Business Models
            business_models = []
            if request.include_business_model and len(ideas) >= 2:
                for idea in ideas[:2]:
                    model = await self._run_step(
                        analysis.id, f"business_{idea.get('id', 'unknown')}",
                        "BusinessModeler",
                        create_business_modeler(provider=provider, api_key=request.llm_api_key),
                        f"Create business model for: {idea.get('title', '')} - {idea.get('description', '')}",
                        store_result=False
                    )
                    if model:
                        business_models.append({"idea_id": idea.get("id"), "business_model": model})

            # Save final results
            analysis_repo.update_results(
                analysis.id,
                analysis.paper_analysis,
                ideas,
                business_models
            )

            await stream_manager.emit(analysis.id, "complete", {
                "paper_analysis": analysis.paper_analysis,
                "ideas": ideas,
                "business_models": business_models
            })

        except Exception as e:
            await stream_manager.emit(analysis.id, "error", {"error": str(e)})
            analysis_repo.update_status(analysis.id, AnalysisStatus.ERROR.value)

    async def _run_step(
        self,
        analysis_id: str,
        step_id: str,
        agent_name: str,
        agent,
        prompt: str,
        store_result: bool = True
    ) -> Optional[dict]:
        """Run a single workflow step"""

        await stream_manager.emit(analysis_id, "step_start", {
            "step": step_id,
            "agent": agent_name
        })

        analysis_repo.update_progress(analysis_id, step_id, {"status": "running"})

        try:
            result = agent.run(prompt)
            parsed = self._parse_json_response(result.content)

            analysis_repo.update_progress(analysis_id, step_id, {"status": "complete"})

            await stream_manager.emit(analysis_id, "step_complete", {
                "step": step_id,
                "agent": agent_name
            })

            return parsed

        except Exception as e:
            analysis_repo.update_progress(analysis_id, step_id, {"status": "error", "error": str(e)})
            raise

    def _parse_json_response(self, content: str) -> Optional[dict]:
        """Parse JSON from agent response"""
        try:
            # Try direct parse
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON in response
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass

            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass

        return None

    def cancel_analysis(self, analysis_id: str):
        """Cancel a running analysis"""
        if analysis_id in self._running_tasks:
            self._running_tasks[analysis_id].cancel()
            del self._running_tasks[analysis_id]


# Singleton instance
analysis_service = AnalysisService()
