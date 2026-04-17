# FermTrack

Track dough batches, fermentation stages, and prep workflow -- from mix to oven.

FermTrack is a multi-tenant kitchen system built for bakeries that want consistency without paper logs. It started around a pretzel and laugenbrezel workflow but is designed for any fermentation-heavy kitchen.

**Live demo:** [fermtrack.com/demo](https://fermtrack.com/demo)

## Quick Start

The fastest way to run everything locally:

```bash
./bootstrap.sh
```

This starts both the backend API (port 5000) and frontend server (port 8080). Open `http://localhost:8080` in your browser.

Default admin login: `admin` / `admin123`

### Manual Setup

If you prefer to start services individually:

```bash
# Backend
cd backend
./setup.sh
source ../.venv/bin/activate
python app.py

# Frontend (separate terminal)
cd frontend
./start.sh
```

## Project Structure

```
backend/          Flask REST API, JWT auth, SQLite
frontend/         Single-page app (vanilla HTML/CSS/JS)
demo/             Standalone local-storage demo
esp32-integration/ PlatformIO firmware for sensor hardware
index.html        Landing page (fermtrack.com root)
bootstrap.sh      Start both services
```

## Features

- **Multi-tenant bakeries** -- each bakery gets an isolated workspace with role-based access (baker, manager, admin)
- **Batch tracking** -- log batch ID, weight, dough type, time mixed, and status
- **Action logging** -- record fortify, re-ball, degas, wash, and other corrective actions
- **Global admin panel** -- manage users, bakeries, roles, and verification from one place
- **ESP32 sensor integration** -- connect CO2, temperature, and humidity sensors for real-time monitoring
- **CSV export** -- export filtered batch data
- **Self-hostable** -- runs on a single machine with SQLite, no external services required

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3, Flask 3.0, SQLAlchemy, Marshmallow |
| Auth | JWT (flask-jwt-extended), scrypt (werkzeug) |
| Database | SQLite (dev), PostgreSQL (prod) |
| Frontend | Vanilla HTML, CSS, JavaScript -- no framework |
| Sensors | ESP32, PlatformIO, Arduino libraries |
| Deploy | Docker, systemd services, Cloudflare |

## API

Backend docs: [backend/README.md](backend/README.md)

Key endpoints:

```
POST   /api/auth/login          Login, get JWT
POST   /api/auth/register       Create account
GET    /api/batches              List batches (filtered)
POST   /api/batches              Create batch
GET    /api/admin/users          Admin: list users
GET    /api/admin/bakeries       Admin: list bakeries
```

## Testing

```bash
cd backend
python test_api.py
```

## Docker

```bash
cd backend
docker-compose up -d
```

## License

FermTrack is free software licensed under the [GNU Affero General Public License v3.0](https://www.gnu.org/licenses/agpl-3.0.html).

- Free to use, modify, and redistribute
- Network copyleft: if you run FermTrack as a network service, you must provide source code access to users

Complete source code: **https://github.com/abelgraham/fermtrack**

All dependencies are AGPL-3.0 compatible (Flask, SQLAlchemy, etc. are MIT/BSD; Arduino libraries are LGPL/MIT). See [NOTICE](NOTICE) for details.
