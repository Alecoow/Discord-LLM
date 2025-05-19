class ConversationBuilder:
    def __init__(self, model="qwen3-0.6b", stream=False):
        self.history = []
        self.model = model
        self.stream = stream

    def append_message(self, message, role="user"):
        self.history.append({
            "role": role,
            "content": message
        })

    def set_system_message(self, message):
        self.append_message(message, "system")

    def build_payload(self):
        return {
        "stream": self.stream,
        "model": self.model,
        "messages": self.history

    }

    def delete_history(self):
        self.history = []