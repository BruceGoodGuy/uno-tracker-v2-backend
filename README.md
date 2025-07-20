# Uno Tracker Backend API

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776ab)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791)](https://postgresql.org/)

> 🚧 **Currently in Development** - This API is actively being developed and is not yet ready for production use.

Backend API for the Uno Tracker application - A FastAPI-based REST API that handles user authentication, game management, and score tracking for Uno games.

## ✨ Features

- 🔐 **JWT Authentication** - Secure user authentication with access/refresh tokens
- 👤 **OAuth Integration** - Google OAuth support for easy sign-in
- 🎮 **Game Management** - Create, join, and manage Uno game sessions
- 📊 **Score Tracking** - Real-time score updates and game history
- 🗄️ **PostgreSQL Database** - Robust data persistence with SQLAlchemy ORM
- 🔄 **Database Migrations** - Alembic for database schema management
- 📝 **API Documentation** - Auto-generated OpenAPI/Swagger documentation
- 🌐 **CORS Support** - Configured for frontend integration
- ⚡ **High Performance** - Built with FastAPI for maximum speed

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or later
- PostgreSQL 13 or later
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/BruceGoodGuy/uno-tracker-v2-backend.git
cd uno-tracker-backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env  # Create environment file
# Edit .env with your configuration
```

Required environment variables:
```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/uno_tracker
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=uno_tracker

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Frontend
FRONTEND_URL=http://localhost:3000
```

5. Set up the database:
```bash
# Run database migrations
alembic upgrade head
```

6. Start the development server:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## 🛠️ Built With

- **[FastAPI 0.116.1](https://fastapi.tiangolo.com/)** - Modern, fast web framework for building APIs
- **[SQLAlchemy 2.0.41](https://sqlalchemy.org/)** - Python SQL toolkit and ORM
- **[PostgreSQL](https://postgresql.org/)** - Advanced open source database
- **[Alembic 1.16.4](https://alembic.sqlalchemy.org/)** - Database migration tool
- **[Pydantic 2.9.2](https://pydantic.dev/)** - Data validation using Python type hints
- **[python-jose](https://python-jose.readthedocs.io/)** - JWT implementation
- **[Passlib](https://passlib.readthedocs.io/)** - Password hashing library
- **[Uvicorn](https://uvicorn.org/)** - ASGI server implementation

## 📁 Project Structure

```
uno-tracker-backend/
├── alembic/                    # Database migrations
│   ├── versions/              # Migration files
│   └── env.py                 # Migration environment
├── src/
│   ├── auth/                  # Authentication module
│   │   ├── models.py         # User and OAuth models
│   │   ├── router.py         # Auth endpoints
│   │   ├── schemas.py        # Pydantic schemas
│   │   └── service.py        # Auth business logic
│   ├── core/                  # Core functionality
│   │   ├── config.py         # Configuration settings
│   │   ├── database.py       # Database connection
│   │   └── security.py       # Security utilities
│   ├── game/                  # Game management module
│   │   ├── models.py         # Game and score models
│   │   ├── router.py         # Game endpoints
│   │   ├── schemas.py        # Game schemas
│   │   └── service.py        # Game business logic
│   ├── dependencies.py        # Shared dependencies
│   └── main.py               # FastAPI application
├── alembic.ini               # Alembic configuration
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `GET /auth/google` - Google OAuth login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user info

### Games (Coming Soon)
- `POST /games` - Create a new game
- `GET /games` - List user's games
- `GET /games/{game_id}` - Get game details
- `POST /games/{game_id}/join` - Join a game
- `POST /games/{game_id}/scores` - Update game scores
- `DELETE /games/{game_id}` - Delete a game

## 📚 API Documentation

Once the server is running, you can access:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 🗄️ Database Schema

### Users Table
- `id` (UUID, Primary Key)
- `email` (String, Unique)
- `username` (String, Unique)
- `hashed_password` (String)
- `is_active` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Games Table (Coming Soon)
- `id` (UUID, Primary Key)
- `name` (String)
- `created_by` (UUID, Foreign Key)
- `status` (Enum: active, completed, paused)
- `created_at` (DateTime)
- `updated_at` (DateTime)

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest

# Run with coverage
pytest --cov=src
```

## 🚀 Deployment

### Using Docker (Recommended)

1. Build the image:
```bash
docker build -t uno-tracker-backend .
```

2. Run with docker-compose:
```bash
docker-compose up -d
```

### Manual Deployment

1. Set environment variables for production
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `alembic upgrade head`
4. Start with Gunicorn: `gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📋 Development Roadmap

- [x] JWT Authentication system
- [x] Google OAuth integration
- [x] Database models and migrations
- [ ] Complete game management endpoints
- [ ] Real-time score tracking
- [ ] User profile management
- [ ] Game statistics and analytics
- [ ] WebSocket support for live updates
- [ ] API rate limiting
- [ ] Comprehensive test suite
- [ ] Docker containerization
- [ ] CI/CD pipeline

## 🐛 Known Issues

- Game management endpoints are still under development
- WebSocket functionality not yet implemented
- Comprehensive error handling needs improvement

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**BruceGoodGuy**
- GitHub: [@BruceGoodGuy](https://github.com/BruceGoodGuy)
- Project Link: [https://github.com/BruceGoodGuy/uno-tracker-v2](https://github.com/BruceGoodGuy/uno-tracker-v2)

## 🙏 Acknowledgments

- Thanks to the FastAPI team for the excellent framework
- SQLAlchemy for the powerful ORM
- PostgreSQL for robust data storage
- All contributors and testers

---

⭐ Star this repository if you find it helpful!