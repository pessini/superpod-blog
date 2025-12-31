import asyncio

import chainlit as cl

from modules.agno import AgnoClient, AgnoClientError
from modules.ollama import get_available_models, get_ollama_generator

# Initialize AgnoService
agno_service = AgnoClient()


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

    # Add Agno entities
    try:
        agno_entities = await agno_service.get_available_entities()
        for entity in agno_entities.values():
            profiles.append(
                cl.ChatProfile(
                    name=entity.profile_key,
                    display_name=entity.name,
                    markdown_description=f"**{entity.type.title()}**: {entity.description}",
                    icon="/public/agno-avatar.png",
                )
            )
    except AgnoClientError as e:
        print(f"Failed to load Agno entities: {e}")

    return profiles or [cl.ChatProfile(name="default", markdown_description="Default model")]


@cl.on_chat_start
async def on_chat_start():
    profile = cl.user_session.get("chat_profile")

    # Check if selected profile is an Agno entity
    if profile and (profile.startswith("agent:") or profile.startswith("workflow:") or profile.startswith("team:")):
        entity_type, entity_id = profile.split(":", 1)
        # Store ID for API usage
        cl.user_session.set("agno_entity_id", entity_id)
        cl.user_session.set("agno_entity_type", entity_type)

        # Create Agno session
        user = cl.user_session.get("user")
        user_id = user.identifier if user else "anonymous"

        try:
            session_id = await agno_service.create_session(
                user_id=user_id, entity_id=entity_id, entity_type=entity_type
            )
            cl.user_session.set("agno_session_id", session_id)

            # await cl.Message(
            #     content=f"Connected to **{entity_type.title()}** (`{entity_id}`).\nSession ID: `{session_id}`"
            # ).send()

        except AgnoClientError as e:
            await cl.Message(content=f"❌ Failed to create session for **{entity_id}**.\nError: {str(e)}").send()
            cl.user_session.set("agno_session_id", None)

    else:
        # Ollama model identifier, so we can use it directly.
        model_name = profile or "llama3.2:latest"
        cl.user_session.set("model_name", model_name)

    cl.user_session.set("messages", [])


@cl.on_message
async def on_message(message: cl.Message):
    agno_session_id = cl.user_session.get("agno_session_id")

    msg = cl.Message(content="")

    if agno_session_id:
        # Handle Agno Message
        entity_id = cl.user_session.get("agno_entity_id")
        entity_type = cl.user_session.get("agno_entity_type")
        user = cl.user_session.get("user")
        user_data = {"user_id": user.identifier} if user else None

        try:
            async for chunk in agno_service.send_message(
                session_id=agno_session_id,
                message=message.content,
                entity_id=entity_id,
                entity_type=entity_type,
                user_data=user_data,
            ):
                await msg.stream_token(chunk)
            await msg.send()
        except AgnoClientError as e:
            await msg.stream_token(f"\n\n❌ Error communicating with AgentOS: {str(e)}")
            await msg.send()
        return

    # If we are in an Agno chat profile but failed to create a session, warn the user
    agno_entity_id = cl.user_session.get("agno_entity_id")
    if agno_entity_id and not agno_session_id:
        await cl.Message(content=f"❌ No active session for **{agno_entity_id}**. Please restart the chat.").send()
        return

    # Existing Ollama Logic
    model_name = cl.user_session.get("model_name")
    messages = cl.user_session.get("messages")

    # Add user message to history
    messages.append({"role": "user", "content": message.content})
    response_content = ""

    # Stream from Ollama while also recording a Langfuse generation
    # with the current user input and final assistant output.
    async for chunk in get_ollama_generator(model_name, messages, user_input=message.content):
        await msg.stream_token(chunk)
        response_content += chunk

    await msg.send()

    # Add assistant response to history
    messages.append({"role": "assistant", "content": response_content})
    cl.user_session.set("messages", messages)


if __name__ == "__main__":
    asyncio(on_message())
