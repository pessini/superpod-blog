import asyncio

import chainlit as cl

from modules.ollama import OLLAMA_MODELS, get_available_models, get_ollama_generator


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.User(identifier="admin", metadata={"role": "admin", "provider": "credentials"})
    else:
        return None


@cl.set_chat_profiles
async def chat_profile():
    models = get_available_models(show_all_installed=False)
    profiles = [
        cl.ChatProfile(
            name=model_id,
            display_name=pretty_name,
            markdown_description=f"Model: **{model_id}**",
            icon="/public/ollama.webp",
        )
        for pretty_name, model_id in models.items()
    ]
    return profiles or [cl.ChatProfile(name="default", markdown_description="Default model")]


@cl.on_chat_start
async def on_chat_start():
    profile = cl.user_session.get("chat_profile")
    model = OLLAMA_MODELS.get(profile, profile)

    if not model or model == "default":
        model = "llama3.2:latest"

    cl.user_session.set("model_name", model)
    cl.user_session.set("messages", [])


@cl.on_message
async def on_message(message: cl.Message):
    model_name = cl.user_session.get("model_name")
    messages = cl.user_session.get("messages")

    # Add user message to history
    messages.append({"role": "user", "content": message.content})

    msg = cl.Message(content="")
    response_content = ""

    async for chunk in get_ollama_generator(model_name, messages):
        await msg.stream_token(chunk)
        response_content += chunk

    await msg.send()

    # Add assistant response to history
    messages.append({"role": "assistant", "content": response_content})
    cl.user_session.set("messages", messages)


if __name__ == "__main__":
    asyncio(on_message())
