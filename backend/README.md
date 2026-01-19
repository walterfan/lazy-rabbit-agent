# Backend - Lazy Rabbit AI Agent Server

FastAPI-based backend server for AI-powered personalized AI Recommendations.

## 🏗️ Architecture

### Tech Stack

- **Framework**: FastAPI 0.109+ (async Python web framework)
- **Database**: SQLAlchemy 2.0+ with SQLite (PostgreSQL-ready)
- **Validation**: Pydantic 2.5+ (request/response validation)
- **Authentication**: JWT tokens with python-jose + bcrypt password hashing
- **Migrations**: Alembic (database schema management)
- **Testing**: pytest with async support
- **Code Quality**: Black, Ruff, mypy

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   │
│   ├── api/                    # API routes
│   │   ├── deps.py            # Dependency injection (auth)
│   │   └── v1/
│   │       ├── api.py         # Router aggregation
│   │       └── endpoints/
│   │           ├── auth.py    # Authentication endpoints
│   │           └── users.py   # User management endpoints
│   │
│   ├── core/                   # Core configuration
│   │   ├── config.py          # Settings (from environment)
│   │   └── security.py        # JWT & password utilities
│   │
│   ├── db/                     # Database setup
│   │   ├── base.py            # SQLAlchemy base & engine
│   │   └── session.py         # Session management
│   │
│   ├── models/                 # SQLAlchemy models
│   │   └── user.py            # User model
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py            # Auth request/response
│   │   └── user.py            # User schemas
│   │
│   └── services/               # Business logic layer
│       └── user_service.py    # User operations
│
├── alembic/                    # Database migrations
│   ├── env.py                 # Alembic environment
│   ├── versions/              # Migration scripts
│   └── script.py.mako         # Migration template
│
├── tests/                      # Test suite
│   ├── conftest.py            # Pytest fixtures
│   ├── test_auth.py           # Authentication tests
│   └── test_users.py          # User management tests
│
├── alembic.ini                 # Alembic configuration
└── pyproject.toml              # Poetry dependencies & config
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Poetry (Python dependency manager)

### Install Poetry

```bash
# macOS / Linux
curl -sSL https://install.python-poetry.org | python3 -

# Or via pip
pip install poetry
```

### Setup

```bash
# 1. Install dependencies
cd backend
poetry install

# 2. Activate virtual environment (optional)
poetry shell

# 3. Run migrations
poetry run alembic upgrade head

# 4. Start development server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the Makefile from project root:

```bash
# From project root
make install-backend  # Install dependencies
make migrate          # Run migrations
make run-backend      # Start server
```

### Access API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## 📡 API Endpoints

### Authentication

#### Sign Up
```http
POST /api/v1/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"  // optional
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "message": "User created successfully"
}
```

#### Sign In
```http
POST /api/v1/auth/signin
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### User Management

All user endpoints require authentication (Bearer token in Authorization header).

#### Get Current User
```http
GET /api/v1/users/me
Authorization: Bearer <access_token>
```

#### Update User Profile
```http
PATCH /api/v1/users/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "Jane Doe",      // optional
  "password": "newpassword123"   // optional
}
```

#### Delete Account
```http
DELETE /api/v1/users/me
Authorization: Bearer <access_token>
```

**Response: 204 No Content**

### Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy"
}
```

## 🔧 Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_auth.py

# Run with verbose output
poetry run pytest -v

# Run and show print statements
poetry run pytest -s
```

Or use Makefile:
```bash
make test-backend  # From project root
```

### Code Quality

#### Format Code
```bash
# Format with Black
poetry run black .

# Auto-fix with Ruff
poetry run ruff check --fix .
```

#### Lint Code
```bash
# Check with Ruff
poetry run ruff check .

# Type check with mypy
poetry run mypy app
```

Or use Makefile:
```bash
make format-backend  # Format code
make lint-backend    # Lint code
```

### Database Migrations

#### Create New Migration

```bash
# Auto-generate migration from model changes
poetry run alembic revision --autogenerate -m "description of changes"

# Create empty migration
poetry run alembic revision -m "description"
```

Or use Makefile:
```bash
make migrate-create  # From project root
```

#### Apply Migrations

```bash
# Upgrade to latest
poetry run alembic upgrade head

# Upgrade one version
poetry run alembic upgrade +1

# Downgrade one version
poetry run alembic downgrade -1

# Show current version
poetry run alembic current

# Show migration history
poetry run alembic history
```

### Interactive Python Shell

```bash
# With all app modules loaded
poetry shell
python

>>> from app.models.user import User
>>> from app.core.security import get_password_hash
>>> get_password_hash("test")
'$2b$12$...'
```

## ⚙️ Configuration

Configuration is managed through environment variables. See `.env.example` in project root.

### Key Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key (MUST change in production) | - |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token validity duration | `15` |
| `DATABASE_URL` | Database connection string | `sqlite:///./app.db` |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins (JSON array) | `["http://localhost:5173"]` |

### Example Configuration

```bash
# Development
DATABASE_URL=sqlite:///./app.db

# Production (PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## 🔒 Security

### Authentication Flow

1. **Sign Up**: User provides email + password → Password hashed with bcrypt (cost 12) → Stored in database
2. **Sign In**: User provides credentials → Password verified → JWT token generated (15 min expiry)
3. **Protected Routes**: Client includes token in Authorization header → Token validated → User info extracted

### Password Security

- **Hashing**: bcrypt with cost factor 12+ (2^12 = 4096 rounds)
- **Requirements**: Minimum 8 characters (enforced by Pydantic)
- **Storage**: Only hashed passwords stored, never plain text
- **Validation**: Constant-time comparison to prevent timing attacks

### JWT Tokens

- **Algorithm**: HS256 (HMAC with SHA-256)
- **Expiry**: 15 minutes (configurable)
- **Payload**: User ID only (minimal data exposure)
- **Signature**: Verified on every request

### Security Best Practices

✅ **Implemented:**
- CORS configuration (whitelist origins)
- SQL injection protection (SQLAlchemy ORM)
- Password hashing (bcrypt)
- Token-based authentication
- Input validation (Pydantic)
- HTTPS ready (use reverse proxy in production)

⚠️ **TODO for Production:**
- Rate limiting (e.g., slowapi, fastapi-limiter)
- Request logging
- Security headers (helmet equivalent)
- HTTPS enforcement
- Token refresh mechanism
- Account lockout after failed attempts

## 🧪 Testing

### Test Structure

```
tests/
├── conftest.py           # Shared fixtures (test DB, client, test user)
├── test_auth.py          # Authentication endpoint tests
└── test_users.py         # User management endpoint tests
```

### Test Database

Tests use an in-memory SQLite database that is:
- Created before each test
- Destroyed after each test
- Completely isolated

### Writing Tests

```python
def test_example(client, test_user_token):
    """Test example endpoint."""
    response = client.get(
        "/api/v1/example",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

### Available Fixtures

- `db`: Database session
- `client`: TestClient instance
- `test_user_data`: Dict with test user credentials
- `test_user_token`: Valid JWT token for test user

## 📊 Database Schema

### User Model

```python
class User(Base):
    __tablename__ = "users"
    
    id: int (Primary Key)
    email: str (Unique, Indexed)
    hashed_password: str
    full_name: str (Optional)
    is_active: bool (Default: True)
    created_at: datetime
    updated_at: datetime
```

### Indexes

- `users.id` - Primary key (automatic)
- `users.email` - Unique index for fast lookups

## 🚢 Deployment

### Production Checklist

- [ ] Set strong `SECRET_KEY` (32+ random characters)
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS (reverse proxy: nginx, traefik)
- [ ] Set `ENVIRONMENT=production` in .env
- [ ] Configure CORS for production frontend URL
- [ ] Setup proper logging (file + monitoring service)
- [ ] Implement rate limiting
- [ ] Add health check monitoring
- [ ] Setup automated backups
- [ ] Configure email service (for future features)

### Production Server

```bash
# Install production dependencies
poetry install --no-dev

# Run with multiple workers
poetry run uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-config logging.conf
```

### Docker Deployment (Future)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev
COPY . .
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

## 🔍 Troubleshooting

### Common Issues

#### Database locked error (SQLite)
**Cause**: Multiple processes accessing SQLite simultaneously

**Solution**: Use PostgreSQL for production, or:
```python
# In config.py
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30}
)
```

#### Import errors
**Cause**: Not in virtual environment or dependencies not installed

**Solution**:
```bash
poetry install
poetry shell
```

#### Migration conflicts
**Cause**: Multiple migrations created simultaneously

**Solution**:
```bash
# Downgrade and reapply
poetry run alembic downgrade -1
poetry run alembic upgrade head
```

#### Port already in use
**Cause**: Another process using port 8000

**Solution**:
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or use different port
poetry run uvicorn app.main:app --port 8001
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [pytest Documentation](https://docs.pytest.org/)

## 🤝 Contributing

1. Follow the code style guide in `openspec/project.md`
2. Write tests for new features
3. Run linters before committing
4. Update this README if adding new endpoints or features

## 📄 License

[Your License Here]

