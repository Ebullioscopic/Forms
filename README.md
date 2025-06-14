# Forms - Real-time Collaborative Form System

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

A real-time collaborative form filling platform that allows multiple users to simultaneously work on a single shared form response, similar to Google Docs but for structured forms.

## 🚀 Live Demo

**Production URL**: [https://collaborative-forms.onrender.com](https://collaborative-forms.onrender.com)

**Demo Credentials**:
- Admin: `admin` / `password123`
- User: `testuser` / `password123`

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Technologies Used](#-technologies-used)
- [Setup & Installation](#-setup--installation)
- [Deployment](#-deployment)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Design Decisions](#-design-decisions)
- [Edge Cases Handled](#-edge-cases-handled)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🔄 Real-time Collaboration
- **Simultaneous Editing**: Multiple users can edit the same form response in real-time
- **Live Synchronization**: Changes are instantly synchronized via WebSocket connections
- **Active User Presence**: See who's currently editing the form with live user indicators
- **Field Locking**: Prevents edit conflicts with automatic field locking mechanism

### 👥 User Management
- **Role-based Access Control**: 
  - **Admins**: Create, edit, and manage forms and fields
  - **Users**: Join forms via share codes and collaborate
- **Custom User Model**: Extended Django user model with role management
- **Secure Authentication**: Django's built-in authentication with CSRF protection

### 📝 Dynamic Form Management
- **Multiple Field Types**: Text, number, email, dropdown, textarea, checkbox, radio buttons
- **Dynamic Field Creation**: Admins can add, edit, and delete fields on the fly
- **Form Sharing**: Unique 8-character share codes for easy form access
- **Single Shared Response**: One collective response per form, editable by all collaborators

### 🎨 Modern UI/UX
- **Google Forms-inspired Design**: Clean, professional grayscale interface
- **Responsive Layout**: Bootstrap 5-based responsive design
- **Real-time Visual Feedback**: Live editing indicators and user presence
- **Accessibility**: Proper ARIA labels and keyboard navigation support

## 🏗 Architecture

### System Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Django +      │    │   Database      │
│   (Bootstrap 5) │◄──►│   Channels      │◄──►│   PostgreSQL    │
│   + WebSocket   │    │   (ASGI)        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │  (Channel Layer)│
                       └─────────────────┘
```

### Key Components

1. **Django Framework**: Core web framework for HTTP requests, authentication, and ORM
2. **Django Channels**: Adds asynchronous WebSocket support for real-time features
3. **Redis**: Channel layer backend for message brokering and state synchronization
4. **PostgreSQL**: Primary database with JSON field support for flexible form responses
5. **Daphne**: Production ASGI server optimized for Django Channels
6. **Bootstrap 5**: Modern, responsive UI framework

## 🛠 Technologies Used

| Technology | Purpose | Why Chosen |
|------------|---------|------------|
| **Django 4.2** | Web Framework | Robust, mature Python framework with excellent ORM and admin interface |
| **Django Channels 4.0** | WebSocket Support | Seamless integration with Django for real-time features |
| **Redis 4.6** | Message Broker | Fast in-memory store perfect for pub/sub and channel layers |
| **PostgreSQL** | Database | Reliable RDBMS with JSON field support for flexible form storage |
| **Bootstrap 5** | Frontend Framework | Modern CSS framework for rapid, responsive UI development |
| **Daphne** | ASGI Server | Recommended production server for Django Channels applications |
| **Python-Decouple** | Configuration | Secure environment variable management |
| **WhiteNoise** | Static Files | Efficient static file serving without separate web server |

## 🚀 Setup & Installation

### Prerequisites
- Python 3.11+
- Redis server (for local development)
- Git

### Local Development Setup

1. **Clone the repository**
   ```
   git clone https://github.com/Ebullioscopic/Forms.git
   cd Forms
   ```

2. **Create and activate virtual environment**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   Create a `.env` file in the `collaborative_forms/` directory:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   REDIS_URL=redis://localhost:6379/0
   ALLOWED_HOSTS=127.0.0.1,localhost
   # DATABASE_URL not needed for local SQLite
   ```

5. **Run database migrations**
   ```
   cd collaborative_forms
   python manage.py makemigrations accounts
   python manage.py makemigrations forms
   python manage.py migrate
   ```

6. **Create a superuser**
   ```
   python manage.py createsuperuser
   ```

7. **Start Redis server** (in a separate terminal)
   ```
   # macOS with Homebrew
   brew install redis
   redis-server
   
   # Ubuntu/Debian
   sudo apt-get install redis-server
   redis-server
   
   # Docker alternative
   docker run -d -p 6379:6379 redis:alpine
   ```

8. **Run the development server**
   ```
   daphne collaborative_forms.asgi:application --port 8000 --bind 0.0.0.0 -v2
   ```

9. **Access the application**
   Open your browser to: `http://127.0.0.1:8000`

## 🌐 Deployment

### Deploy to Render.com

1. **Push to GitHub**
   ```
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Connect to Render**
   - Sign up at [render.com](https://render.com)
   - Connect your GitHub repository
   - Use the provided `render.yaml` blueprint

3. **Automatic Deployment**
   Render will automatically:
   - Create PostgreSQL and Redis services
   - Run `build.sh` to install dependencies and migrate
   - Start the app with Daphne
   - Set up environment variables

4. **Post-deployment Setup**
   ```
   # In Render Shell, create superuser
   python manage.py createsuperuser
   ```

### Environment Variables (Production)
```
DATABASE_URL=postgresql://... (auto-set by Render)
REDIS_URL=redis://... (auto-set by Render)
SECRET_KEY=auto-generated
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-app.onrender.com
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /accounts/login/` - User login
- `POST /accounts/register/` - User registration
- `GET /accounts/logout/` - User logout

### Form Management Endpoints
- `GET /forms/` - Dashboard (list user's forms)
- `POST /forms/create/` - Create new form (admin only)
- `GET /forms/edit//` - Edit form and fields (admin only)
- `POST /forms/join/` - Join form with share code
- `GET /forms/collaborate//` - Collaboration interface

### WebSocket Endpoints
- `ws://domain/ws/forms//` - Real-time collaboration channel

### WebSocket Message Types
```
// Field change
{
    "action": "field_change",
    "field_id": "field_1",
    "value": "new value"
}

// Field focus/blur
{
    "action": "field_focus", // or "field_blur"
    "field_id": "field_1"
}
```

## 📁 Project Structure

```
Forms/                          # Root repository folder
├── build.sh                   # Build script for deployment
├── render.yaml                # Render deployment blueprint
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .gitignore                 # Git ignore rules
└── collaborative_forms/       # Django project folder
    ├── manage.py              # Django management script
    ├── .env                   # Environment variables (local)
    ├── collaborative_forms/   # Project settings and ASGI
    │   ├── __init__.py
    │   ├── asgi.py           # ASGI configuration for WebSocket
    │   ├── settings.py       # Django settings
    │   ├── urls.py           # Main URL routing
    │   └── wsgi.py           # WSGI configuration
    ├── accounts/              # Custom user authentication app
    │   ├── migrations/        # Database migrations
    │   ├── __init__.py
    │   ├── admin.py          # Admin interface config
    │   ├── apps.py           # App configuration
    │   ├── forms.py          # Django forms
    │   ├── models.py         # User model with roles
    │   ├── urls.py           # URL routing
    │   └── views.py          # View functions
    ├── forms/                 # Form management and collaboration app
    │   ├── migrations/        # Database migrations
    │   ├── __init__.py
    │   ├── admin.py          # Admin interface config
    │   ├── apps.py           # App configuration
    │   ├── consumers.py      # WebSocket consumers
    │   ├── forms.py          # Django forms
    │   ├── models.py         # Form, Field, Response models
    │   ├── routing.py        # WebSocket URL routing
    │   ├── urls.py           # HTTP URL routing
    │   └── views.py          # View functions
    ├── templates/             # HTML templates
    │   ├── base.html         # Base template with navigation
    │   ├── accounts/         # Authentication templates
    │   │   ├── login.html
    │   │   └── register.html
    │   └── forms/            # Form-related templates
    │       ├── collaborate.html    # Real-time collaboration interface
    │       ├── create_form.html    # Form creation
    │       ├── dashboard.html      # User dashboard
    │       ├── edit_form.html      # Form editing
    │       └── join_form.html      # Join form with share code
    ├── static/               # Static assets (CSS, JS, images)
    │   ├── css/
    │   ├── js/
    │   └── img/
    └── staticfiles/          # Collected static files (production)
```

## 🎯 Design Decisions

### Single Shared Response Architecture
Unlike traditional forms where each user submits individual responses, CollabForms implements a **collaborative single response** model:
- One `FormResponse` object per `Form`
- Multiple users edit the same response simultaneously
- Real-time synchronization ensures consistency

### Field Locking Strategy
To prevent edit conflicts in real-time collaboration:
- **Optimistic Locking**: Users can start editing any unlocked field
- **Focus-based Locks**: Fields are locked when a user focuses on them
- **Automatic Release**: Locks are released on blur or user disconnect
- **Visual Indicators**: Locked fields are highlighted with user attribution

### WebSocket Architecture
Real-time features are implemented using Django Channels:
- **Consumer-based**: Each form has its own WebSocket consumer group
- **Redis Channel Layer**: Messages are broadcast via Redis pub/sub
- **Authenticated Connections**: WebSocket connections inherit Django session auth
- **Graceful Degradation**: Forms remain functional if WebSocket connection fails

### Data Storage Strategy
- **PostgreSQL JSON Fields**: Form responses stored as flexible JSON
- **Normalized Schema**: Forms, fields, and metadata in relational tables
- **Audit Trail**: Tracks last editor and edit timestamps
- **Active User Tracking**: Temporary session-based user presence

## 🛡 Edge Cases Handled

### Connection Management
- **Abrupt Disconnects**: Automatic cleanup of field locks and user presence
- **WebSocket Reconnection**: Client-side reconnection logic with exponential backoff
- **Connection Status**: Real-time connection status indicator for users

### Data Consistency
- **Concurrent Edits**: Field locking prevents simultaneous edits on same field
- **Transaction Safety**: Database operations use atomic transactions
- **Validation**: Both client-side and server-side validation for form fields
- **Type Safety**: Proper handling of different field types (text, number, etc.)

### Security
- **CSRF Protection**: Proper CSRF token usage for all forms
- **Origin Validation**: Configured trusted origins for production deployment
- **Authentication**: All WebSocket connections authenticated via Django sessions
- **Role-based Access**: Proper permission checks for admin vs user actions

### Performance
- **Efficient Queries**: Optimized database queries with select_related/prefetch_related
- **Static File Optimization**: WhiteNoise for efficient static file serving
- **Redis Optimization**: Configured capacity and expiry for channel layers
- **Connection Pooling**: Database connection pooling for production

### User Experience
- **Loading States**: Visual feedback for all async operations
- **Error Handling**: Graceful error messages and fallback behaviors
- **Mobile Responsiveness**: Full mobile support with touch-friendly interface
- **Accessibility**: ARIA labels and keyboard navigation support

## 🔧 Development

### Running Tests
```
python manage.py test
```

### Code Quality
```
# Install development dependencies
pip install flake8 black isort

# Format code
black .
isort .

# Lint code
flake8 .
```

### Database Management
```
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (development only)
python manage.py flush
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation for API changes
- Ensure mobile responsiveness for UI changes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django and Django Channels communities
- Bootstrap team for the excellent CSS framework
- Render.com for providing excellent deployment platform

## 📞 Support

For support and questions:
- 📧 Email: support@collabforms.com
- 🐛 Issues: [GitHub Issues](https://github.com/Ebullioscopic/Forms/issues)
- 📚 Documentation: [Wiki](https://github.com/Ebullioscopic/Forms/wiki)

---

**Built with ❤️ using Django Channels for real-time collaboration**
