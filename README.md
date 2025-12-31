
<div align="center">
  <img alt="Superpod logo" src="assets/logo-celadon.svg" style="max-width: 300px; width: 80%;">
  <h3>Collective intelligence for autonomous AI agents.</h3>
</div>

<hr />

**Superpod** orchestrates a [Chainlit](https://github.com/Chainlit/chainlit) frontend (backed by Postgres and MinIO) with an [Agno OS](https://github.com/agno-agi/agent-infra-docker) backend, providing the execution layer for multi-agent coordination and intelligence.

> _This repository is the codebase for the article: [Building a Modern, Local-First AI Engineering Stack - Designing a private, multi-agent execution layer with Chainlit, Agno, and Langfuse](#) (link coming soon)._

---

## Tech Stack

- **Frontend:** [Chainlit](https://www.chainlit.io/)
- **Backend:** [Agno OS](https://www.agno.com/)
- **LLM Engineering Platform**: [Langfuse](https://langfuse.com/)
- **Database:** PostgreSQL
- **Object Storage:** MinIO (S3-compatible)
- **Dependency Management:** [uv](https://github.com/astral-sh/uv)
- **Containerization:** Docker
- **Vector Database:** [Qdrant](https://qdrant.tech/documentation/quickstart/) (shipped together but not integrated)

![Architecture](/assets/blog/architecture.png)

---

## Project Setup & Usage

### How to Run the Project

Pre-requisites:
- [Docker](https://docs.docker.com/desktop/)
- [uv](https://github.com/astral-sh/uv)
- [Ollama](https://docs.ollama.com/) (you could also change to use docker)

> [!NOTE]
> After **Ollama** is installed, pull models *llama3.2:latest*, *qwen3:latest* and *nomic-embed-text:v1.5*

```bash
ollama pull llama3.2:latest && ollama pull qwen3:latest && ollama pull nomic-embed-text:v1.5
```

### Install dependencies
Install all dependencies for both frontend and backend:
```bash
make venv
source .venv/bin/activate  # Activate the virtual environment
make env
make init-backend
make init-frontend
```

## Services

**Agno AgentOS**: create your free account at https://os.agno.com and connect your local agents - http://localhost:13300 (image below)

![alt text](/assets/blog/agent-os-config.png)

**Langfuse**: http://localhost:13303

No need to setup Langfuse thanks to [Headless Initialization](https://langfuse.com/self-hosting/administration/headless-initialization).

**Chainlit**: http://localhost:13201

---

## Pro Tips
- Run `uv sync` from root to update all projects at once.
- All projects share a single `.venv` at the root.
- If using Docker, each service (frontend/backend) has its own Dockerfile pointing to its respective `pyproject.toml`.

---

## License

This project is open-source and available under the [MIT License](LICENSE).