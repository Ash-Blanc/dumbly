# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

arXiv SaaS Generator - An AI-powered application that transforms academic research papers (arXiv) into viable SaaS business opportunities using multi-agent orchestration.

## Architecture

Monorepo with two services:

```
dumbly/
├── backend/          # FastAPI Python service (port 8000)
│   ├── main.py       # Single-file FastAPI app with Agno agents
│   ├── requirements.txt
│   └── Dockerfile
└── frontend/         # React + Vite app (port 3000)
    ├── src/
    │   ├── App.jsx   # Main React component
    │   ├── main.jsx  # Entry point
    │   └── index.css # Glassmorphism styling
    └── vite.config.js  # Proxy config for /api -> backend
```

### Backend: Multi-Agent System (Agno)

The backend uses the Agno framework with 5 specialized agents:

1. **PaperAnalyzer** - Extracts innovations, novelty scores, and commercial potential from arXiv papers
2. **SaaSIdeator** - Generates SaaS business ideas with market analysis
3. **BusinessModeler** - Creates revenue models, pricing strategies, MVP roadmaps
4. **MarketResearcher** - Researches market size, competition, customer pain points (DuckDuckGo search)
5. **TechnicalArchitect** - Assesses tech stack, development effort, infrastructure needs

The `ArxivSaaSWorkflow` class orchestrates these agents sequentially:
- Paper analysis → Idea generation → Market research → Technical assessment → Business modeling

### Frontend

Single-page React app with:
- arXiv ID input form
- Polling mechanism (3s interval) for analysis progress
- Results display with paper summary and generated SaaS opportunities

## Development Commands

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# API docs available at http://localhost:8000/docs
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Docker

```bash
cd backend
docker build -t arxiv-saas-backend .
docker run -p 8000:8000 arxiv-saas-backend
```

## Key API Endpoints

- `POST /api/analyze` - Start analysis (returns `analysis_id`, runs in background)
- `GET /api/analysis/{analysis_id}` - Poll for results/progress
- `GET /api/recent` - List recent analyses
- `GET /api/health` - Health check

## Notes

- The LLM is configured to use Pollinations API (OpenAI-compatible endpoint). The model ID is `gemini-fast`.
- CORS is currently set to allow all origins (`allow_origins=["*"]`)
- Analysis results are stored in-memory (`analyses_db` dict) - not persistent
- JSON extraction from agent responses uses regex to find JSON blocks
