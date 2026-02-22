# backend/app/services/export_service.py

from app.models.domain import Analysis, Export
from app.services.repository import export_repo
from app.config import settings
from datetime import datetime, timedelta
from typing import Optional
import os
import json
from pathlib import Path


class ExportService:
    """Generate and manage exports in multiple formats"""

    SUPPORTED_FORMATS = ["pdf", "markdown", "json"]

    def __init__(self):
        self.export_dir = Path(settings.export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export_analysis(self, analysis: Analysis, format: str) -> Export:
        """Export analysis to specified format"""

        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format}")

        export = Export(
            analysis_id=analysis.id,
            format=format,
            expires_at=datetime.utcnow() + timedelta(days=settings.share_link_expiry_days)
        )

        if format == "json":
            file_path = self._export_json(analysis, export.id)
        elif format == "markdown":
            file_path = self._export_markdown(analysis, export.id)
        elif format == "pdf":
            file_path = self._export_pdf(analysis, export.id)

        export.file_path = str(file_path)
        return export

    def _export_json(self, analysis: Analysis, export_id: str) -> Path:
        """Export as JSON file"""
        file_path = self.export_dir / f"{export_id}.json"

        data = {
            "meta": {
                "exported_at": datetime.utcnow().isoformat(),
                "analysis_id": analysis.id,
                "arxiv_id": analysis.resolved_arxiv_id,
            },
            "paper_analysis": analysis.paper_analysis,
            "ideas": analysis.ideas,
            "business_models": analysis.business_models
        }

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

        return file_path

    def _export_markdown(self, analysis: Analysis, export_id: str) -> Path:
        """Export as formatted Markdown"""
        file_path = self.export_dir / f"{export_id}.md"

        paper = analysis.paper_analysis or {}
        ideas = analysis.ideas or []

        md = f"""# arXiv SaaS Analysis Report

> Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

## Paper Analysis

**Title:** {paper.get('paper_title', 'N/A')}
**arXiv ID:** [{analysis.resolved_arxiv_id}](https://arxiv.org/abs/{analysis.resolved_arxiv_id})
**Novelty Score:** {paper.get('novelty_score', 0) * 100:.0f}%

### Summary
{paper.get('summary', 'No summary available.')}

### Key Innovations
"""
        for innovation in paper.get('key_innovations', []):
            md += f"- {innovation}\n"

        md += "\n---\n\n## Generated SaaS Opportunities\n\n"

        for i, idea in enumerate(ideas, 1):
            md += f"""### {i}. {idea.get('title', 'Untitled')}

*{idea.get('tagline', '')}*

{idea.get('description', '')}

**Target Market:** {idea.get('target_market', 'N/A')}
**Market Fit Score:** {idea.get('market_fit_score', 0) * 10:.0f}%

#### Key Features
"""
            for feature in idea.get('key_features', []):
                md += f"- {feature}\n"
            md += "\n"

        with open(file_path, "w") as f:
            f.write(md)

        return file_path

    def _export_pdf(self, analysis: Analysis, export_id: str) -> Path:
        """Export as PDF"""
        # For now, we'll use markdown and convert via a simple HTML
        # In production, use WeasyPrint or similar
        file_path = self.export_dir / f"{export_id}.pdf"

        # Create HTML for PDF
        html = self._generate_html(analysis)
        html_path = self.export_dir / f"{export_id}.html"

        with open(html_path, "w") as f:
            f.write(html)

        # Placeholder - in production, convert HTML to PDF
        # For now, return HTML path
        return html_path

    def _generate_html(self, analysis: Analysis) -> str:
        """Generate HTML for PDF export"""
        paper = analysis.paper_analysis or {}
        ideas = analysis.ideas or []

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SaaS Analysis - {paper.get('paper_title', 'Report')}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 40px; }}
        h1 {{ color: #6366f1; border-bottom: 3px solid #6366f1; padding-bottom: 10px; }}
        h2 {{ color: #4f46e5; margin-top: 40px; }}
        h3 {{ color: #7c3aed; }}
    </style>
</head>
<body>
    <h1>arXiv SaaS Analysis Report</h1>
    <p>arXiv: {analysis.resolved_arxiv_id}</p>
    <h2>Paper Analysis</h2>
    <h3>{paper.get('paper_title', 'Untitled')}</h3>
    <p>{paper.get('summary', '')}</p>
    <h2>SaaS Opportunities</h2>
    {self._render_ideas_html(ideas)}
</body>
</html>"""

    def _render_ideas_html(self, ideas: list) -> str:
        html = ""
        for idea in ideas:
            html += f"""
    <div style="border: 1px solid #e5e7eb; padding: 20px; margin: 20px 0; border-radius: 12px;">
        <h3>{idea.get('title', 'Untitled')}</h3>
        <p>{idea.get('description', '')}</p>
    </div>"""
        return html

    def get_share_link(self, export: Export) -> str:
        """Generate shareable link for export"""
        return f"{settings.base_url}/share/{export.share_token}"


# Singleton instance
export_service = ExportService()
