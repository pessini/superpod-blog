import ollama
from ollama import AsyncClient

from .config import OLLAMA_BASE_URL

OLLAMA_MODELS = {
    "llama 3": "llama3.2:latest",
    "qwen 3": "qwen3:latest",
    "deep seek r1": "deepseek-r1:latest",
}


def get_available_models(show_all_installed: bool = False) -> dict:
    """Returns a dictionary of available models from Ollama."""
    if not show_all_installed:
        return OLLAMA_MODELS

    try:
        models = getattr(ollama.list(), "models", [])
        rev = {v: k for k, v in OLLAMA_MODELS.items()}
        return {rev.get(m.model, m.model): m.model for m in models}
    except Exception as e:  # noqa: BLE001
        print(f"Error fetching models: {e}")
        return {}


async def get_ollama_generator(model_name: str, messages: list):
    """Yields chunks from Ollama chat stream."""
    client = AsyncClient(host=OLLAMA_BASE_URL)

    async for part in await client.chat(model=model_name, messages=messages, stream=True):
        yield part["message"]["content"]
