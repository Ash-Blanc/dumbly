# arXiv SaaS Generator

Transform academic research papers from arXiv into viable SaaS business opportunities using AI-powered multi-agent orchestration.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-orange.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19+-blue.svg)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Overview

arXiv SaaS Generator analyzes academic papers and generates comprehensive business intelligence including:

- **Paper Analysis** - Extract innovations, novelty scores, and technical details
- **SaaS Ideation** - Generate viable business ideas from research
- **Market Research** - Analyze market size, competition, and trends
- **Technical Assessment** - Evaluate development effort and tech stack
- **Business Modeling** - Create revenue models and pricing strategies

## Quick Start

### Prerequisites

- Node.js 18+ (for frontend)
- Python 3.12+ with [uv](https://github.com/astral-sh/uv) (for backend)
- Docker (for PostgreSQL database)

### Single Command

```bash
npm install && npm run dev
```

This starts all three services:
- PostgreSQL database on port 5432
- FastAPI backend on port 8000
- React frontend on port 5173

### Individual Services

```bash
# Start only the database
npm run dev:db

# Start only the backend
npm run dev:backend

# Start only the frontend
npm run dev:frontend

# Stop all services
npm run stop

# Stop and remove database volumes
npm run clean
```

## Input Types

The system supports multiple input formats:

| Type | Example | Description |
|------|---------|-------------|
| arXiv ID | `2303.12712` | Direct paper analysis |
| arXiv URL | `https://arxiv.org/abs/2303.12712` | Extracts ID automatically |
| Platform URL | `https://alphaxiv.org/paper/...` | Works with AlphaXiv, HuggingFace, Papers With Code |
| Topic | `transformer attention mechanisms` | Discovers 5 relevant papers for selection |

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Frontend (React/Vite)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ Input UI    │  │ WebSocket   │  │ Results     │  │ History/    │   │
│  │ (multi-type)│  │ Streaming   │  │ Display     │  │ Export      │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                    HTTP API + WebSocket
                                   │
┌──────────────────────────────────▼──────────────────────────────────────┐
│                        Backend (FastAPI)                                │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Routers Layer                               │   │
│  │  /analyze  │  /analysis/{id}  │  /ws/{id}  │  /export  │  /health│  │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     Services Layer                               │   │
│  │  AnalysisService │ PaperService │ ExportService │ StreamManager │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Agno Workflow Layer                           │   │
│  │  ┌─────────┐   ┌─────────┐   ┌─────────────┐   ┌──────────────┐ │   │
│  │  │ Router  │──►│ Paper   │──►│ Idea        │──►│ Parallel     │ │   │
│  │  │(input)  │   │Analysis │   │ Generation  │   │ Research     │ │   │
│  │  └─────────┘   └─────────┘   └─────────────┘   └──────────────┘ │   │
│  │                                                      │          │   │
│  │                                          ┌───────────▼────────┐ │   │
│  │                                          │ Business Model     │ │   │
│  │                                          │ (conditional)      │ │   │
│  │                                          └────────────────────┘ │ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Agents Layer                                │   │
│  │  PaperAnalyzer │ SaaSIdeator │ MarketResearcher │ TechArchitect │   │
│  │  BusinessModeler │ PaperDiscovery                                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────────┐
│                        Database (PostgreSQL)                            │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  ┌────────────┐  │
│  │ analyses    │  │ discovered_  │  │ workflow_     │  │ exports    │  │
│  │             │  │ papers       │  │ sessions      │  │            │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  └────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Backend Modules

```
backend/app/
├── main.py              # FastAPI app entry point
├── config.py            # Pydantic Settings
├── database.py          # PostgreSQL connection
├── agents/              # 6 specialized Agno agents
│   ├── base.py          # LLM factory pattern
│   ├── paper_analyzer.py
│   ├── saas_ideator.py
│   ├── market_researcher.py
│   ├── technical_architect.py
│   ├── business_modeler.py
│   └── paper_discovery.py
├── workflows/           # Agno Workflow orchestration
│   ├── saas_pipeline.py
│   └── steps.py
├── models/              # SQLModel + Pydantic
│   ├── domain.py        # Database models
│   ├── requests.py      # API request schemas
│   └── responses.py     # API response schemas
├── services/            # Business logic
│   ├── analysis_service.py
│   ├── paper_service.py
│   ├── export_service.py
│   ├── stream_manager.py
│   └── repository.py
└── routers/             # API endpoints
    ├── analysis.py
    ├── history.py
    ├── export.py
    ├── stream.py
    └── health.py
```

## API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze` | Start analysis from any input type |
| POST | `/api/analyze/select` | Select paper after discovery |
| GET | `/api/analysis/{id}` | Get analysis status/results |
| GET | `/api/recent` | List recent analyses |
| DELETE | `/api/analysis/{id}` | Delete analysis |
| WS | `/ws/analysis/{id}` | Real-time streaming |
| POST | `/api/export` | Export results (markdown, json, pdf) |
| GET | `/api/export/{id}/download` | Download export |
| GET | `/share/{token}` | Public share access |
| GET | `/api/health` | Health check |

## Configuration

### Environment Variables

Create a `backend/.env` file (copy from `.env.example`):

```bash
# Application
APP_NAME=arXiv SaaS Generator
DEBUG=true
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/arxiv_saas

# LLM Providers (optional - Pollinations is free and works by default)
DEFAULT_LLM_PROVIDER=pollinations
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Export settings
EXPORT_DIR=./exports
SHARE_LINK_EXPIRY_DAYS=30

# CORS
CORS_ORIGINS=*
```

### LLM Providers

The system supports multiple LLM providers:

- **Pollinations** (default, free) - No API key required
- **OpenAI** - Requires API key
- **Anthropic** - Requires API key
- **Ollama** - Local LLM server

## Development

### Backend

```bash
cd backend

# Create virtual environment
uv venv
source .venv/bin/activate  # Linux/Mac

# Install dependencies
uv pip install -e .

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest
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
# Build backend image
docker build -t arxiv-saas-backend .

# Run with database
docker-compose up -d

# Run backend
docker run -p 8000:8000 --env-file backend/.env arxiv-saas-backend
```

## Project Status

- ✅ Multi-agent orchestration with Agno v2
- ✅ PostgreSQL persistence
- ✅ Workflow orchestration with parallel steps
- ✅ Multiple input type support
- ✅ Real-time WebSocket streaming
- ✅ Export to PDF, Markdown, JSON
- ✅ Shareable links with expiration
- ✅ Analysis history management
- ✅ Multi-LLM provider support

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Acknowledgments

- Powered by [Agno](https://github.com/agno-agi/agno) for multi-agent orchestration
- Uses [FastAPI](https://fastapi.tiangolo.com/) for the backend
- Built with [React](https://react.dev/) and [Vite](https://vitejs.dev/)
- Database powered by [PostgreSQL](https://www.postgresql.org/)
