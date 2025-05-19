import discord
import os
from dotenv import load_dotenv
import requests
import json

import conversation
convo = conversation.ConversationBuilder()

# Discord
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

load_dotenv()

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

    if message.content.startswith('$msg'):
        prefix = '$msg'
        msg = message.content.lstrip(prefix)
        convo.append_message(msg)
        payload = convo.build_payload()
        await message.channel.send(message_llm(payload))
        
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

        return json_response["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        if response is not None:
            print("Response content:", response.text)
        return None

client.run(f'{api_key}')

#convo.add_message("How many R's are in the word Strawberry?")
#message = convo.build_payload()
#print(message_llm(message))