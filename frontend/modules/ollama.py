import ollama
from ollama import AsyncClient

from .config import OLLAMA_BASE_URL
from .langfuse import langfuse

OLLAMA_MODELS = {
    "llama 3": "llama3.2:latest",
    "qwen 3": "qwen3:latest",
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


async def get_ollama_generator(model_name: str, messages: list, user_input: str | None = None):
    """Yields chunks from Ollama chat stream and records Langfuse trace.

    A Langfuse observation of type "generation" is created for each
    model call. The user's input (or full message list) is stored as
    the observation input, and the streamed model response is
    concatenated and stored as the observation output.
    """

    with langfuse.start_as_current_observation(as_type="generation", name=model_name) as generation:
        client = AsyncClient(host=OLLAMA_BASE_URL)

        # Record the input for this generation so it shows up in Langfuse.
        if user_input is not None:
            generation.update(input=user_input)
        else:
            generation.update(input=messages)

        full_output = ""

        async for part in await client.chat(model=model_name, messages=messages, stream=True):
            chunk = part["message"]["content"]
            full_output += chunk
            yield chunk

        # Store the full generated response as the output.
        generation.update(output=full_output)
