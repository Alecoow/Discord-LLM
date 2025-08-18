import os
from dotenv import load_dotenv

load_dotenv()

# Helper class for managing LLM context history and crafting messages
class ConversationBuilder:
    def __init__(self, model: str | None = os.environ.get("LLM_MODEL"), stream: bool = False):
        self.history: list[dict[str, str]] = []
        self.model = model
        self.stream = stream

    # Add message to context history
    def append_message(self, message: str, role: str = "user") -> None:
        self.history.append({"role": role, "content": message})

    def set_system_message(self, message: str) -> None:
        # Ensure system goes first
        if self.history and self.history[0].get("role") == "system":
            self.history[0] = {"role": "system", "content": message}
        else:
            self.history.insert(0, {"role": "system", "content": message})

    def build_payload(self) -> dict:
        return {
            "stream": self.stream,
            "model": self.model,
            "messages": self.history,
        }

    def delete_history(self) -> None:
        # Keep system message if present
        if self.history and self.history[0].get("role") == "system":
            self.history = [self.history[0]]
        else:
            self.history = []