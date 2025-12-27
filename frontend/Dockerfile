## ------------------------------- Builder Stage ------------------------------ ## 
FROM python:3.12-bookworm AS builder

# Download the latest installer, install it and then remove it
ADD https://github.com/astral-sh/uv/releases/latest/download/uv-installer.sh /install.sh
RUN chmod -R 655 /install.sh && /install.sh && rm /install.sh

# Set UV_HTTP_TIMEOUT for production
ENV UV_HTTP_TIMEOUT=600
# Set up the UV environment path correctly
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

COPY ./pyproject.toml .

RUN uv sync \
    && uv cache clean

## ------------------------------- Production Stage ------------------------------ ##
FROM python:3.12-slim-bookworm AS production

WORKDIR /app

COPY . .
COPY --from=builder /app/.venv .venv

# Set up environment variables for production
ENV PATH="/app/.venv/bin:$PATH"

# Expose the port the app runs on (default is 8000 for Chainlit)
EXPOSE 8000

# Start the application with Chainlit in production mode
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "-h"]