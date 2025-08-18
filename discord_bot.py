from __future__ import annotations
import asyncio
import discord

from settings import DISCORD_MAX, THINK_MARKER, BOT_API_KEY
from llm_client import LLMClient
from utils import sanitize_messages, strip_think, truncate_response
from conversation_builder import ConversationBuilder

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

        await message.channel.send("Generating...")

        model_text = await llm.chat(payload)
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