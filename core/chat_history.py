import json
import uuid
from datetime import datetime
from pathlib import Path


class ChatHistory:
    """
    Manages chat sessions — save, load, delete, rename.
    Each chat is stored as a JSON file in user_data/chats/.
    """

    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "user_data" / "chats"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._current_chat_id = None

    def new_chat(self):
        """Create a new empty chat and return its ID."""
        chat_id = str(uuid.uuid4())[:8]
        chat = {
            "id": chat_id,
            "title": "New Chat",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }
        self._save_chat(chat)
        self._current_chat_id = chat_id
        return chat_id

    def add_message(self, chat_id, role, content, **extra):
        """Add a message to a chat. role = 'user' or 'ai'."""
        chat = self.load_chat(chat_id)
        if not chat:
            return

        msg = {"role": role, "content": content}
        msg.update(extra)
        chat["messages"].append(msg)
        chat["updated_at"] = datetime.now().isoformat()

        # Auto-title from first user message
        if chat["title"] == "New Chat" and role == "user":
            chat["title"] = content[:50].strip()
            if len(content) > 50:
                chat["title"] += "..."

        self._save_chat(chat)

    def load_chat(self, chat_id):
        """Load a chat by ID."""
        path = self.data_dir / f"{chat_id}.json"
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def get_all_chats(self):
        """Get all chats, sorted by most recent first."""
        chats = []
        for path in self.data_dir.glob("*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    chats.append({
                        "id": data["id"],
                        "title": data["title"],
                        "updated_at": data.get("updated_at", ""),
                        "msg_count": len(data.get("messages", []))
                    })
            except Exception:
                continue

        chats.sort(key=lambda c: c["updated_at"], reverse=True)
        return chats

    def rename_chat(self, chat_id, new_title):
        """Rename a chat."""
        chat = self.load_chat(chat_id)
        if chat:
            chat["title"] = new_title
            self._save_chat(chat)

    def delete_chat(self, chat_id):
        """Delete a chat file."""
        path = self.data_dir / f"{chat_id}.json"
        if path.exists():
            path.unlink()

    def _save_chat(self, chat):
        path = self.data_dir / f"{chat['id']}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(chat, f, indent=2, ensure_ascii=False)

    @property
    def current_id(self):
        return self._current_chat_id

    @current_id.setter
    def current_id(self, val):
        self._current_chat_id = val
