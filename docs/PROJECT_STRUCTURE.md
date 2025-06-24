# 📁 Project Structure

This document outlines the organization of the Elasticsearch Agent project.

## 🏗️ Root Directory

```
elasticsearch_agent/
├── 📖 README.md              # Main project documentation
├── 📋 SETUP.md               # Setup and installation guide
├── 📄 LICENSE                # MIT license
├── 🐳 docker-compose.yml     # Infrastructure services
├── 🔧 .gitignore             # Git ignore rules
├── 📝 .env.template          # Environment template
├── 📝 .env.example           # Environment example
├── 📊 techstack.md           # Technology stack details
└── 🔗 .gitattributes         # Git attributes
```

## 🖥️ Backend Structure

```
backend/
├── 📱 app/                   # Main application code
│   ├── 🤖 agents/           # LangGraph AI agents
│   │   └── elasticsearch_agent.py
│   ├── 🌐 api/              # REST API and WebSocket routes
│   │   ├── routes.py
│   │   └── websocket.py
│   ├── ⚙️ core/             # Core configuration and dependencies
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   ├── middleware.py
│   │   └── exceptions.py
│   ├── 📦 models/           # Pydantic data models
│   │   └── schemas.py
│   ├── 🔌 services/         # External service integrations
│   │   ├── elasticsearch.py
│   │   ├── gemini.py
│   │   ├── redis.py
│   │   └── vector_db.py
│   └── 🛠️ utils/            # Utility functions
│       ├── logging.py
│       └── sample_data.py
├── 📜 scripts/              # Utility scripts
│   ├── ingest_sample_data.py
│   ├── test_gemini.py
│   └── test_vector_db.py
├── 🧪 tests/                # Test suite
│   ├── conftest.py
│   ├── test_edge_cases.py
│   └── unit/
├── 🚀 main.py               # FastAPI application entry point
├── 📦 pyproject.toml        # Python dependencies (UV)
├── 🔒 .env.example          # Backend environment example
└── 📖 README.md             # Backend-specific documentation
```

## 🎨 Frontend Structure

```
frontend/
├── 📱 src/                  # Source code
│   ├── 🏠 app/              # Next.js App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── 🧩 components/       # React components
│   │   ├── 💬 chat/         # Chat interface components
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   └── MessageList.tsx
│   │   ├── 📊 charts/       # Chart components
│   │   │   └── ChartRenderer.tsx
│   │   ├── 🎯 ui/           # UI components (shadcn/ui)
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   └── ...
│   │   ├── ErrorBoundary.tsx
│   │   └── StatusIndicator.tsx
│   ├── 🪝 hooks/            # Custom React hooks
│   │   ├── useApi.ts
│   │   ├── useChart.ts
│   │   ├── useConnectionStatus.ts
│   │   ├── useSession.ts
│   │   └── useWebSocket.ts
│   ├── 🏪 store/            # Zustand state management
│   │   └── chatStore.ts
│   └── 📝 types/            # TypeScript definitions
│       └── api.ts
├── 🖼️ public/              # Static assets
│   ├── next.svg
│   └── ...
├── 📦 package.json          # Node.js dependencies (Bun)
├── ⚙️ next.config.ts        # Next.js configuration
├── 🎨 postcss.config.mjs    # PostCSS configuration
├── 📏 eslint.config.mjs     # ESLint configuration
├── 📘 tsconfig.json         # TypeScript configuration
├── 🔒 .env.example          # Frontend environment example
└── 📖 README.md             # Frontend-specific documentation
```

## 📚 Documentation

```
docs/
├── 📋 PROJECT_STRUCTURE.md  # This file
├── 🌍 ENVIRONMENT.md        # Environment configuration guide
├── 🔄 ENVIRONMENT_MIGRATION.md # Environment migration guide
└── ⚠️ EDGE_CASES.md         # Known edge cases and limitations
```

## 🔧 Scripts

```
scripts/
└── setup-env.sh            # Environment setup automation
```

## 🔑 Key Files

### Configuration Files
- **`.env.template`**: Master environment template
- **`docker-compose.yml`**: Infrastructure services (Elasticsearch + Redis)
- **`pyproject.toml`**: Python dependencies using UV
- **`package.json`**: Frontend dependencies using Bun

### Entry Points
- **`backend/main.py`**: FastAPI server entry point
- **`frontend/src/app/page.tsx`**: Next.js homepage

### Core Components
- **`backend/app/agents/elasticsearch_agent.py`**: Main AI agent with LangGraph workflow
- **`frontend/src/components/chat/ChatInterface.tsx`**: Main chat interface

## 🚫 Ignored Files

The following files/directories are ignored by Git (see `.gitignore`):

### Development Files
- `.agent.md`, `PHASE_REVIEW.md`, `plan.md` - Internal development notes
- `*_old.*`, `*_backup.*` - Backup files
- `*.tmp`, `*.temp` - Temporary files

### Secrets & Environment
- `.env`, `.env.local`, `.env.production` - Actual environment files
- `*.key`, `*.pem` - Certificate files
- `credentials.json`, `secrets.json` - Credential files

### Dependencies & Build Artifacts
- `node_modules/`, `.venv/` - Dependency directories
- `uv.lock`, `bun.lockb` - Lock files
- `.next/`, `build/`, `dist/` - Build outputs

### Runtime Data
- `*.log` - Log files
- `*.db`, `*.sqlite` - Database files
- `__pycache__/`, `*.pyc` - Python cache files

## 📝 Notes

- **Environment Files**: Only `.example` and `.template` files are committed
- **Dependencies**: Lock files are ignored to allow flexibility across environments
- **Development**: Internal development files are excluded from the repository
- **Security**: All credential and secret files are properly ignored

This structure ensures a clean, maintainable, and secure codebase for all contributors.
