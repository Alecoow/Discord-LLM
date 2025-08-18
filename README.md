Your friendly AI assistant for discord!

Currently supports basic text communication in text channels.

USAGE:
Once connected to a discord app/bot, you can interact with it by sending a message into a channel with the following commands:
- [ping] [message] - Ping the bot either with an @ or a reply. Sends a message to the LLM
- $clear - Clears chat history

INSTALLATION:
- This project is compatible with the OpenAI API standard, meaning you can theoretically connect any inference server to it that follows this standard, though It's only been tested with LM Studio.
- You will need to create environment variables on your system specifying the following:
  - BOT_API_KEY: Your discord "app" key
  - LLM_ENDPOINT: The endpoint to your inference server.
  - LLM_Model: The name of your LLM. Ex: Qwen3-0.6b
- This project uses Python 3.13.3
