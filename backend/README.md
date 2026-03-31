# FermTrack Backend

A Python Flask API backend for the FermTrack fermentation tracking application. This backend provides user authentication, batch management, and fermentation stage tracking for bakeries and kitchens.

## Features

- **User Authentication**: JWT-based authentication with role-based access control (baker, manager, admin)
- **Batch Management**: Create and track fermentation batches with detailed metadata
- **Action Logging**: Record specific actions performed on batches (fortify, re-ball, degas, wash, etc.)
- **Fermentation Stages**: Track different fermentation stages with timing and environmental conditions
- **Environmental Monitoring**: Record temperature and humidity data
- **RESTful API**: Clean API design for easy frontend integration

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication (`/api/auth`)

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info
- `GET /api/auth/users` - List all users (admin/manager)
- `PUT /api/auth/users/<id>/deactivate` - Deactivate user (admin)

### Batches (`/api/batches`)

- `POST /api/batches` - Create new batch
- `GET /api/batches` - List batches (with filtering)
- `GET /api/batches/<batch_id>` - Get specific batch
- `PUT /api/batches/<batch_id>` - Update batch
- `DELETE /api/batches/<batch_id>` - Delete batch (admin/manager)
- `POST /api/batches/<batch_id>/actions` - Add action to batch
- `POST /api/batches/<batch_id>/fermentation-stages` - Add fermentation stage
- `PUT /api/batches/<batch_id>/fermentation-stages/<stage_id>/complete` - Complete stage

### Utility

- `GET /api/health` - Health check
- `GET /api` - API information

## Data Models

### User
- Authentication and role management
- Roles: baker, manager, admin

### Batch
- Core fermentation batch tracking
- Includes recipe name, weight, status, environmental conditions
- Status options: mixing, bulk_ferment, divided, proofing, ready, baked, discarded

### Batch Action
- Log of actions performed on batches
- Action types: fortify, re-ball, degas, wash, divide, shape, other
- Tracks weight changes and environmental readings

### Fermentation Stage
- Tracks specific fermentation phases
- Stage types: autolyse, bulk_ferment, proof, final_proof, retard
- Includes timing targets and environmental targets

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. After logging in, include the token in the `Authorization` header:

```
Authorization: Bearer <your-jwt-token>
```

## Database

The backend uses SQLite by default for easy setup. The database file (`fermtrack.db`) will be created automatically when you first run the application.

For production, you can configure a different database by setting the `DATABASE_URL` environment variable.

## Default Admin User

On first startup, a default admin user is created:
- Username: `admin`
- Password: `admin123`

**Important**: Change this password immediately in production!

## Development

To run in development mode with auto-reload:

```bash
pip install flask
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

## Production Deployment

For production deployment:

1. Set `FLASK_ENV=production` in your `.env` file
2. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
3. Configure a reverse proxy (nginx, Apache)
4. Use a production database (PostgreSQL, MySQL)
5. Update secret keys and JWT secrets
6. Enable HTTPS

## API Usage Examples

### Register User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "baker1",
    "email": "baker@example.com",
    "password": "securepassword",
    "role": "baker"
  }'
```

### Create Batch
```bash
curl -X POST http://localhost:5000/api/batches \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "batch_id": "LB001",
    "recipe_name": "Laugenbrezeln",
    "dough_weight": 2500,
    "temperature": 22.5,
    "notes": "Standard pretzel dough batch"
  }'
```

### Add Batch Action
```bash
curl -X POST http://localhost:5000/api/batches/LB001/actions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "action_type": "fortify",
    "description": "Added extra flour for consistency",
    "weight_change": 50,
    "temperature_recorded": 23.0
  }'
```

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
See the LICENSE file for details.