# Python Voice Assistant (Beginner & Advanced Tiers)

A modular, extensible, and error-tolerant Python Voice Assistant designed to execute commands through spoken voice or keyboard interaction, providing natural text-to-speech audio feedback.

---

## 🌟 Key Features

### 🐣 Beginner Tier
- **Speech Recognition (STT)**: Captures voice input from the microphone with ambient noise calibration via `SpeechRecognition`.
- **Text-to-Speech (TTS)**: Audible spoken responses using `pyttsx3`.
- **Greetings**: Responds naturally to `hello`, `hi`, `hey`, `good morning`.
- **Date & Time**: Real-time queries (`"what time is it"`, `"what is today's date"`).
- **Web Search**: Automatically opens web browser searches (`"search Python tutorials"`).
- **Graceful Error Handling**: Manages timeouts, microphone disconnects, and unknown speech without crashing.

### 🚀 Advanced Tier
- **Natural Language Understanding (NLU)**: Regex & intent classification mapping conversational queries to actions (e.g. *"Could you please tell me what time it is?"*).
- **Live Weather Reports**: Real-time weather forecasting using OpenWeatherMap API with temperature (°C), conditions, and humidity.
- **Voice-Guided Emailing**: Voice-driven SMTP email composition (recipient validation, subject, message body) with TLS authentication.
- **Timed Background Reminders**: Asynchronous non-blocking timers with audible alerts and spoken notifications.
- **General Knowledge Q&A**: Encyclopedic question answering using local knowledge base and Wikipedia summaries.
- **Custom Configurable Commands**: Add custom shortcuts and browser triggers directly in `config.json`.
- **Dual Mode (Voice & Text)**: Runs in full microphone voice mode with automatic text fallback, plus `--text-mode` for silent/headless environments.

---

## 🏗️ Architecture

```text
                         ┌──────────────────┐
                         │      USER        │
                         └────────┬─────────┘
                                  │
                   ┌──────────────┴──────────────┐
                   ▼                             ▼
             Microphone (STT)              Console / Text Input
                   │                             │
                   └──────────────┬──────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  INTENT PARSER   │
                         │  & NLU ENGINE    │
                         └────────┬─────────┘
                                  │
       ┌──────────────────────────┼──────────────────────────┐
       ▼                          ▼                          ▼
Basic Commands             Advanced Services          Custom Commands
(Time, Date, Search)     (Weather, Email, Reminder)    (config.json)
       │                          │                          │
       └──────────────────────────┼──────────────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ RESPONSE ENGINE  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     pyttsx3      │
                         │  TEXT-TO-SPEECH  │
                         └────────┬─────────┘
                                  │
                                  ▼
                               SPEAKER
```

---

## 📁 Project Structure

```text
Voice-Assistant/
├── app.py                 # Main entry point and CLI runner
├── assistant.py           # Core VoiceAssistant orchestrator
├── config.json            # Configuration file for custom commands & assistant settings
├── .env.example           # Template for environment variables (API keys, SMTP)
├── .gitignore             # Git ignore file for secrets (.env) and Python artifacts
├── requirements.txt       # Dependencies
├── README.md              # Project documentation & privacy guide
│
├── modules/
│   ├── __init__.py        # Module package initializer
│   ├── speech.py          # Speech-to-text (STT) and Text-to-speech (TTS) engine
│   ├── commands.py        # Natural Language Intent Classifier & Command Dispatcher
│   ├── weather.py         # Live weather service integration (OpenWeatherMap)
│   ├── email.py           # Voice-controlled email dispatcher via SMTP
│   ├── reminder.py        # Background asynchronous reminder & audible alert manager
│   └── knowledge.py       # General knowledge QA service (Wikipedia & local KB)
│
└── tests/
    └── test_assistant.py  # Comprehensive unit test suite
```

---

## 🚀 Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher installed on your system.

### 2. Clone / Open the Workspace
```powershell
cd "Voice-Assistant"
```

### 3. Create and Activate Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Activate on Windows (CMD)
.\venv\Scripts\activate.bat
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

> [!TIP]
> **Windows PyAudio Installation Note**:
> If `pip install PyAudio` encounters a build error on older Windows environments, install the pre-compiled wheel using:
> `pip install pipwin && pipwin install pyaudio`

---

## ⚙️ Configuration

### Environment Variables (`.env`)
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```
Edit `.env` with your API keys and credentials:
```env
# OpenWeatherMap API Key (Get a free key from https://openweathermap.org/api)
OPENWEATHER_API_KEY=your_actual_api_key_here

# Email Configuration (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_gmail_app_password_here
```

### Custom Commands (`config.json`)
You can register custom shortcuts and web destinations in `config.json`:
```json
{
  "assistant_name": "Nova",
  "tts_rate": 175,
  "tts_volume": 1.0,
  "default_city": "New York",
  "custom_commands": {
    "open github": "https://github.com",
    "open youtube": "https://youtube.com",
    "open google": "https://google.com",
    "open stackoverflow": "https://stackoverflow.com",
    "open python documentation": "https://docs.python.org/3/"
  }
}
```

---

## 🎮 How to Run

### 1. Default Voice Mode
```powershell
python app.py
```
Speak commands into your microphone when prompted with `🎙️ Listening...`.

### 2. Text-Only Mode (Keyboard Input)
```powershell
python app.py --text-mode
```
Type your commands directly in the console (ideal for environments without a microphone).

---

## 🗣️ Example Commands

| Category | Example Voice / Text Command | Description |
|---|---|---|
| **Greeting** | `"Hello"`, `"Good morning"` | Greets the user with assistant intro |
| **Time** | `"What time is it?"`, `"Tell me the time"` | Announces current local time |
| **Date** | `"What is today's date?"` | Announces today's full date |
| **Search** | `"Search Python data science tutorials"` | Opens default browser with Google Search |
| **Weather** | `"What is the weather in London?"` | Fetches live temperature and condition |
| **Reminder** | `"Remind me after 5 minutes to take a break"` | Schedules non-blocking timer with alert sound |
| **Email** | `"Send an email"` | Interactive voice prompt for recipient, subject, and body |
| **Knowledge**| `"Who invented Python?"`, `"What is artificial intelligence?"` | Answers using Wikipedia & local KB |
| **Custom** | `"Open GitHub"`, `"Open YouTube"` | Launches configured URL in browser |
| **Help** | `"What can you do?"`, `"Help"` | Speaks available capabilities |
| **Exit** | `"Exit"`, `"Quit"`, `"Goodbye"` | Safely terminates the assistant |

---

## 🔒 Privacy Considerations

In compliance with the project specification:
1. **Microphone Capture**: Audio is only captured in short segments (5–8 seconds) during active listening prompts. Continuous or passive recording is strictly prohibited.
2. **Audio Storage**: Audio is streamed in memory directly to the speech recognizer and is **never saved to disk or permanently stored**.
3. **External Services**:
   - Google Speech Recognition API receives temporary audio bytes for transcription.
   - OpenWeatherMap API receives only the city name queried.
   - Wikipedia API receives only the search entity/topic.
4. **Email Security**:
   - SMTP credentials are read exclusively from environment variables (`.env`).
   - Passwords and API tokens are never hard-coded in the source repository.
   - `.env` is listed in `.gitignore` to prevent accidental commits.
5. **Data History**: No conversation transcripts or personally identifiable information are logged or uploaded.

---

## 🧪 Running Unit Tests

Run the automated test suite to verify intent classification, duration parsing, and email validation:
```powershell
python -m unittest discover -s tests -p "test_*.py"
```

---

## 📄 License
MIT License. Created for the OIBSIP Python Programming Track.
#   O I B S I P - T R A C K - P Y T H O N - P R O G R A M M I N G T A S K - 1 - V o i c e - A s s i s t a n t  
 