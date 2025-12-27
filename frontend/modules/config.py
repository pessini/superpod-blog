import os


def is_docker():
    """Detect if running inside Docker container"""
    return os.path.exists("/.dockerenv") or os.environ.get("DOCKER_ENV") == "true"


def get_ollama_url():
    """Get Ollama URL based on environment"""
    if is_docker():
        return "http://host.docker.internal:11434"
    return "http://localhost:11434"


# Export configured value
OLLAMA_BASE_URL = get_ollama_url()
