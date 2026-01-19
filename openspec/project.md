# Project Context

## Purpose

**Lazy Rabbit Agent** is an AI-powered personalized recommendation server that leverages Large Language Models (LLMs) to provide intelligent, context-aware recommendations to users. The system integrates with multiple LLM providers, weather services, and email systems to deliver personalized experiences.

### Key Features

- **AI-Powered Recommendations**: LLM-driven personalized recommendations based on user context
- **Multi-Provider LLM Support**: OpenAI-compatible API integration (OpenAI, DeepSeek, Anthropic, Ollama)
- **Role-Based Access Control (RBAC)**: Fine-grained permission system with roles and permissions
- **Weather Integration**: Multi-provider weather service (Gaode, QWeather, OpenWeather)
- **Email Notifications**: SMTP-based email service with templating
- **User Management**: JWT-based authentication with user profiles and preferences
- **Real-time Communication**: WebSocket support for streaming responses (planned)

## Tech Stack

### Backend

- **Framework**: FastAPI 0.109+ (async Python web framework)
- **Language**: Python 3.11+
- **Database**: SQLAlchemy 2.0+ with SQLite (PostgreSQL-ready)
- **ORM**: SQLAlchemy 2.0+ (async-capable)
- **Validation**: Pydantic 2.5+ (request/response validation)
- **Authentication**: JWT tokens with python-jose + bcrypt password hashing
- **Migrations**: Alembic (database schema management)
- **Testing**: pytest with async support, pytest-asyncio, pytest-cov
- **Code Quality**: 
  - Black (code formatter, line length 88)
  - Ruff (linter, replaces flake8/isort)
  - mypy (type checker, strict mode)
- **Dependency Management**: Poetry
- **LLM Integration**: 
  - instructor (structured LLM outputs)
  - openai (OpenAI SDK)
  - httpx (async HTTP client)
- **Email**: aiosmtplib (async SMTP client)
- **Templating**: Jinja2 (email templates)
- **Caching**: cachetools
- **Configuration**: pydantic-settings (environment-based config)

### Frontend

- **Framework**: Vue.js 3.4+ (Composition API)
- **Language**: TypeScript 5.3+ (strict mode)
- **Build Tool**: Vite 5.0+
- **State Management**: Pinia 2.1+
- **Routing**: Vue Router 4.2+
- **HTTP Client**: Axios 1.6+
- **UI Utilities**: @vueuse/core 10.7+
- **Styling**: Tailwind CSS 3.4+
- **Testing**: Vitest 1.2+ with @vue/test-utils
- **Code Quality**:
  - ESLint 8.56+ with TypeScript and Vue plugins
  - Prettier 3.1+ (code formatter)
- **Package Manager**: npm

### Infrastructure

- **Reverse Proxy**: Nginx (production deployment)
- **Containerization**: Docker (via docker-compose.yml)
- **Process Management**: Makefile for development workflows

## Project Conventions

### Code Style

#### Backend (Python)

- **Formatter**: Black with 88 character line length
- **Linter**: Ruff (replaces flake8, isort, pycodestyle)
  - Line length: 88
  - Select rules: E, W, F, I, C, B
  - Ignore: E501 (line too long, handled by Black), B008, C901
- **Type Checking**: mypy in strict mode
  - `strict = true`
  - `warn_return_any = true`
  - `disallow_untyped_defs = true`
- **Naming Conventions**:
  - Classes: PascalCase (e.g., `UserService`)
  - Functions/Variables: snake_case (e.g., `get_user_by_id`)
  - Constants: UPPER_SNAKE_CASE (e.g., `API_V1_STR`)
  - Private: prefix with underscore (e.g., `_internal_method`)
- **Import Organization**: Ruff handles with isort rules
- **Docstrings**: Use triple-quoted strings for module/class/function documentation

#### Frontend (TypeScript/Vue)

- **Formatter**: Prettier (configured via ESLint)
- **Linter**: ESLint with TypeScript and Vue plugins
- **Type Checking**: TypeScript strict mode
  - `strict: true`
  - `noImplicitAny: true`
  - `strictNullChecks: true`
  - `strictFunctionTypes: true`
  - `strictBindCallApply: true`
  - `strictPropertyInitialization: true`
- **Naming Conventions**:
  - Components: PascalCase (e.g., `UserProfile.vue`)
  - Files: kebab-case for components (e.g., `user-profile.vue`), camelCase for utilities
  - Variables/Functions: camelCase (e.g., `getUserData`)
  - Constants: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)
  - Types/Interfaces: PascalCase (e.g., `UserProfile`)
- **Vue Style**:
  - Use Composition API (`<script setup>`)
  - Prefer `ref()` and `reactive()` for state
  - Use `computed()` for derived state
  - Use `watch()` and `watchEffect()` for side effects

### Architecture Patterns

#### Backend Architecture

**Layered Architecture**:
```
API Layer (app/api/v1/endpoints/)
  ↓
Service Layer (app/services/)
  ↓
Data Layer (app/models/, app/db/)
```

- **API Layer**: FastAPI route handlers, request/response validation via Pydantic schemas
- **Service Layer**: Business logic, external service integration, transaction management
- **Data Layer**: SQLAlchemy models, database session management

**Key Patterns**:
- **Dependency Injection**: FastAPI's `Depends()` for auth, database sessions, permissions
- **Repository Pattern**: Services encapsulate data access logic
- **Provider Pattern**: Abstract interfaces for LLM and weather providers (see `app/services/llm/`, `app/services/weather/`)
- **Factory Pattern**: Provider factories for creating service instances
- **RBAC Pattern**: Role-based access control with permissions (see `app/services/rbac_service.py`)

**Service Organization**:
- `user_service.py`: User management operations
- `rbac_service.py`: Role and permission management
- `recommendation_service.py`: AI recommendation generation
- `streaming_recommendation_service.py`: Streaming recommendation responses
- `llm/`: LLM provider abstraction (OpenAI-compatible)
- `weather/`: Weather provider abstraction
- `email_service.py`: SMTP email sending
- `email_template_service.py`: Email template rendering
- `prompt_service.py`: Prompt management
- `cache_service.py`: Caching utilities
- `city_service.py`: City data management

**Database Models**:
- `user.py`: User model with roles (super_admin, admin, user, guest)
- `role.py`: RBAC roles
- `permission.py`: RBAC permissions
- `role_permission.py`: Many-to-many relationship between roles and permissions
- `recommendation.py`: Recommendation records
- `city.py`: City data for weather/recommendations
- `email_log.py`: Email sending history

#### Frontend Architecture

**Component Structure**:
```
Views (src/views/)
  ↓
Components (src/components/)
  ↓
Services (src/services/)
  ↓
Stores (src/stores/)
```

- **Views**: Page-level components (routes)
- **Components**: Reusable UI components
- **Services**: API client, WebSocket client, utility functions
- **Stores**: Pinia stores for state management

**State Management**:
- **Pinia Stores**: 
  - `auth.ts`: Authentication state, user info, JWT token
  - `user.ts`: User profile data
  - `recommendations.ts`: Recommendation data
  - `weather.ts`: Weather data
  - `rbac.ts`: RBAC state (roles, permissions)
- **Reactive State**: Use Pinia stores for global state, component `ref()`/`reactive()` for local state

**Routing**:
- **Vue Router**: Client-side routing with navigation guards
- **Route Meta**: `requiresAuth`, `requiresAdmin`, `requiresSuperAdmin`, `guestOnly`
- **Navigation Guards**: Authentication and authorization checks in `router.beforeEach()`

**API Communication**:
- **Axios**: HTTP client with interceptors for auth tokens
- **Service Layer**: API services in `src/services/` (e.g., `authService.ts`, `userService.ts`)
- **Error Handling**: Centralized error handling in services

### Testing Strategy

#### Backend Testing

- **Framework**: pytest with async support
- **Test Structure**:
  - `tests/conftest.py`: Shared fixtures (test DB, client, test users)
  - `test_*.py`: Test files organized by feature
- **Fixtures**:
  - `db`: Database session (in-memory SQLite for isolation)
  - `client`: FastAPI TestClient
  - `test_user_data`: Test user credentials
  - `test_user_token`: Valid JWT token for test user
- **Coverage**: pytest-cov for coverage reports
- **Markers**: `@pytest.mark.slow`, `@pytest.mark.integration`
- **Async Tests**: Use `pytest-asyncio` with `asyncio_mode = "auto"`

**Test Database**:
- In-memory SQLite database
- Created before each test, destroyed after
- Completely isolated from production database

#### Frontend Testing

- **Framework**: Vitest with @vue/test-utils
- **Test Structure**:
  - `tests/unit/`: Unit tests for components, services, utilities
- **Component Testing**: Use `@vue/test-utils` for component rendering and interaction
- **Coverage**: Vitest coverage reports
- **UI Mode**: `vitest --ui` for interactive test runner

**Testing Commands**:
- `npm run test`: Run tests
- `npm run test:ui`: Interactive test UI
- `npm run test:coverage`: Generate coverage report

### Git Workflow

**Branch Strategy**:
- `main`: Production-ready code
- `develop`: Integration branch for features
- Feature branches: `feature/description` (e.g., `feature/add-email-notifications`)
- Bug fixes: `fix/description`
- Hotfixes: `hotfix/description`

**Commit Conventions**:
- Use descriptive commit messages
- Prefix with type: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Examples:
  - `feat: add RBAC permission system`
  - `fix: resolve JWT token expiration issue`
  - `docs: update API documentation`

**Pull Request Process**:
1. Create feature branch from `develop`
2. Make changes with tests
3. Run linters and tests (`make lint`, `make test`)
4. Create PR with description
5. Code review and approval
6. Merge to `develop`, then to `main` after testing

## Domain Context

### Core Domain Concepts

**Users & Authentication**:
- User accounts with email/password authentication
- JWT tokens for session management (15-minute expiry)
- User roles: `super_admin`, `admin`, `user`, `guest`
- User profiles with preferences

**RBAC (Role-Based Access Control)**:
- **Roles**: Named roles (e.g., "Super Administrator", "Administrator")
- **Permissions**: Fine-grained permissions with resource and action (e.g., `recommendation.admin`)
- **Role-Permission Mapping**: Many-to-many relationship
- **Permission Checks**: `require_permission()` dependency in FastAPI routes

**Recommendations**:
- AI-generated personalized recommendations
- Context-aware (user location, weather, preferences)
- Cached for performance (1-hour TTL)
- Streaming support for real-time generation

**LLM Integration**:
- Provider abstraction for multiple LLM backends
- OpenAI-compatible API interface
- Support for: OpenAI, DeepSeek, Anthropic, Ollama
- Structured outputs via `instructor` library
- Configurable models, timeouts, SSL verification

**Weather Service**:
- Multi-provider weather integration
- Providers: Gaode (高德), QWeather, OpenWeather
- City-based weather data
- Caching (1-hour TTL)

**Email System**:
- SMTP-based email sending
- Jinja2 templates for email content
- Email logging for audit trail
- Scheduled email support (cronjob integration)

**City Data**:
- City database with location information
- Used for weather and recommendation context
- Imported from CSV data

### Business Rules

1. **Authentication**: Users must sign up with email/password, then sign in to receive JWT token
2. **Authorization**: Routes protected by `require_permission()` check user's role permissions
3. **Recommendations**: Generated on-demand, cached for 1 hour, personalized by user context
4. **Email**: Sent via SMTP, logged for audit, supports HTML templates
5. **RBAC**: Super admins can manage roles and permissions, admins have elevated permissions

## Important Constraints

### Technical Constraints

- **Python Version**: Must use Python 3.11+ (type hints, modern async features)
- **Node.js Version**: Must use Node.js 16+ (for frontend)
- **Database**: SQLite for development, PostgreSQL recommended for production
- **JWT Expiry**: 15 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Password Requirements**: Minimum 8 characters (enforced by Pydantic)
- **CORS**: Configured for specific origins (default: `http://localhost:5173`)

### Security Constraints

- **Secret Key**: Must be set in production (32+ random characters)
- **HTTPS**: Required in production (use reverse proxy)
- **Password Hashing**: bcrypt with cost factor 12+ (2^12 = 4096 rounds)
- **Token Security**: JWT tokens signed with HS256, minimal payload (user ID only)
- **SQL Injection**: Protected by SQLAlchemy ORM (parameterized queries)
- **Input Validation**: All inputs validated via Pydantic schemas

### Performance Constraints

- **Recommendation Cache**: 1-hour TTL to reduce LLM API calls
- **Weather Cache**: 1-hour TTL to reduce external API calls
- **Database**: Use indexes on frequently queried columns (email, role)
- **Async Operations**: Use async/await for I/O-bound operations (LLM, email, HTTP)

### Business Constraints

- **LLM API Costs**: Cache recommendations to minimize API usage
- **Email Rate Limits**: Respect SMTP server rate limits
- **Weather API Limits**: Cache weather data to respect provider limits

## External Dependencies

### LLM Providers

- **OpenAI**: `https://api.openai.com/v1` (default)
- **DeepSeek**: OpenAI-compatible API
- **Anthropic**: Claude API (via OpenAI-compatible interface)
- **Ollama**: Self-hosted LLM (OpenAI-compatible interface)

**Configuration**:
- `LLM_PROVIDER`: Provider type
- `LLM_API_KEY`: API key (required)
- `LLM_BASE_URL`: Base URL for API
- `LLM_MODEL`: Model name (e.g., "gpt-3.5-turbo", "deepseek-chat")
- `LLM_VERIFY_SSL`: SSL verification (default: true)
- `LLM_TIMEOUT`: Request timeout in seconds (default: 30.0)

### Weather Providers

- **Gaode (高德)**: Chinese weather service
- **QWeather**: Chinese weather service
- **OpenWeather**: International weather service

**Configuration**:
- `WEATHER_PROVIDER`: Provider type
- `WEATHER_API_KEY`: Provider-specific API key (required)
- `WEATHER_BASE_URL`: Provider-specific base URL (required)
- `WEATHER_CACHE_TTL`: Cache TTL in seconds (default: 3600)

### Email Service (SMTP)

- **SMTP Server**: Configurable (default: `smtp.163.com`)
- **Port**: 465 (SSL) or 587 (TLS)
- **Authentication**: Username/password

**Configuration**:
- `MAIL_SERVER`: SMTP server hostname
- `MAIL_PORT`: SMTP port (465 for SSL, 587 for TLS)
- `MAIL_USE_SSL`: Use SSL (port 465)
- `MAIL_USE_TLS`: Use STARTTLS (port 587)
- `MAIL_USERNAME`: SMTP username
- `MAIL_PASSWORD`: SMTP password
- `MAIL_SENDER`: From email address

### Database

- **Development**: SQLite (`sqlite:///./app.db`)
- **Production**: PostgreSQL (recommended)
- **Connection String**: `DATABASE_URL` environment variable

### Reverse Proxy (Production)

- **Nginx**: Configured in `deploy/nginx/default.conf`
- **Docker Compose**: `deploy/docker-compose.yml` for containerized deployment

### Development Tools

- **Poetry**: Python dependency management
- **npm**: Node.js package management
- **Alembic**: Database migrations
- **Makefile**: Development workflow automation
