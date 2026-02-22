# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

arXiv SaaS Generator - An AI-powered application that transforms academic research papers (arXiv) into viable SaaS business opportunities using multi-agent orchestration.

## Architecture

Monorepo with two services:

```
dumbly/
├── backend/              # FastAPI Python service (port 8000)
│   └── app/
│       ├── main.py       # FastAPI app entry point
│       ├── config.py     # Pydantic Settings for env vars
│       ├── database.py   # PostgreSQL connection (async + sync)
│       ├── agents/       # 6 specialized Agno agents
│       ├── workflows/    # Agno workflow orchestration
│       ├── models/       # SQLModel domain + Pydantic req/res
│       ├── services/     # Business logic layer
│       └── routers/      # API endpoints
└── frontend/             # React + Vite app (port 3000)
    └── src/
        ├── App.jsx       # Main React component
        ├── hooks/        # Custom hooks (useAnalysisStream)
        └── utils/        # Utilities (inputDetection)
```

### Backend: Multi-Agent System (Agno)

6 specialized agents orchestrated by AnalysisService:

1. **PaperAnalyzer** - Extracts innovations, novelty scores from arXiv papers
2. **SaaSIdeator** - Generates SaaS business ideas with market analysis
3. **MarketResearcher** - Researches market size, competition (DuckDuckGo)
4. **TechnicalArchitect** - Assesses tech stack, development effort
5. **BusinessModeler** - Creates revenue models, pricing strategies
6. **PaperDiscovery** - Finds relevant papers for topic searches

### Input Types Supported

- **arXiv ID**: `2303.12712`
- **arXiv URL**: `https://arxiv.org/abs/2303.12712`
- **Platform URL**: AlphaXiv, HuggingFace, Papers With Code
- **Topic**: `transformer attention mechanisms` (discovers 5 papers)

### Frontend

React app with:
- Multi-input form with auto-detection
- WebSocket streaming for real-time progress
- Paper discovery selection UI
- Results display with export options

## Development Commands

### Backend (using uv)

```bash
cd backend

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # Linux/Mac

# Install dependencies
uv pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API docs available at http://localhost:8000/docs
```

### Frontend (using bun)

```bash
cd frontend

# Install dependencies
bun install

# Run development server
bun run dev

# Build for production
bun run build
```

### Docker

```bash
cd backend
docker build -t arxiv-saas-backend .
docker run -p 8000:8000 arxiv-saas-backend
```

### Database (PostgreSQL)

```bash
# Start PostgreSQL with Docker
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=arxiv_saas \
  -p 5432:5432 \
  postgres:15
```

## Key API Endpoints

- `POST /api/analyze` - Start analysis (returns `analysis_id`, runs in background)
- `POST /api/analyze/select` - Select paper from discovery
- `GET /api/analysis/{analysis_id}` - Get analysis status/results
- `GET /api/recent` - List recent analyses
- `DELETE /api/analysis/{analysis_id}` - Delete analysis
- `WS /ws/analysis/{analysis_id}` - Real-time streaming
- `POST /api/export` - Export results (markdown, json, pdf)
- `GET /api/export/{id}/download` - Download export
- `GET /share/{token}` - Public share access

## Notes

- LLM defaults to Pollinations API (free, no key needed)
- Multi-LLM support: OpenAI, Anthropic, Ollama (via config)
- CORS allows all origins in development
- PostgreSQL required for persistence
- WebSocket for real-time progress streaming
