# Cold Chain Monitoring System

This document explains how to run every layer (backend, frontend, IoT) and how the clean architecture pieces interact.

## Architecture Overview

- **Domain layer** (`monitoring/models.py`, `monitoring/services.py`): holds entities, business rules, alert evaluation logic, audit helper.
- **Application layer** (`monitoring/views.py`, `monitoring/serializers.py`, `monitoring/permissions.py`): orchestrates REST I/O, validation, auth.
- **Infrastructure layer** (`monitoring/notifications.py`, management commands, docker): integrates SMTP, Telegram, WhatsApp, exports, deployment.
- **Presentation layer** (`frontend/`): React dashboard + CRUD.
- **Edge layer** (`iot/esp8266_dht11.ino`): sensor firmware pushing data every 20 minutes.

## Environment Variables

Copy `env.example` to `.env` (root) and set:

```
DJANGO_SECRET_KEY=...
POSTGRES_USER=...
POSTGRES_PASSWORD=...
FRONTEND_URL=http://localhost:5173
TELEGRAM_BOT_TOKEN=...
WHATSAPP_TOKEN=...
```

The backend automatically loads `backend/.env` (symlink or copy the same file there).

## Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

Useful scripts:

- `python manage.py export_measurements_csv --output exports/measurements.csv`
- `python manage.py export_measurements_pdf --output exports/measurements.pdf`

### Docker

```bash
docker compose up --build
```

Services:

- `db` – PostgreSQL 14
- `api` – Django + Gunicorn (`backend/Dockerfile`)
- `web` – React build served by NGINX (`frontend/Dockerfile`)

## Frontend

```bash
cd frontend
npm install
VITE_API_URL=http://localhost:8000/api npm run dev
```

Build for production: `npm run build`.

## IoT Firmware

1. Open `iot/esp8266_dht11.ino` in Arduino IDE.
2. Install the `ESP8266` board package, `DHT sensor library`, and `ArduinoJson`.
3. Update `WIFI_SSID`, `WIFI_PASSWORD`, `API_URL`, `SENSOR_TOKEN`.
4. Flash to NodeMCU / Wemos D1 mini.

The device:

- Reconnects WiFi if needed.
- Reads DHT11 temperature/humidity.
- Posts JSON `{sensor_token, temperature, humidity, recorded_at}` to `/api/ingest/`.
- Retries every second if WiFi drops, publishes data every 20 minutes.

## JWT Authentication Flow

1. Frontend login calls `POST /api/token/`.
2. Access token stored in `localStorage`, injected via Axios interceptor.
3. All API calls require `Authorization: Bearer <token>`.

## Alerting Rules

- Default cold chain guard: 2–8 °C (sensor thresholds).
- Custom rules (`alert_rules` endpoint) per sensor or global.
- Each measurement triggers `store_measurement` → evaluation:
  - Creates `Alert`, `Ticket` when outside limits.
  - Sends notifications (SMTP, Telegram Bot API, WhatsApp Cloud API).
  - Writes audit entries for every action.

## CSV / PDF Export

- Backend management commands produce official reports.
- Frontend includes quick CSV/PDF utilities for ad-hoc exports.

## Testing Checklist

- `python manage.py test`
- `npm run lint`
- Manual steps:
  - Create sensor + rule.
  - Use `curl`/Postman to hit `/api/ingest/` and confirm alerts + tickets.
  - Verify login + dashboard widgets.

