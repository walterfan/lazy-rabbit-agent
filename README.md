# Lazy Rabbit Agent

A modern web application for LLM (Large Language Model) interaction with a clean, modular architecture.

## Features

- **Backend**: FastAPI-based REST API with WebSocket support
- **Frontend**: Vue.js 3 with TypeScript and Element Plus UI
- **LLM Integration**: Support for multiple LLM providers
- **Real-time Communication**: WebSocket-based streaming responses
- **Authentication**: JWT-based user authentication
- **Database**: SQLAlchemy ORM with repository pattern
- **Configuration**: Environment-based configuration management

## Architecture

### Backend Structure
```
backend/
├── app/
│   ├── core/           # Core configuration and utilities
│   ├── services/       # Business logic layer
│   ├── database/       # Database models and repositories
│   ├── api/            # API routes and endpoints
│   ├── user/           # User management
│   ├── prompt/         # Prompt management
│   └── agile/          # Agile workflow features
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/     # Reusable Vue components
│   ├── views/          # Page components
│   ├── stores/         # Pinia state management
│   ├── services/       # API and WebSocket services
│   ├── types/          # TypeScript type definitions
│   └── router/         # Vue Router configuration
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lazy-rabbit-agent
   ```

2. **Start the application**
   
   **On Linux/macOS:**
   ```bash
   ./start.sh
   ```
   
   **On Windows:**
   ```cmd
   start.bat
   ```

   The script will:
   - Create virtual environments
   - Install dependencies
   - Generate configuration files
   - Start both backend and frontend services

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup

If you prefer to set up manually:

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Configuration

### Backend Configuration

Create a `.env` file in the `backend/` directory:

```env
# Database Configuration
DATABASE_URL=sqlite:///./app.db
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PWD=password
DB_NAME=lazy_rabbit

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# LLM Configuration
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your-llm-api-key-here
LLM_MODEL=gpt-3.5-turbo
LLM_STREAM=true

# External APIs
LBS_API_KEY=your-lbs-api-key-here

# Debug
DEBUG_FLAG=false
```

### Frontend Configuration

Create a `.env` file in the `frontend/` directory:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

## Usage

### Startup Script Commands

**Linux/macOS:**
```bash
./start.sh [command]
```

**Windows:**
```cmd
start.bat [command]
```

Available commands:
- `start` (default) - Start all services
- `stop` - Stop all services
- `restart` - Restart all services
- `status` - Show service status
- `help` - Show help message

### API Usage

#### Authentication
```bash
# Login
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your_username&password=your_password"
```

#### WebSocket Connection
```javascript
const socket = new WebSocket('ws://localhost:8000/ws');
socket.onopen = () => {
  socket.send(JSON.stringify({
    model: "gpt-3.5-turbo",
    messages: [
      { role: "user", content: "Hello!" }
    ]
  }));
};
```

## Development

### Backend Development

The backend uses a layered architecture:

- **Routes**: API endpoints and request handling
- **Services**: Business logic and external service integration
- **Repositories**: Data access layer
- **Models**: Database models and schemas

### Frontend Development

The frontend uses Vue.js 3 with:

- **Composition API**: Modern Vue.js development
- **TypeScript**: Type safety and better development experience
- **Pinia**: State management
- **Element Plus**: UI component library

### Adding New Features

1. **Backend**: Add routes, services, and models following the existing patterns
2. **Frontend**: Create components, stores, and services as needed
3. **Types**: Update TypeScript interfaces for new data structures

## Testing

### Backend Testing
```bash
cd backend
source venv/bin/activate
pytest
```

### Frontend Testing
```bash
cd frontend
npm run test
```

## Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Production Deployment

1. Set up a production database (PostgreSQL/MySQL)
2. Configure environment variables for production
3. Build the frontend for production
4. Use a production WSGI server (Gunicorn) for the backend
5. Set up reverse proxy (Nginx) for static files and load balancing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at http://localhost:8000/docs
- Review the code comments and documentation

## Changelog

### v1.0.0
- Initial release with basic LLM interaction
- WebSocket support for real-time communication
- User authentication and authorization
- Modular architecture with service layer separation
- TypeScript frontend with Vue.js 3