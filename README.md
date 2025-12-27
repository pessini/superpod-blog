

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/logo.svg">
    <img alt="Superpod logo" src="assets/logo.svg">
  </picture>
  <h3>Collective intelligence for autonomous AI agents.</h3>
</div>

<hr />
**Superpod** is a platform for running [Chainlit](https://www.chainlit.io/) as the frontend (with a datalayer powered by Postgres and MinIO) and [Agno OS](https://github.com/your-org/agno-os) as the agent infrastructure. The frontend uses Postgres and MinIO for its data and object storage, while the Agno backend manages its own database and storage independently. Superpod serves as the execution layer for multi-agent coordination and intelligence.

> _This repository is the codebase for the article: [How to Build a Multi-Agent Platform with Chainlit and Agno OS](https://medium.com/your-article-link) (link coming soon)._

---

## Tech Stack

- **Frontend:** [Chainlit](https://www.chainlit.io/) (Python)
- **Backend:** Agno OS (FastAPI, Python)
- **Database:** PostgreSQL
- **Object Storage:** MinIO (S3-compatible)
- **Dependency Management:** [uv](https://github.com/astral-sh/uv)
- **Containerization:** Docker

---

# Project Setup & Usage
## How to Run the Project

### 1. Initialize the Workspace
Install all dependencies for both frontend and backend:
```bash
uv sync
```

### 2. Run the Chainlit Frontend
- **Option 1:**
  ```bash
  cd frontend
  uv run chainlit run app.py
  ```
- **Option 2:**
  ```bash
  uv run --package chainlit-app --directory frontend chainlit run app.py
  ```

### 3. Run the Agno Backend (FastAPI)
- **Option 1:**
  ```bash
  cd backend
  uv run fastapi dev app/api.py
  ```
- **Option 2:**
  ```bash
  uv run --package agents-os --directory backend fastapi dev app/api.py
  ```

### 4. Run Backend Tests
- **From backend folder:**
  ```bash
  cd backend
  uv run pytest
  ```
- **Or from root:**
  ```bash
  uv run --package agents-os --directory backend pytest
  ```

### 5. Type Checking (mypy)
```bash
cd backend
uv run mypy .
```

### 6. Linting (ruff)
- **Frontend:**
  ```bash
  cd frontend
  uv run ruff check .
  ```
- **Backend:**
  ```bash
  cd backend
  uv run ruff check .
  ```

### 7. Add New Dependencies
- **Frontend:**
  ```bash
  cd frontend
  uv add some-package
  ```
- **Backend:**
  ```bash
  cd backend
  uv add some-package
  ```
- **Backend (dev dependency):**
  ```bash
  cd backend
  uv add --dev some-dev-package
  ```

### 8. Typical Development Workflow
- **Terminal 1 (backend):**
  ```bash
  cd backend
  uv run fastapi dev app/api.py
  ```
- **Terminal 2 (frontend):**
  ```bash
  cd frontend
  uv run chainlit run app.py
  ```

---

## Pro Tips
- Run `uv sync` from root to update all projects at once.
- All projects share a single `.venv` at the root.
- If using Docker, each service (frontend/backend) has its own Dockerfile pointing to its respective `pyproject.toml`.

---

## License

This project is open-source and available under the [MIT License](LICENSE).

---

<p align="center">
  <em>Made with ❤️ by the Superpod community</em>
</p>
