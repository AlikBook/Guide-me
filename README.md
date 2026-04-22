# Master Camp Project

This project is a full-stack application focused on the Paris Metro:

- Frontend: Vue 3 + Vite
- Backend: FastAPI

## Important Note About Local Backend Execution

At the moment, you cannot fully run the backend locally from a clean setup unless you have access to the private `V2_text_files` dataset.

Why:

- The backend builds/loads the transport database from these GTFS text files.
- These files are currently not publicly available.
- They are required to generate the SQLite database used by the API.

Required folder (not included in this repository for external users):

```bash
fastapi-backend/app/V2_text_files
```

## Project Requirements

### General

- Git
- Node.js 18+ and npm
- Python 3.11+

### Backend-specific

- `pip` (Python package manager)
- C compiler toolchain for Cython extensions
  - On Windows: Microsoft C++ Build Tools
- Docker Desktop (optional, for containerized backend)

## Repository Structure

```text
Master_camp_project/
	fastapi-backend/
	front_end/
```

## Frontend Setup and Launch

From the project root:

```bash
cd front_end
npm install
npm run dev
```

The frontend dev server runs with Vite (usually on `http://localhost:5173`).

## Connect Frontend to Backend

You must set the backend URL used by the frontend.

The frontend reads the API base URL from:

- `VITE_API_BASE_URL` (environment variable)

It is used in `front_end/src/config/api.js`.
If not set, the frontend falls back to:

- `http://127.0.0.1:8000`

Create a local frontend env file:

```bash
front_end/.env.local
```

With this content:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

If your backend runs on another host/port (for example Docker, VM, or remote server), set this URL accordingly.

## Backend Setup and Launch (Local Python)

From the project root:

```bash
cd fastapi-backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Default API URL:

```text
http://localhost:8000
```

Environment example (`fastapi-backend/.env`):

```dotenv
GUIDE_ME_HOST_PORT=8000
GUIDE_ME_CONTAINER_PORT=8000
APP_ENV=production
DATABASE_PATH=/app/database/transport_data.db
```

Note:

- Startup loads transport data and may compile the Yen C extension.
- Without the required `V2_text_files`, the backend cannot build/load data correctly.

## Backend with Docker

From the project root:

```bash
cd fastapi-backend
docker compose up --build
```

Run in detached mode:

```bash
docker compose up -d --build
```

Stop containers:

```bash
docker compose down
```

Notes:

- API is exposed on `http://localhost:8000` (based on `.env` ports).
- `fastapi-backend/database` is mounted as a volume to persist the SQLite database.
- Docker does not remove the requirement for `V2_text_files` when database generation is needed.

## Suggested Local Workflow

1. Run the frontend immediately (`front_end`) for UI development.
2. Run the backend only if you have the required private GTFS files in `fastapi-backend/app/V2_text_files`.
3. If backend data files are unavailable, use mock responses or a previously generated database for frontend testing.
