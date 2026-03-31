# FermTrack

A comprehensive fermentation tracking system for bakeries and kitchens. FermTrack helps you monitor dough batches, track fermentation stages, and maintain consistency in your baking workflow.

## 🏗️ Project Structure

- **[backend/](backend/)** - Python Flask API with JWT authentication and SQLite database
- **[frontend/](frontend/)** - Single-page web application for batch management  
- **[index.html](index.html)** - Original landing page
- **[demo/](demo/)** - Demo resources

## 🚀 Quick Start

### 1. Start the Backend API

```bash
cd backend
./setup.sh          # One-time setup
source venv/bin/activate
python app.py        # Start API server
```

Backend runs at `http://localhost:5000`

### 2. Start the Frontend

```bash
cd frontend  
./start.sh           # Start frontend server
```

Frontend runs at `http://localhost:8080`

### 3. Access the Application

- Open `http://localhost:8080` in your browser
- Login with default admin: `admin` / `admin123`
- Create batches and start tracking fermentation!

## 📋 Features

- **User Management**: Role-based authentication (baker, manager, admin)
- **Batch Tracking**: Create and monitor fermentation batches
- **Action Logging**: Record batch actions (fortify, re-ball, degas, wash, etc.)
- **Fermentation Stages**: Track timing and environmental conditions
- **Environmental Monitoring**: Temperature and humidity tracking
- **RESTful API**: Complete backend API for integration

## 📖 Documentation

- [Backend Documentation](backend/README.md) - API endpoints and setup
- [Frontend Documentation](frontend/README.md) - Web application usage  

## 🧪 Testing

Test the API functionality:
```bash
cd backend
python test_api.py
```

## 🐳 Docker Deployment

```bash
cd backend
docker-compose up -d
```

## 📄 License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
See the [LICENSE](LICENSE) file for details.

## 🔧 Tech Stack

- **Backend**: Python, Flask, SQLAlchemy, JWT, SQLite
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Authentication**: JWT tokens with role-based access
- **Database**: SQLite (development), PostgreSQL (production)
