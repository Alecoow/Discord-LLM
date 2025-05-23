import discord
import os
from dotenv import load_dotenv
import requests
import json
import asyncio

import conversation_builder
convo = conversation_builder.ConversationBuilder()

# Discord
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

load_dotenv()

response_lock = asyncio.Lock()

# LLM API
LLM_ENDPOINT = os.environ.get('LLM_ENDPOINT')
# Discord API key
api_key = os.environ.get('BOT_API_KEY')

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    print("\nReady and waiting!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    elif message.content.startswith("$msg"):
        if response_lock.locked():
            await message.channel.send("Server busy! Please wait")
            return
        async with response_lock:
            # we don't need to send $msg to the LLM
            msg = message.content.lstrip("$msg")
            convo.append_message(msg)
            payload = convo.build_payload()
            await message.channel.send("Generating...")
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, message_llm, payload)
            convo.append_message(response, "assistant")
            await message.channel.send(response)
    elif message.content.startswith("$clear"):
        convo.delete_history()
        await message.channel.send("Memory cleared")
        
def query_models():
    try:
        response = requests.get(f"{LLM_ENDPOINT}/models")
        response.raise_for_status()
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def message_llm(message):
    try:
        response = requests.post(
            url=f'{LLM_ENDPOINT}/chat/completions',
            json=message
        )
        response.raise_for_status()

        # parse response to trim out unneccessary information + limit response to 2000 characters to comply with discord limits
        json_response = response.json()
        parsed_response = json_response["choices"][0]["message"]["content"]
        parsed_response = (parsed_response[:1976] + "\n\n [RESPONSE TRUNCATED]") if len(parsed_response) > 1976 else parsed_response
        return parsed_response
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        if response is not None:
            print("Response content:", response.text)
        return None

client.run(f'{api_key}')
