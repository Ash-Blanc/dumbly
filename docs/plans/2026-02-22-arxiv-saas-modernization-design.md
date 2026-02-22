# arXiv SaaS Generator - Modernization Design

**Date:** 2026-02-22
**Status:** Approved
**Author:** Claude Code

---

## Overview

Modernize the arXiv SaaS Generator codebase using Agno v2 patterns with modular architecture, PostgreSQL persistence, Workflow orchestration, and an enhanced React frontend with real-time streaming.

---

## Goals

- Refactor monolithic backend into clean module structure
- Use Agno Workflows for parallel/conditional step execution
- Add PostgreSQL persistence for sessions, history, and results
- Support multiple input types (arXiv ID, URLs, topics)
- Real-time streaming via WebSockets
- Export/share functionality (PDF, Markdown, JSON)
- Multi-LLM provider support with Pollinations as default

---

## Architecture

### High-Level System Design

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
│  │  /analyze  │  /analysis/{id}  │  /ws/{id}  │  /export  │  /history│  │
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
│  │                                          │ Condition: Business│ │   │
│  │                                          │ Model (ideas >= 2) │ │   │
│  │                                          └────────────────────┘ │   │
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

---

## Backend Architecture

### Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, CORS, middleware
│   ├── config.py               # Pydantic Settings for env vars
│   ├── database.py             # PostgreSQL connection, session factory
│   │
│   ├── agents/
│   │   ├── __init__.py         # Exports all agents
│   │   ├── base.py             # Shared agent config, LLM factory
│   │   ├── paper_analyzer.py   # ArxivTools agent
│   │   ├── saas_ideator.py     # DuckDuckGoTools agent
│   │   ├── business_modeler.py # Business strategy agent
│   │   ├── market_researcher.py # DuckDuckGoTools + market focus
│   │   ├── technical_architect.py # Tech assessment agent
│   │   └── paper_discovery.py  # Paper search agent
│   │
│   ├── workflows/
│   │   ├── __init__.py
│   │   ├── saas_pipeline.py    # Main Workflow with Steps
│   │   └── steps.py            # Custom Step definitions
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py         # AnalysisRequest, ExportRequest
│   │   ├── responses.py        # AnalysisResponse, StatusResponse
│   │   └── domain.py           # Analysis, Idea, BusinessModel (SQLModel)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analysis_service.py # Orchestrate workflow, manage state
│   │   ├── paper_service.py    # Input parsing, paper discovery
│   │   ├── export_service.py   # PDF, markdown, JSON exports
│   │   ├── stream_manager.py   # WebSocket broadcasting
│   │   └── repository.py       # Database operations
│   │
│   └── routers/
│       ├── __init__.py
│       ├── analysis.py         # POST /analyze, GET /analysis/{id}
│       ├── history.py          # GET /recent, DELETE /analysis/{id}
│       ├── export.py           # GET /export/{id}/{format}
│       ├── stream.py           # WebSocket for real-time updates
│       └── health.py           # GET /health
│
├── requirements.txt
├── Dockerfile
└── .env.example
```

### Key Components

#### 1. Agent Factory Pattern

```python
# agents/base.py

class LLMProvider(str, Enum):
    POLLINATIONS = "pollinations"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"

def get_model(provider: LLMProvider, api_key: str | None = None):
    """Factory for LLM models based on provider"""
    # Returns configured model instance

def create_agent(name: str, instructions: str, tools: list,
                 provider: LLMProvider = LLMProvider.POLLINATIONS,
                 api_key: str | None = None,
                 db = None) -> Agent:
    """Factory for creating agents with configured LLM"""
```

#### 2. Workflow Pipeline

```python
# workflows/saas_pipeline.py

# Step 1: Input Router (detect input type)
input_router = Router(...)

# Step 2: Paper Analysis (sequential)
paper_analysis_step = Step(name="PaperAnalysis", agent=paper_analyzer)

# Step 3: Idea Generation (sequential)
idea_generation_step = Step(name="IdeaGeneration", agent=saas_ideator)

# Step 4: Parallel Research
parallel_research = Parallel(
    Step(name="MarketResearch", agent=market_researcher),
    Step(name="TechnicalAssessment", agent=technical_architect),
)

# Step 5: Conditional Business Models
business_model_condition = Condition(
    evaluator=lambda si: len(si.previous_step_content) >= 2,
    steps=[Step(name="BusinessModeling", agent=business_modeler)],
)

# Main Workflow
saas_workflow = Workflow(
    name="ArxivSaaSPipeline",
    steps=[
        input_router,
        paper_analysis_step,
        idea_generation_step,
        parallel_research,
        business_model_condition,
    ],
)
```

#### 3. Input Types Supported

| Type | Example | Processing |
|------|---------|------------|
| arXiv ID | `2303.12712` | Direct analysis |
| arXiv URL | `https://arxiv.org/abs/2303.12712` | Extract ID → analyze |
| Platform URL | `https://alphaxiv.org/paper/...` | Extract ID → analyze |
| Topic | `transformer attention mechanisms` | Discover 5 papers → user selects |

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────────┐       ┌──────────────────────┐
│     analyses        │       │  discovered_papers   │
├─────────────────────┤       ├──────────────────────┤
│ id (PK)             │◄──────│ analysis_id (FK)     │
│ input_type          │       │ id (PK)              │
│ input_value         │       │ arxiv_id             │
│ resolved_arxiv_id   │       │ title                │
│ status              │       │ authors (JSON)       │
│ progress (JSON)     │       │ summary              │
│ paper_analysis(JSON)│       │ relevance_score      │
│ ideas (JSON)        │       │ novelty_score        │
│ business_models(JSON)│      │ selected             │
│ created_at          │       └──────────────────────┘
│ completed_at        │
│ user_id             │       ┌──────────────────────┐
└──────────┬──────────┘       │  workflow_sessions   │
           │                  ├──────────────────────┤
           │                  │ analysis_id (FK)     │
           └─────────────────►│ id (PK)              │
                              │ session_id           │
           ┌──────────────────┐│ step_history (JSON)  │
           │     exports      │└──────────────────────┘
           ├──────────────────┤
           │ analysis_id (FK) │
           │ id (PK)          │
           │ format           │
           │ share_token      │
           │ expires_at       │
           └──────────────────┘
```

### Key Tables

```python
# models/domain.py

class Analysis(SQLModel, table=True):
    id: str
    input_type: str
    input_value: str
    resolved_arxiv_id: Optional[str]
    status: str  # discovery, pending, processing, completed, error
    progress: dict  # Step status tracking
    paper_analysis: Optional[dict]
    ideas: Optional[List[dict]]
    business_models: Optional[List[dict]]
    created_at: datetime
    completed_at: Optional[datetime]

class DiscoveredPaper(SQLModel, table=True):
    id: str
    analysis_id: str  # FK
    arxiv_id: str
    title: str
    authors: List[str]
    summary: str
    relevance_score: float
    novelty_score: float
    selected: bool

class Export(SQLModel, table=True):
    id: str
    analysis_id: str  # FK
    format: str  # pdf, markdown, json
    file_path: str
    share_token: str  # For public share links
    expires_at: datetime
```

---

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze` | Start analysis from any input type |
| POST | `/api/analyze/select` | Select paper after discovery |
| GET | `/api/analysis/{id}` | Get analysis status/results |
| GET | `/api/recent` | List recent analyses |
| DELETE | `/api/analysis/{id}` | Delete analysis |
| WS | `/ws/analysis/{id}` | Real-time streaming |
| POST | `/api/export/{analysis_id}` | Create export |
| GET | `/api/export/{id}/download` | Download file |
| GET | `/share/{token}` | Public share access |
| GET | `/api/health` | Health check |

### Request/Response Models

```python
class AnalysisRequest(BaseModel):
    input: str                              # arXiv ID, URL, or topic
    input_type: Optional[InputType] = None  # Auto-detected if not provided
    max_papers: int = 5                     # For topic search
    auto_select: bool = True                # Auto-select top paper
    include_market_research: bool = True
    include_technical_assessment: bool = True
    include_business_model: bool = True
    llm_provider: str = "pollinations"
    llm_api_key: Optional[str] = None

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: str
    papers: Optional[List[dict]]  # For discovery phase
```

---

## Real-time Streaming

### WebSocket Events

```python
EVENT_TYPES = {
    "status": {"status": "str", "message": "str"},
    "discovery_start": {"topic": "str", "max_papers": 5},
    "paper_found": {"arxiv_id": "str", "title": "str", "rank": 1},
    "discovery_complete": {"papers": [...]},
    "step_start": {"step": "str", "description": "str"},
    "progress": {"step": "str", "progress": 0.5, "message": "str"},
    "thought": {"agent": "str", "thought": "str"},
    "step_complete": {"step": "str", "result_preview": "str"},
    "complete": {"paper_analysis": {...}, "ideas": [...], ...},
    "error": {"step": "str", "error": "str"},
    "cancelled": {"message": "str"},
}
```

### Stream Manager

```python
class StreamManager:
    async def connect(websocket, analysis_id)
    async def emit(analysis_id, event_type, data)
    async def emit_all(event_type, data)
```

---

## Export System

### Supported Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| JSON | Raw structured data | API integration, backup |
| Markdown | Formatted text | Documentation, notes |
| PDF | Styled document | Reports, sharing |

### Share Links

- Public access via unique token
- Configurable expiration (default 30 days)
- Download counter
- One-click copy

---

## Frontend Architecture

### Directory Structure

```
frontend/src/
├── components/
│   ├── layout/         # Header, Container, GlassCard
│   ├── input/          # AnalysisInput, InputTypeBadge, LLMConfig
│   ├── discovery/      # PaperDiscovery, PaperCard
│   ├── progress/       # WorkflowProgress, StepIndicator, AgentThoughts
│   ├── results/        # PaperSummary, IdeasGrid, IdeaCard, ExportButtons
│   └── history/        # HistoryList, HistoryItem
│
├── hooks/
│   ├── useAnalysisStream.js  # WebSocket streaming
│   ├── useAnalysis.js        # Analysis API calls
│   └── useHistory.js         # History management
│
├── contexts/
│   ├── AnalysisContext.jsx   # Global analysis state
│   └── ThemeContext.jsx      # Theme settings
│
├── utils/
│   ├── inputDetection.js     # Detect input type
│   └── formatters.js         # Format dates, scores
│
└── pages/
    ├── HomePage.jsx
    ├── AnalysisPage.jsx
    ├── HistoryPage.jsx
    └── SharePage.jsx
```

### Key Components

1. **AnalysisInput**: Auto-detects input type, shows badge, configurable LLM
2. **PaperDiscovery**: Displays discovered papers with ranking and selection
3. **WorkflowProgress**: Visual step progress with agent thought stream
4. **IdeasGrid**: Responsive grid of SaaS idea cards with export options
5. **HistoryList**: Analysis history with delete/export actions

---

## Configuration

### Environment Variables

```bash
# Application
APP_NAME=arXiv SaaS Generator
DEBUG=false
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/arxiv_saas

# LLM Providers
DEFAULT_LLM_PROVIDER=pollinations
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Pollinations (default, free)
POLLINATIONS_API_KEY=sk_2Ic2LdKet78KodrKBmDyD34ciKHUkz7D
POLLINATIONS_BASE_URL=https://gen.pollinations.ai/v1

# Redis (optional, for caching)
REDIS_URL=redis://localhost:6379

# Export settings
EXPORT_DIR=./exports
SHARE_LINK_EXPIRY_DAYS=30

# CORS
CORS_ORIGINS=*
```

---

## Dependencies

### Backend (requirements.txt)

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlmodel>=0.0.14
asyncpg>=0.29.0
agno>=2.5.3
arxiv>=2.1.0
duckduckgo-search>=4.0.0
weasyprint>=60.0  # For PDF export
python-multipart>=0.0.6
python-dotenv>=1.0.0
```

### Frontend (package.json)

```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^6.0.0",
    "lucide-react": "^0.575.0"
  },
  "devDependencies": {
    "vite": "^7.0.0",
    "@vitejs/plugin-react": "^5.0.0"
  }
}
```

---

## Migration Plan

### Phase 1: Backend Restructure
1. Create new directory structure
2. Migrate agents to separate modules
3. Implement agent factory pattern
4. Add PostgreSQL configuration

### Phase 2: Workflow Implementation
1. Create workflow with steps
2. Add parallel execution for research
3. Implement conditional business modeling
4. Add paper discovery agent

### Phase 3: Database & Persistence
1. Create SQLModel schemas
2. Implement repository pattern
3. Add session storage for workflows
4. Create export tables

### Phase 4: API & Streaming
1. Refactor routers
2. Implement WebSocket streaming
3. Add export endpoints
4. Create share link system

### Phase 5: Frontend Enhancement
1. Restructure component hierarchy
2. Add input type detection
3. Implement WebSocket hook
4. Add paper discovery UI
5. Create history page

---

## Success Criteria

- [ ] Backend fully modular with clear separation of concerns
- [ ] Workflow executes with parallel steps for faster analysis
- [ ] All input types supported (ID, URL, topic)
- [ ] PostgreSQL persistence working
- [ ] Real-time streaming via WebSocket
- [ ] Export to PDF, Markdown, JSON
- [ ] Shareable links with expiration
- [ ] Analysis history with CRUD
- [ ] Frontend displays live progress
- [ ] Multi-LLM support (Pollinations default)

---

## Future Considerations

- User authentication with JWT
- Rate limiting per user
- Redis caching for repeated queries
- Agent evaluation metrics
- A/B testing for prompt variations
- Slack/Discord integration via AgentOS
