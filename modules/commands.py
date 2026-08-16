"""
Commands Module: Intent parsing, entity extraction, and command execution.
"""

import re
import os
import json
import datetime
import webbrowser
import logging
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)


class IntentClassifier:
    """Classifies spoken natural language queries into distinct assistant intents."""

    # Intent Types
    INTENT_GREETING = "GREETING"
    INTENT_TIME = "TIME"
    INTENT_DATE = "DATE"
    INTENT_SEARCH = "SEARCH"
    INTENT_WEATHER = "WEATHER"
    INTENT_EMAIL = "EMAIL"
    INTENT_REMINDER = "REMINDER"
    INTENT_KNOWLEDGE = "KNOWLEDGE"
    INTENT_CUSTOM = "CUSTOM"
    INTENT_HELP = "HELP"
    INTENT_EXIT = "EXIT"
    INTENT_UNKNOWN = "UNKNOWN"

    def __init__(self, custom_commands: Optional[Dict[str, str]] = None):
        self.custom_commands = custom_commands or {}

    def classify(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Classify text and extract relevant entities.
        Returns: (intent_name, entities_dict)
        """
        if not text:
            return self.INTENT_UNKNOWN, {}

        text_lower = text.lower().strip()

        # 1. Exit Intent
        if any(re.search(rf"\b{w}\b", text_lower) for w in ["exit", "quit", "goodbye", "bye", "stop", "terminate"]):
            return self.INTENT_EXIT, {}

        # 2. Check Custom Commands (from config.json)
        for trigger_phrase, url_or_action in self.custom_commands.items():
            if trigger_phrase.lower() in text_lower:
                return self.INTENT_CUSTOM, {"action": url_or_action, "trigger": trigger_phrase}

        # 3. Help Intent
        if any(w in text_lower for w in ["what can you do", "help me", "show commands", "list commands", "help"]):
            return self.INTENT_HELP, {}

        # 4. Weather Intent (check before general knowledge/what is)
        if re.search(r"\b(?:weather|temperature|forecast|climate|how is it outside)\b", text_lower):
            city_match = re.search(r"\b(?:in|for|at|of)\s+([a-zA-Z\s]+?)(?:\s+today|\s+tomorrow|\s+now|[?.!]|\s*$)", text, re.IGNORECASE)
            city = city_match.group(1).strip() if city_match else None
            return self.INTENT_WEATHER, {"city": city}

        # 5. Greeting Intent
        greeting_patterns = [
            r"\b(hello|hi|hey|greetings|howdy|good\s+(?:morning|afternoon|evening))\b"
        ]
        if any(re.search(p, text_lower) for p in greeting_patterns) and not any(
            k in text_lower for k in ["weather", "time", "date", "search", "email", "remind", "who", "what"]
        ):
            return self.INTENT_GREETING, {}

        # 6. Time Intent
        if re.search(r"\b(time|what time|current time|clock|what's the time)\b", text_lower) and "date" not in text_lower:
            return self.INTENT_TIME, {}

        # 7. Date Intent
        if re.search(r"\b(date|today's date|current date|what day is it|day of the week)\b", text_lower):
            return self.INTENT_DATE, {}

        # 8. Reminder Intent
        if re.search(r"\b(remind|reminder|timer|alarm|set an alarm|set a reminder)\b", text_lower):
            # Extract note / message if present
            note_match = re.search(r"remind me\s+(?:to\s+(.+?)\s+after|to\s+(.+?)\s+in|after\s+\d+\s+\w+\s+to\s+(.+))", text, re.IGNORECASE)
            note = None
            if note_match:
                note = next((g for g in note_match.groups() if g), None)
            return self.INTENT_REMINDER, {"raw_text": text, "note": note}

        # 9. Email Intent
        if re.search(r"\b(send an email|send email|write an email|mail to|send a mail)\b", text_lower):
            # Extract quick recipient if spoken directly
            recipient_match = re.search(r"(?:to)\s+([\w\.\+-]+@[\w\.-]+\.\w+)", text, re.IGNORECASE)
            recipient = recipient_match.group(1) if recipient_match else None
            return self.INTENT_EMAIL, {"recipient": recipient}

        # 10. Web Search Intent
        search_match = re.search(r"^(?:search|google|search for|look up|search the web for)\s+(.+)", text, re.IGNORECASE)
        if search_match:
            query = search_match.group(1).strip()
            return self.INTENT_SEARCH, {"query": query}

        # 11. General Knowledge Intent
        knowledge_patterns = [
            r"^(?:who is|who was|who invented|who developed|who created|who wrote)\s+(.+)",
            r"^(?:what is|what are|what was|what were|explain|define)\s+(.+)",
            r"^(?:where is|where are|where was)\s+(.+)",
            r"^(?:tell me about)\s+(.+)"
        ]
        for p in knowledge_patterns:
            km = re.search(p, text_lower)
            if km:
                return self.INTENT_KNOWLEDGE, {"query": text}

        # Fallback to search if query contains "search" anywhere
        if "search" in text_lower:
            parts = text.split("search", 1)
            if len(parts) > 1:
                query = re.sub(r"^for\s+", "", parts[1].strip(), flags=re.IGNORECASE)
                if query:
                    return self.INTENT_SEARCH, {"query": query}

        return self.INTENT_UNKNOWN, {"query": text}


class CommandProcessor:
    """Executes actions based on classified intents."""

    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.classifier = IntentClassifier(self.config.get("custom_commands", {}))

    def _load_config(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config file {path}: {e}")
        return {
            "assistant_name": "Nova",
            "tts_rate": 175,
            "tts_volume": 1.0,
            "default_city": "New York",
            "custom_commands": {}
        }

    def get_time(self) -> str:
        """Return formatted current time."""
        now = datetime.datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}."

    def get_date(self) -> str:
        """Return formatted current date."""
        now = datetime.datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}."

    def execute_search(self, query: str) -> str:
        """Open web browser for google search query."""
        if not query or not query.strip():
            return "What would you like me to search for?"
        query = query.strip()
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Searching the web for '{query}'."

    def execute_custom_command(self, action: str, trigger: str) -> str:
        """Open configured web URL or trigger custom action."""
        if action.startswith("http://") or action.startswith("https://"):
            webbrowser.open(action)
            return f"Opening {trigger}."
        return f"Executing custom action for {trigger}."

    def get_help(self) -> str:
        """Return summary of voice assistant abilities."""
        return (
            "Here is what I can do: "
            "1. Greet you and tell the current date and time. "
            "2. Search the web by saying 'search Python tutorials'. "
            "3. Provide live weather reports by saying 'what is the weather in London'. "
            "4. Send voice-guided emails via SMTP. "
            "5. Set timed reminders like 'remind me after 5 minutes'. "
            "6. Answer general knowledge questions like 'who created Python'. "
            "7. Open custom websites like 'open github' or 'open youtube'. "
            "8. Exit when you say 'exit' or 'goodbye'."
        )
