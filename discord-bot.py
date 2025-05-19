import discord
import os
from dotenv import load_dotenv
import requests
import json
import asyncio

import conversation
convo = conversation.ConversationBuilder()

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
    
    elif message.content.startswith('$msg'):
        if response_lock.locked():
            await message.channel.send("Server busy! Please wait")
            return
        async with response_lock:
            prefix = '$msg'
            msg = message.content.lstrip(prefix)
            convo.append_message(msg)
            payload = convo.build_payload()
            await message.channel.send("Generating...")
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, message_llm, payload)
            await message.channel.send(response)
        
def query_models():
    try:
        response = requests.get(f'{LLM_ENDPOINT}/models')
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
        json_response = response.json()
        parsed_response = json_response["choices"][0]["message"]["content"]
        parsed_response = (parsed_response[:1995] + '...') if len(parsed_response) > 1995 else json_response
        return parsed_response
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        if response is not None:
            print("Response content:", response.text)
        return None

client.run(f'{api_key}')

#convo.add_message("How many R's are in the word Strawberry?")
#message = convo.build_payload()
#print(message_llm(message))