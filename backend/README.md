# Backend - AI Sentry Issues Explainer

Python backend application built with FastAPI for processing Sentry issues and generating technical specifications using AI.

## 🏗️ Architecture

```
backend/
├── app/
│   ├── api/            # REST API endpoints
│   ├── auth/           # Internal authentication system
│   ├── models/         # MongoDB data models
│   ├── services/       # Business logic, AI services, and monitoring
│   └── middleware/     # Custom middleware (Sentry context)
├── config/             # Configuration and environment settings
├── tests/              # Unit and integration tests
├── main.py             # FastAPI application entry point
└── requirements.txt    # Python dependencies
```

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**
   ```bash
   cp config/.env.example config/.env
   # Edit config/.env with your settings
   ```

3. **Run Development Server**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## � Monitoring with Sentry

The application includes comprehensive Sentry integration for monitoring and error tracking:

### Features:
- **Error Tracking**: Automatic capture of exceptions with context
- **Performance Monitoring**: API call timing and traces
- **User Context**: Automatic user and workspace context setting
- **Custom Events**: Tracking of AI analysis and Sentry API calls
- **Debug Endpoints**: Test Sentry integration (development only)

### Configuration:
Set the following environment variables for Sentry monitoring:
```env
APP_SENTRY_DSN=https://your-sentry-dsn@sentry.io/your-project-id
APP_SENTRY_ENVIRONMENT=development
APP_SENTRY_RELEASE=1.0.0
APP_SENTRY_TRACES_SAMPLE_RATE=0.1
APP_SENTRY_PROFILES_SAMPLE_RATE=0.1
```

### Debug Endpoints (Development Only):
- `POST /api/v1/debug/test-error` - Generate test error
- `POST /api/v1/debug/test-message` - Send test message
- `GET /api/v1/debug/sentry-status` - Check Sentry configuration

## �📋 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔧 Environment Variables

See `config/.env.example` for all required environment variables.

### Key Configuration:
- **Database**: MongoDB connection
- **Authentication**: JWT secrets and token expiration
- **OpenAI**: API key and model selection
- **Sentry (App Monitoring)**: DSN and monitoring settings
- **Sentry (Workspace)**: Optional defaults for workspace Sentry integration

## 🧪 Testing

```bash
pytest tests/
```
