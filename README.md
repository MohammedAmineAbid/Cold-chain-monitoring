# Cold Chain Monitoring System

End-to-end cold chain stack covering hardware → backend → dashboard.

## Structure

```
backend/   Django REST API, PostgreSQL models, alerts, exports
frontend/  React + Recharts dashboard, authentication, exports
iot/       ESP8266 firmware (DHT11 → API ingest)
docs/      How-to guides
```

## Features

- Sensors, measurements, alert rules, tickets, audit logs, users.
- Automatic detection when temperature leaves 2–8 °C and configurable rules.
- Notifications via SMTP, Telegram Bot API, WhatsApp Cloud API.
- JWT auth, CORS, Swagger docs (`/api/docs`).
- CSV + PDF export scripts.
- Dockerized deployment (`docker-compose.yml`).
- React SPA with dashboard cards, charts, CRUD tables, CSV/PDF export helpers.
- ESP8266 firmware with WiFi retry + 20-minute reporting cadence.

## Quickstart

1. Copy `env.example` → `.env` (root + `backend/.env`).
2. `docker compose up --build` or run backend/frontend individually (see `docs/GETTING_STARTED.md`).
3. Create a Django superuser, login at `/login`, register sensors, pair sensor token with firmware.

See [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) for detailed instructions.

