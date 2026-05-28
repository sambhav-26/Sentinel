# SentinelOS Backend

Autonomous AI Security Analysis Platform - FastAPI Backend

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# From root directory
docker-compose up --build
```

This starts:
- PostgreSQL database (localhost:5432)
- Redis cache (localhost:6379)
- FastAPI backend (localhost:8000)
- Next.js frontend (localhost:3000)

### Option 2: Local Development

#### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- Redis 6+

#### Setup

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. **Initialize database:**
```bash
# Run migrations (when implemented)
alembic upgrade head
```

4. **Start the server:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server runs at: http://localhost:8000

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/api/health

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Python project metadata
├── Dockerfile             # Docker image definition
├── .env.example           # Environment variables template
│
├── app/
│   ├── api/               # API routes
│   │   ├── scans.py      # Scan endpoints
│   │   ├── findings.py   # Finding endpoints
│   │   ├── attacks.py    # Attack endpoints
│   │   ├── patches.py    # Patch endpoints
│   │   ├── reports.py    # Report endpoints
│   │   └── routes.py     # Route aggregation
│   │
│   ├── agents/            # Autonomous agents
│   │   ├── base.py       # Base agent class
│   │   ├── scanner.py    # Vulnerability scanner
│   │   ├── threat.py     # Threat analysis
│   │   ├── attack.py     # Attack simulation
│   │   ├── patch.py      # Patch generation
│   │   ├── risk.py       # Risk assessment
│   │   └── report.py     # Report generation
│   │
│   ├── schemas/           # Pydantic models
│   │   ├── scan.py
│   │   ├── finding.py
│   │   ├── attack.py
│   │   ├── patch.py
│   │   └── report.py
│   │
│   ├── models/            # SQLAlchemy models
│   │   ├── database.py
│   │   └── schemas.py
│   │
│   ├── services/          # Business logic
│   │   ├── scan_service.py
│   │   ├── finding_service.py
│   │   ├── attack_service.py
│   │   ├── patch_service.py
│   │   └── report_service.py
│   │
│   ├── tools/             # External tool wrappers
│   │   ├── bandit_runner.py
│   │   ├── semgrep_runner.py
│   │   ├── npm_audit_runner.py
│   │   └── pip_audit_runner.py
│   │
│   ├── utils/             # Utility functions
│   │   ├── cwe_mapping.py
│   │   ├── mitre_mapping.py
│   │   ├── logging.py
│   │   ├── validators.py
│   │   └── helpers.py
│   │
│   ├── middleware/        # Custom middleware
│   │   ├── error_handler.py
│   │   └── logging.py
│   │
│   └── tasks/             # Background tasks
│       └── celery_tasks.py
│
├── migrations/            # Database migrations
│   └── versions/
│
├── tests/                 # Unit and integration tests
│   ├── test_agents.py
│   ├── test_api.py
│   └── test_tools.py
│
└── uploads/              # Temporary uploaded files

```

## API Endpoints (In Development)

### Scans
- `POST /api/scans` - Start a new scan
- `GET /api/scans` - List all scans
- `GET /api/scans/{scan_id}` - Get scan details
- `GET /api/scans/{scan_id}/findings` - Get findings for a scan

### Findings
- `GET /api/findings` - List all findings
- `GET /api/findings/{finding_id}` - Get finding details
- `POST /api/findings/{finding_id}/ignore` - Mark as false positive

### Attacks
- `GET /api/attacks` - List attack simulations
- `GET /api/attacks/{attack_id}` - Get attack details

### Patches
- `GET /api/patches` - List patches
- `GET /api/patches/{patch_id}` - Get patch details

### Reports
- `GET /api/reports/{scan_id}` - Get report
- `POST /api/reports/{scan_id}/export` - Export report

## Configuration

See `.env.example` for all available configuration options:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/sentinelos

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here

# LLM (Optional)
USE_LLM_FOR_PATCHES=false
LLM_PROVIDER=openai
LLM_API_KEY=your-api-key

# Scanning
SCAN_TIMEOUT_SECONDS=3600
MAX_CONCURRENT_SCANS=5
```

## Development

### Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint
flake8 app/

# Type checking
mypy app/
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify database exists

### Redis Connection Error
- Ensure Redis is running
- Check REDIS_URL in .env
- Verify Redis port (default: 6379)

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

## Performance

### Async Operations
The backend uses async/await for database and API operations:
```python
async def get_scan(scan_id: str):
    scan = await db.get_scan(scan_id)
    return scan
```

### Connection Pooling
SQLAlchemy manages database connection pools automatically.
Configure in config.py:
```python
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
```

### Caching
Redis is used for caching and Celery background jobs.
See tasks/ for background job configuration.

## Deployment

See root directory deployment guides:
- Docker: Use provided Dockerfile
- Cloud: AWS, GCP, Azure guides coming soon
- Kubernetes: Helm charts coming soon

## Contributing

1. Create a feature branch
2. Make changes following code style (black/isort)
3. Add tests
4. Submit pull request

## License

MIT License - See LICENSE file

## Support

- Documentation: https://docs.sentinelos.dev
- Issues: https://github.com/sentinelos/sentinelos/issues
- Discussions: https://github.com/sentinelos/sentinelos/discussions
