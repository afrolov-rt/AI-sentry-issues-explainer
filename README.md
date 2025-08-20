# 🧠 AI Sentry Issues Explainer

An intelligent web application that transforms Sentry error reports into detailed AI-powered analysis and actionable technical insights for developers.

Webpage of the project:
https://ai-sentry.tvoysad.by/

## 🚀 Overview

This application connects to your Sentry instance, fetches error reports and issues, and generates comprehensive AI-powered analysis including root cause identification, impact assessment, and suggested fixes. It features an intuitive dashboard with real-time Sentry event generation for testing and a comprehensive analysis management system.

## ✨ Key Features

### 🔍 **Smart Analysis Engine**
- **AI-Powered Issue Analysis**: Advanced OpenAI integration for detailed error analysis
- **Root Cause Detection**: Intelligent identification of underlying problems
- **Impact Assessment**: Severity and scope analysis with priority recommendations
- **Suggested Fixes**: Actionable remediation strategies and implementation guidance

### 📊 **Interactive Dashboard**
- **Real-time Statistics**: Live overview of processed issues with visual indicators
- **Sentry Event Generation**: Built-in tools to generate test events (Error, Warning, Info types)
- **One-click Analysis**: Direct analysis initiation from issue cards
- **Clickable Cards**: Instant access to detailed analysis results

### 📝 **Analysis Management**
- **Dedicated AI Analyses Page**: Centralized view of all AI-generated analyses
- **Detailed Analysis View**: Comprehensive breakdown including:
  - Executive Summary
  - Root Cause Analysis
  - Impact Assessment
  - Step-by-step Reproduction
  - Suggested Fixes
  - Effort Estimation
  - Priority Classification
- **Status Tracking**: Real-time analysis progress monitoring

### � **Advanced Configuration**
- **Workspace Management**: Multi-workspace support with individual Sentry configurations
- **Dynamic DSN Configuration**: Flexible Sentry Data Source Name management
- **Authentication System**: Secure access control
- **API Integration**: Seamless Sentry API connectivity

## 🏗️ Architecture

```
AI-sentry-issues-explainer/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── api/            # REST API endpoints
│   │   │   ├── dashboard.py    # Dashboard statistics
│   │   │   ├── issues.py       # Issue management
│   │   │   ├── analyses.py     # AI analysis endpoints
│   │   │   ├── sentry_events.py # Event generation
│   │   │   └── settings.py     # Configuration management
│   │   ├── models/         # MongoDB data models
│   │   ├── services/       # Business logic
│   │   │   ├── openai_service.py      # AI analysis service
│   │   │   ├── sentry_service.py      # Sentry integration
│   │   │   └── sentry_event_generator.py # Event generation
│   │   └── database/       # Database utilities
│   ├── config/             # Environment configuration
│   └── main.py             # Application entry point
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   │   └── DashboardLayout.tsx
│   │   ├── pages/          # Main application pages
│   │   │   ├── DashboardPage.tsx   # Main dashboard
│   │   │   ├── IssuesPage.tsx      # Issues management
│   │   │   ├── AnalysesPage.tsx    # AI analyses view
│   │   │   └── SettingsPage.tsx    # Configuration
│   │   ├── services/       # API clients
│   │   ├── hooks/          # Custom React hooks
│   │   ├── types/          # TypeScript definitions
│   │   └── utils/          # Utility functions
│   └── public/             # Static assets
└── docs/                   # Documentation
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.8+** - Core backend language
- **MongoDB** - NoSQL database for flexible data storage
- **OpenAI API** - GPT-4 integration for intelligent analysis
- **Sentry SDK** - Event generation and monitoring
- **Pydantic** - Data validation and settings management
- **Motor** - Async MongoDB driver

### Frontend
- **React 18** - Modern frontend framework with hooks
- **TypeScript** - Type-safe JavaScript development
- **Material-UI** - Comprehensive React component library
- **React Router** - Client-side routing
- **Axios** - HTTP client for API communication
- **Modern CSS** - Flexbox and Grid layouts

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **MongoDB** (local or cloud instance)
- **OpenAI API Key** (for AI analysis)
- **Sentry Account** with DSN (for event generation and monitoring)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/afrolov-rt/AI-sentry-issues-explainer.git
   cd AI-sentry-issues-explainer
   ```

2. **Backend Setup**
   ```bash
   cd backend
   
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure environment
   cp config/.env.example config/.env
   # Edit config/.env with your settings
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   
   # Install dependencies
   npm install
   
   # Configure environment (optional)
   # Default settings work with backend on localhost:8000
   ```

4. **Database Setup**
   ```bash
   # Ensure MongoDB is running
   # Default connection: mongodb://localhost:27017
   # Database will be created automatically
   ```

### Configuration

#### Backend Environment Variables (`backend/config/.env`)

```env
# Environment Configuration
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000

# Database
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=sentry_ai_explainer_test

# OpenAI API (Required for AI analysis)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4

# Sentry Configuration (Optional - can be configured per workspace)
SENTRY_API_TOKEN=your-sentry-api-token
SENTRY_ORG_SLUG=your-organization-slug
SENTRY_BASE_URL=https://sentry.io/api/0

# Application Sentry DSN (for event generation and monitoring)
APP_SENTRY_DSN=your-sentry-dsn-here
APP_SENTRY_ENVIRONMENT=development
APP_SENTRY_RELEASE=1.0.0
APP_SENTRY_TRACES_SAMPLE_RATE=0.1
APP_SENTRY_PROFILES_SAMPLE_RATE=0.1

# Security
SECRET_KEY=your-secret-key-for-development
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

#### Frontend Configuration
The frontend automatically connects to `http://localhost:8000` by default. No additional configuration required for development.

### Running the Application

1. **Start Backend Server**
   ```bash
   cd backend
   source .venv/bin/activate  # Activate virtual environment
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend Development Server**
   ```bash
   cd frontend
   npm start
   ```

3. **Access the Application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

## � Usage Guide

### 1. **Dashboard Overview**
- View real-time statistics of processed issues
- Generate test Sentry events (Error, Warning, Info)
- Quick access to recent issues with one-click analysis
- Visual indicators for analysis status

### 2. **Issue Analysis**
- Click "Analyze" on any issue card
- AI generates comprehensive analysis including:
  - **Summary**: Executive overview of the issue
  - **Root Cause**: Technical analysis of underlying problems
  - **Impact Assessment**: Severity and scope evaluation
  - **Reproduction Steps**: Step-by-step recreation guide
  - **Suggested Fixes**: Actionable remediation strategies
  - **Effort Estimation**: Development time assessment
  - **Priority Classification**: Critical, High, Medium, Low

### 3. **AI Analyses Management**
- Navigate to "AI Analyses" tab
- View all generated analyses
- Click any analysis card for detailed view
- Filter by status or priority

### 4. **Event Generation (Testing)**
- Use dashboard buttons to generate test events
- Choose event type: Error, Warning, or Info
- Specify quantity (1-10 events)
- Events appear in Sentry dashboard within moments

### 5. **Workspace Configuration**
- Configure individual workspace settings
- Set custom Sentry DSN per workspace
- Manage API tokens and organization settings

## �️ Development

### Project Structure

- **Backend**: FastAPI with async/await patterns
- **Frontend**: Modern React with TypeScript and hooks
- **Database**: MongoDB with async operations
- **API**: RESTful design with OpenAPI documentation
- **AI Integration**: OpenAI GPT-4 for intelligent analysis
- **Event Generation**: Sentry SDK for testing and monitoring

### Key Components

#### Backend Services
- `OpenAIService`: AI analysis engine
- `SentryService`: Sentry API integration
- `SentryEventGenerator`: Test event generation
- `DatabaseService`: MongoDB operations

#### Frontend Pages
- `DashboardPage`: Main overview with statistics and event generation
- `AnalysesPage`: AI analysis management and viewing
- `IssuesPage`: Issue browsing and analysis initiation
- `SettingsPage`: Configuration and workspace management

### API Endpoints

#### Dashboard
- `GET /api/v1/dashboard/stats` - Get dashboard statistics
- `GET /api/v1/dashboard/recent-issues` - Fetch recent issues

#### Analysis
- `POST /api/v1/issues/{issue_id}/analyze` - Start AI analysis
- `GET /api/v1/analyses` - List all analyses
- `GET /api/v1/analyses/{analysis_id}` - Get specific analysis

#### Sentry Events
- `POST /api/v1/sentry/generate-random-event` - Generate test events
- `GET /api/v1/sentry/sentry-status-public` - Check Sentry status

### Development Guidelines

1. **Code Quality**: Follow TypeScript/Python best practices
2. **Error Handling**: Comprehensive error catching and user feedback
3. **Performance**: Async operations and efficient data fetching
4. **UI/UX**: Material-UI for consistent design
5. **Testing**: Generate test events for development
6. **Documentation**: Keep API docs updated

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🔧 Advanced Configuration

### Custom Sentry Integration
- Configure workspace-specific DSN in Settings
- Use built-in event generator for testing
- Monitor application performance with Sentry

### AI Model Configuration
- Supports OpenAI GPT-4 and GPT-3.5-turbo
- Configurable analysis depth and focus areas
- Token usage optimization

### Database Optimization
- Automatic indexing for performance
- Configurable connection pools
- Data retention policies

## 🚨 Troubleshooting

### Common Issues

1. **"Sentry not configured"**: Set `APP_SENTRY_DSN` in backend config
2. **"Analysis failed"**: Check OpenAI API key and rate limits
3. **"Database connection error"**: Ensure MongoDB is running
4. **"Frontend connection refused"**: Verify backend is running on port 8000

### Debug Mode
Set `DEBUG=True` in backend configuration for detailed error messages.

## 📊 Monitoring

- **Sentry Integration**: Automatic error monitoring and performance tracking
- **API Metrics**: Request/response monitoring via FastAPI
- **Database Metrics**: MongoDB operation tracking
- **AI Usage**: OpenAI token consumption monitoring

## 🔐 Security

- **Environment Variables**: Sensitive data stored in `.env` files
- **API Security**: Request validation and rate limiting
- **Database Security**: Connection encryption and access control
- **CORS Configuration**: Controlled cross-origin requests

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

For support, questions, or feature requests:

- **GitHub Issues**: [Open an issue](https://github.com/afrolov-rt/AI-sentry-issues-explainer/issues)
- **Documentation**: Check the `/docs` folder for detailed guides
- **API Documentation**: Available at `http://localhost:8000/docs` when running

## 🎯 Roadmap

- [ ] **Enhanced AI Analysis**: More detailed code suggestions
- [ ] **Team Collaboration**: Multi-user workspace management
- [ ] **Integration Expansion**: Support for more monitoring tools
- [ ] **Advanced Filtering**: Smart issue categorization
- [ ] **Notification System**: Real-time analysis updates
- [ ] **Export Features**: Analysis reports in multiple formats

---

*Built with ❤️ using FastAPI, React, and OpenAI • Empowering developers with AI-driven insights*
