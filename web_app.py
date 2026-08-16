"""
Flask Web Application for the Python Voice Assistant.
Exposes all assistant capabilities via a clean REST API.
"""

import os
import sys
import json
import logging
from datetime import datetime

try:
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from flask import Flask, request, jsonify, render_template, send_from_directory

try:
    from flask_cors import CORS
except ImportError:
    CORS = None

from modules.commands import CommandProcessor, IntentClassifier
from modules.weather import WeatherService
from modules.email import EmailService
from modules.reminder import ReminderManager
from modules.knowledge import KnowledgeService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ── Flask App Setup ────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder="templates", static_folder="static")
if CORS:
    CORS(app)

# ── Load config & initialize modules ──────────────────────────────────────────
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
cmd_processor = CommandProcessor(CONFIG_PATH)
config = cmd_processor.config
ASSISTANT_NAME = config.get("assistant_name", "Nova")

weather_service = WeatherService()
email_service = EmailService()
knowledge_service = KnowledgeService()

# Reminder callback posts alert text into a queue the frontend can poll
reminder_alerts = []

def reminder_callback(alert_text: str):
    reminder_alerts.append({"text": alert_text, "time": datetime.now().isoformat()})

reminder_manager = ReminderManager(alert_callback=reminder_callback)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", assistant_name=ASSISTANT_NAME)


@app.route("/api/status")
def status():
    return jsonify({"status": "ok", "assistant": ASSISTANT_NAME, "version": "2.0"})


@app.route("/api/command", methods=["POST"])
def command():
    """
    Main endpoint. Accepts { "text": "user command string" }.
    Returns { "response": "...", "intent": "...", "action": "..." }
    """
    data = request.get_json(silent=True) or {}
    user_text = (data.get("text") or "").strip()

    if not user_text:
        return jsonify({"response": "I didn't receive any command. Please try again.", "intent": "UNKNOWN"})

    intent, entities = cmd_processor.classifier.classify(user_text)
    logger.info(f"[WEB] Intent: {intent} | Text: '{user_text}'")

    response_text = ""
    extra = {}

    if intent == IntentClassifier.INTENT_EXIT:
        response_text = "Goodbye! Come back whenever you need help."

    elif intent == IntentClassifier.INTENT_GREETING:
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        response_text = f"{greeting}! I am {ASSISTANT_NAME}, your personal assistant. How can I help you today?"

    elif intent == IntentClassifier.INTENT_TIME:
        response_text = cmd_processor.get_time()

    elif intent == IntentClassifier.INTENT_DATE:
        response_text = cmd_processor.get_date()

    elif intent == IntentClassifier.INTENT_SEARCH:
        query = entities.get("query", "")
        if not query:
            response_text = "What would you like me to search for?"
        else:
            # Return a search URL the frontend will open
            url = f"https://www.google.com/search?q={query}"
            response_text = f"Searching the web for '{query}'."
            extra["open_url"] = url

    elif intent == IntentClassifier.INTENT_WEATHER:
        city = entities.get("city") or config.get("default_city", "New York")
        response_text = weather_service.get_weather(city)

    elif intent == IntentClassifier.INTENT_EMAIL:
        response_text = (
            "To send an email, I need three things from you. "
            "Please type: recipient email, subject, and message — each on a separate line. "
            "Or say 'send email to <address> subject <subject> message <body>'."
        )
        extra["email_mode"] = True

    elif intent == IntentClassifier.INTENT_REMINDER:
        raw_text = entities.get("raw_text", user_text)
        response_text = reminder_manager.set_reminder(raw_text)

    elif intent == IntentClassifier.INTENT_CUSTOM:
        action = entities.get("action", "")
        trigger = entities.get("trigger", "")
        if action.startswith("http"):
            response_text = f"Opening {trigger} for you."
            extra["open_url"] = action
        else:
            response_text = f"Executing: {trigger}."

    elif intent == IntentClassifier.INTENT_KNOWLEDGE:
        query = entities.get("query", user_text)
        response_text = knowledge_service.answer_question(query)

    elif intent == IntentClassifier.INTENT_HELP:
        response_text = (
            f"Here's what {ASSISTANT_NAME} can do: "
            "say 'hello' to greet me, ask for the time or date, "
            "say 'search [topic]' to search the web, "
            "ask about weather in any city, "
            "say 'remind me in X minutes', "
            "ask any general knowledge question, "
            "or say 'open github' for custom commands."
        )

    else:
        # Try knowledge as last resort
        ans = knowledge_service.answer_question(user_text)
        if "don't have information" not in ans and "find out online" not in ans:
            response_text = ans
        else:
            response_text = (
                "I'm not sure how to respond to that. "
                "Try asking about the weather, time, date, or say 'help' to see what I can do."
            )

    return jsonify({
        "response": response_text,
        "intent": intent,
        **extra
    })


@app.route("/api/email/send", methods=["POST"])
def send_email_api():
    """Dedicated email send endpoint."""
    data = request.get_json(silent=True) or {}
    recipient = data.get("recipient", "")
    subject = data.get("subject", "Message from Nova")
    body = data.get("body", "")

    if not recipient or not body:
        return jsonify({"success": False, "response": "Please provide recipient and message."})

    success, msg = email_service.send_email(recipient, subject, body)
    return jsonify({"success": success, "response": msg})


@app.route("/api/reminders")
def get_reminder_alerts():
    """Poll endpoint for pending reminder notifications."""
    alerts = reminder_alerts.copy()
    reminder_alerts.clear()
    return jsonify({"alerts": alerts})


# ── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    print(f"\n{'='*55}")
    print(f"  {ASSISTANT_NAME} Voice Assistant Web App")
    print(f"  Running at: http://localhost:{port}")
    print(f"{'='*55}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
