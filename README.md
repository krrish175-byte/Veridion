# Veridion

A deterministic, multi-agent investment-reasoning system that continuously
gathers market evidence, enables collaborative reasoning among specialized AI
agents, and produces transparent, explainable investment research.

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose

### Local Infrastructure

```bash
docker compose -f infra/docker/docker-compose.yml up -d
```

This starts **Postgres 16** (port 5432) and **Redis 7** (port 6379) with
default credentials matching `packages/core/config.py`.

### Install Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

## Project Structure

```
veridion/
├── apps/api/             # FastAPI application (future)
├── apps/web/             # Web frontend (future)
├── packages/
│   ├── core/             # Config, structured logging, base errors
│   ├── evidence/         # Evidence providers (ADR-0002, future)
│   ├── agents/           # Orchestrator, Research, Critic agents
│   ├── reasoning/        # Report assembler (ADR-0003, future)
│   ├── verification/     # Verification pipeline (future)
│   ├── calibration/      # Confidence calibration (future)
│   ├── backtesting/      # Historical backtesting (future)
│   └── audit/            # Audit trail (future)
├── infra/                # Docker, migrations
├── docs/                 # Vision, ADRs
├── research/             # Knowledge base, papers
├── tests/                # Unit, integration, backtests
└── scripts/              # Utility scripts
```

## Architecture

Veridion follows a **modular monolith** architecture (see ADR-0001) with:

- **Dependency injection** — no module-level singletons
- **Structured JSON logging** with correlation IDs
- **Postgres + Redis** as the only two databases at this stage
- **pydantic** for configuration and validation

## License

MIT
