# backend/app/services/repository.py

from sqlmodel import select
from app.models.domain import Analysis, DiscoveredPaper, Export
from app.database import get_sync_session
from typing import Optional, List
from datetime import datetime


class AnalysisRepository:
    """Repository for analysis CRUD operations"""

    def create(self, analysis: Analysis) -> Analysis:
        with get_sync_session() as session:
            session.add(analysis)
            session.flush()  # Flush to get the ID without committing
            session.refresh(analysis)
            return analysis

    def get(self, analysis_id: str) -> Optional[Analysis]:
        with get_sync_session() as session:
            result = session.execute(
                select(Analysis).where(Analysis.id == analysis_id)
            )
            return result.scalar_one_or_none()

    def update_status(self, analysis_id: str, status: str) -> None:
        with get_sync_session() as session:
            analysis = session.execute(
                select(Analysis).where(Analysis.id == analysis_id)
            ).scalar_one_or_none()
            if analysis:
                analysis.status = status
                analysis.updated_at = datetime.utcnow()
                session.add(analysis)

    def update_progress(self, analysis_id: str, step: str, data: dict) -> None:
        with get_sync_session() as session:
            analysis = session.execute(
                select(Analysis).where(Analysis.id == analysis_id)
            ).scalar_one_or_none()
            if analysis:
                analysis.progress[step] = data
                analysis.updated_at = datetime.utcnow()
                session.add(analysis)

    def update_results(
        self,
        analysis_id: str,
        paper_analysis: dict,
        ideas: List[dict],
        business_models: List[dict]
    ) -> Optional[Analysis]:
        with get_sync_session() as session:
            analysis = session.execute(
                select(Analysis).where(Analysis.id == analysis_id)
            ).scalar_one_or_none()
            if analysis:
                analysis.paper_analysis = paper_analysis
                analysis.ideas = ideas
                analysis.business_models = business_models
                analysis.status = "completed"
                analysis.completed_at = datetime.utcnow()
                analysis.updated_at = datetime.utcnow()
                session.add(analysis)
            return analysis

    def get_recent(self, limit: int = 10) -> List[Analysis]:
        with get_sync_session() as session:
            result = session.execute(
                select(Analysis)
                .order_by(Analysis.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())

    def delete(self, analysis_id: str) -> bool:
        with get_sync_session() as session:
            analysis = session.execute(
                select(Analysis).where(Analysis.id == analysis_id)
            ).scalar_one_or_none()
            if analysis:
                session.delete(analysis)
                return True
            return False


class DiscoveredPaperRepository:
    """Repository for discovered papers"""

    def save_papers(self, analysis_id: str, papers: List[dict]) -> List[DiscoveredPaper]:
        with get_sync_session() as session:
            db_papers = []
            for p in papers:
                db_paper = DiscoveredPaper(
                    analysis_id=analysis_id,
                    arxiv_id=p["arxiv_id"],
                    title=p["title"],
                    authors=p.get("authors", []),
                    summary=p.get("summary", ""),
                    relevance_score=p.get("relevance_score", 0),
                    novelty_score=p.get("novelty_score", 0),
                    categories=p.get("categories", []),
                    published_date=p.get("published_date"),
                )
                session.add(db_paper)
                db_papers.append(db_paper)
            return db_papers

    def get_by_analysis(self, analysis_id: str) -> List[DiscoveredPaper]:
        with get_sync_session() as session:
            result = session.execute(
                select(DiscoveredPaper)
                .where(DiscoveredPaper.analysis_id == analysis_id)
                .order_by(DiscoveredPaper.relevance_score.desc())
            )
            return list(result.scalars().all())

    def select_paper(self, analysis_id: str, arxiv_id: str) -> Optional[DiscoveredPaper]:
        with get_sync_session() as session:
            papers = session.execute(
                select(DiscoveredPaper)
                .where(DiscoveredPaper.analysis_id == analysis_id)
            ).scalars().all()

            for paper in papers:
                paper.selected = (paper.arxiv_id == arxiv_id)
                session.add(paper)

            selected = session.execute(
                select(DiscoveredPaper)
                .where(
                    DiscoveredPaper.analysis_id == analysis_id,
                    DiscoveredPaper.arxiv_id == arxiv_id
                )
            ).scalar_one_or_none()
            return selected


class ExportRepository:
    """Repository for exports"""

    def create(self, export: Export) -> Export:
        with get_sync_session() as session:
            session.add(export)
            session.flush()
            session.refresh(export)
            return export

    def get(self, export_id: str) -> Optional[Export]:
        with get_sync_session() as session:
            result = session.execute(
                select(Export).where(Export.id == export_id)
            )
            return result.scalar_one_or_none()

    def get_by_share_token(self, share_token: str) -> Optional[Export]:
        with get_sync_session() as session:
            result = session.execute(
                select(Export).where(Export.share_token == share_token)
            )
            return result.scalar_one_or_none()

    def increment_download_count(self, export_id: str) -> None:
        with get_sync_session() as session:
            export = session.execute(
                select(Export).where(Export.id == export_id)
            ).scalar_one_or_none()
            if export:
                export.download_count += 1
                session.add(export)


# Singleton instances
analysis_repo = AnalysisRepository()
discovered_paper_repo = DiscoveredPaperRepository()
export_repo = ExportRepository()
