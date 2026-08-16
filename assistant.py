"""
Core Voice Assistant orchestrator. Coordinates speech, intent processing, and services.
"""

import sys
import logging
from typing import Optional

try:
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from modules.speech import SpeechEngine
from modules.commands import CommandProcessor, IntentClassifier
from modules.weather import WeatherService
from modules.email import EmailService
from modules.reminder import ReminderManager
from modules.knowledge import KnowledgeService

logger = logging.getLogger(__name__)


class VoiceAssistant:
    """Main Voice Assistant coordinator."""

    def __init__(self, config_path: str = "config.json", text_only: bool = False):
        self.cmd_processor = CommandProcessor(config_path)
        self.config = self.cmd_processor.config
        self.assistant_name = self.config.get("assistant_name", "Nova")
        self.text_only = text_only

        # Initialize speech engine
        tts_rate = self.config.get("tts_rate", 175)
        tts_volume = self.config.get("tts_volume", 1.0)
        self.speech = SpeechEngine(rate=tts_rate, volume=tts_volume)
        if self.text_only:
            self.speech.mic_available = False

        # Initialize services
        self.weather_service = WeatherService()
        self.email_service = EmailService()
        self.knowledge_service = KnowledgeService()
        self.reminder_manager = ReminderManager(alert_callback=self._reminder_callback)

        self.running = False

    def _reminder_callback(self, alert_message: str) -> None:
        """Invoked when a background reminder is triggered."""
        self.speech.speak(alert_message)

    def greet_user(self) -> None:
        """Speak opening greeting."""
        greeting = f"Hello! I am {self.assistant_name}, your personal voice assistant. How can I help you today?"
        self.speech.speak(greeting)

    def handle_email_flow(self, initial_recipient: Optional[str] = None) -> None:
        """Interactive multi-turn flow to compose and send an email via voice or text."""
        recipient = initial_recipient
        if not recipient:
            self.speech.speak("Who is the recipient? Please provide the email address.")
            recipient = self.speech.listen()
            if not recipient or recipient.lower() in ["cancel", "exit", "stop"]:
                self.speech.speak("Email cancelled.")
                return

        recipient = EmailService.clean_spoken_email(recipient)
        if not EmailService.validate_email(recipient):
            self.speech.speak(f"'{recipient}' is not a valid email format. Email cancelled.")
            return

        self.speech.speak("What is the subject of the email?")
        subject = self.speech.listen()
        if not subject or subject.lower() in ["cancel", "exit", "stop"]:
            self.speech.speak("Email cancelled.")
            return

        self.speech.speak("What should the message say?")
        message = self.speech.listen()
        if not message or message.lower() in ["cancel", "exit", "stop"]:
            self.speech.speak("Email cancelled.")
            return

        self.speech.speak(f"Sending email to {recipient}...")
        success, response_msg = self.email_service.send_email(recipient, subject, message)
        self.speech.speak(response_msg)

    def process_command(self, user_text: str) -> bool:
        """
        Process user input string and execute corresponding action.
        Returns: True to continue running, False to terminate.
        """
        if not user_text:
            return True

        intent, entities = self.cmd_processor.classifier.classify(user_text)
        logger.info(f"Classified Intent: {intent}, Entities: {entities}")

        if intent == IntentClassifier.INTENT_EXIT:
            self.speech.speak(f"Goodbye! Have a wonderful day.")
            return False

        elif intent == IntentClassifier.INTENT_GREETING:
            self.speech.speak(f"Hello! How can I assist you?")

        elif intent == IntentClassifier.INTENT_TIME:
            response = self.cmd_processor.get_time()
            self.speech.speak(response)

        elif intent == IntentClassifier.INTENT_DATE:
            response = self.cmd_processor.get_date()
            self.speech.speak(response)

        elif intent == IntentClassifier.INTENT_SEARCH:
            query = entities.get("query", "")
            response = self.cmd_processor.execute_search(query)
            self.speech.speak(response)

        elif intent == IntentClassifier.INTENT_WEATHER:
            city = entities.get("city") or self.config.get("default_city", "New York")
            self.speech.speak(f"Fetching weather information for {city}...")
            response = self.weather_service.get_weather(city)
            self.speech.speak(response)

        elif intent == IntentClassifier.INTENT_EMAIL:
            self.handle_email_flow(initial_recipient=entities.get("recipient"))

        elif intent == IntentClassifier.INTENT_REMINDER:
            raw_text = entities.get("raw_text", user_text)
            note = entities.get("note")
            response = self.reminder_manager.set_reminder(raw_text, custom_message=note)
            self.speech.speak(response)

        elif intent == IntentClassifier.INTENT_CUSTOM:
            action = entities.get("action", "")
            trigger = entities.get("trigger", "")
            response = self.cmd_processor.execute_custom_command(action, trigger)
            self.speech.speak(response)

        elif intent == IntentClassifier.INTENT_KNOWLEDGE:
            query = entities.get("query", user_text)
            response = self.knowledge_service.answer_question(query)
            self.speech.speak(response)

        elif intent == IntentClassifier.INTENT_HELP:
            response = self.cmd_processor.get_help()
            self.speech.speak(response)

        else:
            # Try knowledge service first before fallback error
            ans = self.knowledge_service.answer_question(user_text)
            if ans and not ans.startswith("I don't have an answer"):
                self.speech.speak(ans)
            else:
                self.speech.speak(
                    "Sorry, I didn't understand that command. You can ask for help to see what I can do."
                )

        return True

    def run(self) -> None:
        """Start the main assistant interaction loop."""
        self.running = True
        self.greet_user()

        try:
            while self.running:
                user_input = self.speech.listen()
                if user_input is None:
                    continue

                should_continue = self.process_command(user_input)
                if not should_continue:
                    self.running = False
        except KeyboardInterrupt:
            self.speech.speak("Shutting down. Goodbye!")
            self.running = False
