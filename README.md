# AI Sentry Issues Explainer

An intelligent web application that transforms Sentry error reports into detailed technical specifications for developers using AI analysis.

## 🚀 Overview

This application connects to your Sentry instance, analyzes error reports and issues, and generates comprehensive technical documentation and task specifications for development teams. It leverages OpenAI's language models through the Model Context Protocol (MCP) to provide intelligent analysis and recommendations.

## 📋 Features

- **Sentry Integration**: Connect to Sentry API to fetch and analyze issues
- **AI-Powered Analysis**: Uses OpenAI models via MCP Sentry to generate technical specifications
- **User Authentication**: Secure authentication via Firebase
- **Data Persistence**: MongoDB integration for storing analysis states and results
- **Modern SPA Interface**: React-based single-page application with multiple sections:
  - 📊 Dashboard - Overview and analytics
  - 🐛 Issues - Sentry issues management and analysis
  - 👥 Users - User management and permissions
  - ⚙️ Settings - Configuration and API connections

## 🏗️ Architecture

```
AI-sentry-issues-explainer/
├── backend/                 # Python backend application
│   ├── app/
│   │   ├── api/            # REST API endpoints
│   │   ├── auth/           # Firebase authentication
│   │   ├── models/         # MongoDB data models
│   │   └── services/       # Business logic and AI services
│   ├── config/             # Configuration files
│   └── tests/              # Backend tests
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # Reusable React components
│   │   ├── pages/          # Page components (Dashboard, Issues, Users, Settings)
│   │   ├── services/       # API client and external services
│   │   ├── hooks/          # Custom React hooks
│   │   ├── utils/          # Utility functions
│   │   └── styles/         # CSS/styling files
│   └── public/             # Static assets
└── README.md
```

## 🛠️ Technology Stack

### Backend
- **Python** - Core backend language
- **FastAPI/Flask** - Web framework (TBD)
- **MongoDB** - Database for storing analysis states
- **OpenAI API** - AI language model integration
- **MCP Sentry** - Model Context Protocol for Sentry integration
- **Firebase Admin SDK** - Authentication management

### Frontend
- **React** - Frontend framework
- **JavaScript** - Primary frontend language
- **Firebase SDK** - Client-side authentication
- **Axios/Fetch** - HTTP client for API communication
- **React Router** - SPA routing
- **CSS Modules/Styled Components** - Styling (TBD)

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB instance
- OpenAI API key
- Sentry account and API token
- Firebase project setup

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI-sentry-issues-explainer
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp config/.env.example config/.env
   # Configure your environment variables
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   # Configure your environment variables
   ```

### Configuration

#### Backend Environment Variables
```env
OPENAI_API_KEY=your_openai_api_key
MONGODB_URI=your_mongodb_connection_string
FIREBASE_ADMIN_SDK_PATH=path_to_firebase_admin_sdk.json
SENTRY_API_TOKEN=your_sentry_api_token
SENTRY_ORG_SLUG=your_sentry_organization
```

#### Frontend Environment Variables
```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_FIREBASE_CONFIG=your_firebase_config_json
```

### Running the Application

1. **Start Backend**
   ```bash
   cd backend
   python main.py
   ```

2. **Start Frontend**
   ```bash
   cd frontend
   npm start
   ```

The application will be available at `http://localhost:3000`

## 📝 Usage

1. **Setup**: Configure Sentry API connection in Settings
2. **Authentication**: Login using Firebase authentication
3. **Dashboard**: View overview of processed issues and analytics
4. **Issues**: Browse Sentry issues and generate technical specifications
5. **Users**: Manage team members and permissions
6. **Settings**: Configure integrations and preferences

## 🔧 Development

### Project Structure Guidelines

- **Backend**: Follow Python PEP 8 standards
- **Frontend**: Use functional components with hooks
- **API**: RESTful design principles
- **Database**: MongoDB with proper indexing
- **Testing**: Unit and integration tests for both frontend and backend

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For support and questions, please open an issue in the GitHub repository.

---

*Built with ❤️ using AI and modern web technologies*
