from __future__ import annotations
import asyncio
import json
import discord

from settings import DISCORD_MAX, THINK_MARKER, BOT_API_KEY
from llm_client import LLMClient
from utils import sanitize_messages, strip_think, truncate_response
from conversation_builder import ConversationBuilder
from settings import LLM_ENDPOINT, LLM_MODEL

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

response_lock = asyncio.Lock()
convo = ConversationBuilder()
llm = LLMClient()

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    print("Ready and waiting!")
    convo.set_system_message("You are a helpful, concise assistant. Prefer clear, direct answers.")
    await llm.start()

    # Decide status text based on endpoint + model
    status_text = "Running "
    if "127.0.0.1" in LLM_ENDPOINT or "localhost" in LLM_ENDPOINT:
        status_text += "Private LLM (Local)"
    elif "openrouter.ai" in LLM_ENDPOINT:
        if LLM_MODEL:
            status_text += f"Public LLM ({LLM_MODEL})"
        else:
            status_text += "Public LLM"
    else:
        status_text = f"Custom API: {LLM_ENDPOINT}"

    await client.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name=status_text),
            status=discord.Status.online
    )

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if message.content.startswith("$clear"):
        convo.delete_history()
        await message.reply("Memory cleared", mention_author=False)
        return

    if not (client.user and client.user.mentioned_in(message) and not message.mention_everyone):
        return

    if response_lock.locked():
        await message.reply("Server busy! Please wait")
        return

    async with response_lock:
        raw = message.clean_content
        mention = f"@{client.user.name}" if client.user else ""
        user_text = raw.replace(mention, "").strip()

        convo.append_message(user_text)
        payload = convo.build_payload()
        payload["messages"] = sanitize_messages(payload.get("messages"))
        print(json.dumps(payload, indent=2))

        async with message.channel.typing():
            model_text = await llm.chat(payload)

        print(f"Raw LLM response: {model_text}")
        if not model_text:
            await message.channel.send("LLM request failed.")
            return

        final = truncate_response(strip_think(model_text, THINK_MARKER), DISCORD_MAX)
        convo.append_message(final, role="assistant")
        await message.channel.send(final)

# called when the bot disconnects
@client.event
async def on_disconnect():
    await llm.close()

# start the Discord bot
if __name__ == "__main__":
    client.run(BOT_API_KEY)