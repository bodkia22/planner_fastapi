 # 🗓️ Weekly Planner — AI-Powered Task Manager (Backend)

> A full-stack task manager with an **AI agent** that manages your tasks through natural language.
> Tell it *"add a dentist appointment next Tuesday and a task to call mom tomorrow"* — the agent decides which actions to run, creates the tasks, and replies.

<p align="left">
  <a href="https://weekly-planner-bb.vercel.app/"><img src="https://img.shields.io/badge/Live_Demo-Try_it-22c55e?style=for-the-badge" alt="Live Demo"></a>
  <a href="https://github.com/bodkia22/planner_react"><img src="https://img.shields.io/badge/Frontend_Repo-React_+_TS-3178c6?style=for-the-badge" alt="Frontend Repo"></a>
</p>

**🔗 Live demo:** https://weekly-planner-bb.vercel.app/
**🧪 Test account:** `admin@gmail.com` / `test_admin`

> ℹ️ The backend runs on Railway — the first request after a period of inactivity may take a few seconds to wake up.

## 🎬 Demo

Tell the assistant in plain language — it figures out the dates, priorities and where each task belongs:

![AI assistant parsing a natural-language request into structured tasks](https://github.com/user-attachments/assets/319cb91b-eaa1-4061-afd5-ab163a7e7290)

Dated tasks land on the right days with the correct priority:

![Weekend tasks created on the board](https://github.com/user-attachments/assets/1a5cd078-6a17-4195-8f41-6fbaaad0feac)

…and tasks without a date go to a separate To-Do list:

![Undated task in the To-Do column](https://github.com/user-attachments/assets/694384a1-5998-4a62-a6ef-ee4c7fd4230c)

---

## ✨ Features

- 🤖 **AI assistant** — manage tasks with natural language, powered by Claude with **tool use**
- 🔐 **JWT authentication** stored in **httpOnly cookies** (not localStorage — protected against XSS token theft)
- ✅ **Task CRUD** with priorities, due dates, and "done" status
- 💬 **Persistent conversations** — chat history stored in the DB, so the assistant has context across messages
- 🗄️ **PostgreSQL + Alembic migrations**
- 🐳 **Dockerized** — one command to run the whole stack locally
- 🧪 **Tested with Pytest** (isolated SQLite test DB, auth fixtures)

---

## 🤖 How the AI assistant works

This is not a single "parse text → JSON" call. It's a proper **agentic tool-use loop**:

1. The user message + full conversation history is sent to Claude along with a set of **tool definitions** (`get_user_tasks`, `create_task`, `update_task`, `delete_task`).
2. The model decides **which tools to call and with what arguments** — it can chain multiple actions in one turn (e.g. read existing tasks, then update the right one by ID).
3. The backend **executes the real functions** against the database, returns the results to the model, and the loop continues until the model finishes its turn.
4. Relative dates ("tomorrow", "next Monday") are resolved by injecting the current date into the system prompt.

```
User message
    │
    ▼
┌─────────────────────────────────────────┐
│  Claude (system prompt + tools + history)│◄──────┐
└─────────────────────────────────────────┘       │
    │  stop_reason = "tool_use"?                    │
    ▼                                               │
┌──────────────┐   real DB operations   ┌───────────────┐
│ tool executor│ ─────────────────────► │  Tasks service │
└──────────────┘   tool_result back ───►└───────────────┘
    │  stop_reason = "end_turn" → return reply to user
    ▼
Response
```

> 🔒 **Security note:** the Anthropic API key lives **only on the backend**, never exposed to the frontend.

---

## 🛠️ Tech Stack

| Layer        | Tech                                                        |
|--------------|-------------------------------------------------------------|
| **API**      | FastAPI, Pydantic v2 (`pydantic-settings` for typed config) |
| **Database** | PostgreSQL, SQLAlchemy, Alembic (migrations)                |
| **Auth**     | JWT (`python-jose`), bcrypt (`passlib`), httpOnly cookies   |
| **AI**       | Anthropic SDK (Claude), tool use / function calling         |
| **DevOps**   | Docker, docker-compose, deployed on Railway                 |
| **Tests**    | Pytest, FastAPI `TestClient`                                |

**Frontend** (React + TypeScript + Vite + Tailwind + TanStack Query): https://github.com/bodkia22/planner_react

---

## 🚀 Quick Start (local)

### Option A — Docker (recommended)

```bash
git clone https://github.com/bodkia22/planner_fastapi.git
cd planner_fastapi

# create .env (see below), then:
docker-compose up --build
```

API will be available at `http://localhost:8000`, interactive docs at `http://localhost:8000/docs`.

### Option B — without Docker

```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# make sure PostgreSQL is running and .env is configured
alembic upgrade head
uvicorn main:app --reload
```

### Environment variables (`.env`)

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/todo_db
SECRET_KEY=your-secret-key
ANTHROPIC_API_KEY=sk-ant-...
CORS_ORIGINS=["http://localhost:5173"]
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
```

> In production (`COOKIE_SECURE=true`, `COOKIE_SAMESITE=none`) cookies are sent only over HTTPS, which is what enables the Vercel frontend to talk to the Railway backend across domains.

---

## 🧪 Running Tests

```bash
pytest
```

Tests run against an isolated SQLite database with fixtures for authenticated requests, so they don't touch your real DB.

---

## 📡 API Overview

| Method | Endpoint            | Description                          | Auth |
|--------|---------------------|--------------------------------------|------|
| POST   | `/auth/register`    | Register a new user                  | ❌   |
| POST   | `/auth/login`       | Login, sets httpOnly cookie          | ❌   |
| POST   | `/auth/logout`      | Clear auth cookie                    | ❌   |
| GET    | `/auth/me`          | Current user info                    | ✅   |
| GET    | `/tasks`            | List user's tasks                    | ✅   |
| POST   | `/tasks`            | Create a task                        | ✅   |
| PUT    | `/tasks/{id}`       | Update a task                        | ✅   |
| DELETE | `/tasks/{id}`       | Delete a task                        | ✅   |
| POST   | `/chat`             | Talk to the AI assistant             | ✅   |

Full interactive documentation (Swagger) is auto-generated at `/docs`.

---

## 📁 Project Structure

```
.
├── main.py              # FastAPI app + CORS + routers
├── config.py            # typed settings (pydantic-settings)
├── database.py          # SQLAlchemy session / Base
├── routers/             # auth, tasks, assistant, conversation
├── services/            # business logic (tasks)
├── tools/               # AI tool definitions + executor
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── utils/jwt.py         # JWT create / verify / current_user dependency
├── alembic/             # DB migrations
├── tests/               # pytest
├── Dockerfile
└── docker-compose.yml
```
