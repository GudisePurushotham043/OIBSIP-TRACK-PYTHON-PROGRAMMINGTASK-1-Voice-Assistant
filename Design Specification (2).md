# Design Specification

# TASK 1 – Voice Assistant

## 1. Design Concept

**Concept:** Simple, Modular Voice Assistant

The application should be designed as a command-driven Python application with separate modules for speech recognition, text-to-speech, command processing and advanced services.

The architecture should make it easy to add new commands without modifying the entire application.

## 2. System Architecture

```text
                         ┌──────────────────┐
                         │      USER        │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    MICROPHONE    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ SPEECH RECOGNITION│
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   TEXT COMMAND   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  INTENT PARSER   │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
        Basic Commands       Advanced APIs       Custom Commands
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ RESPONSE ENGINE │
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

## 3. Module Design

### `app.py`

Main entry point.

Responsibilities:

- Start the assistant
- Initialize modules
- Run the command loop
- Handle shutdown

### `speech.py`

Responsibilities:

- Initialize microphone
- Listen to audio
- Convert speech to text
- Handle recognition errors

### `commands.py`

Responsibilities:

- Process recognized text
- Identify user intent
- Execute appropriate action

### `weather.py`

Responsibilities:

- Connect to weather API
- Request weather data
- Extract useful information
- Return readable results

### `email.py`

Responsibilities:

- Collect recipient
- Collect subject/message
- Connect to SMTP server
- Send email
- Handle authentication errors

### `reminder.py`

Responsibilities:

- Accept duration
- Start timer
- Trigger reminder
- Generate audible notification

## 4. Beginner Command Design

### Greeting

Input:

```text
hello
hi
hey
```

Output:

```text
Hello! How can I help you?
```

### Time

Input examples:

```text
what time is it
tell me the time
current time
```

Process:

```text
Command
   ↓
datetime.now()
   ↓
Format time
   ↓
Speak result
```

### Date

Input examples:

```text
what is today's date
tell me the date
today's date
```

Process:

```text
Command
   ↓
datetime.now()
   ↓
Format date
   ↓
Speak result
```

### Web Search

Input:

```text
search Python tutorials
```

Process:

```text
Extract query
      ↓
Create search URL
      ↓
webbrowser.open()
      ↓
Speak confirmation
```

## 5. Speech Recognition Design

The assistant should use:

```python
speech_recognition
```

Basic flow:

```text
Microphone
    ↓
Recognizer
    ↓
Listen
    ↓
Recognize Speech
    ↓
Text
```

If recognition fails:

```text
Assistant:
Sorry, I didn't understand.
Please repeat.
```

## 6. Text-to-Speech Design

Use:

```python
pyttsx3
```

The assistant should have a central function such as:

```text
speak(message)
```

All responses should pass through this function.

Example:

```text
speak("Hello! How can I help you?")
```

This keeps the application's audio behavior consistent.

## 7. Advanced Intent Design

Instead of only checking exact commands, classify user requests into intents.

Example:

```text
"What time do we have?"
       ↓
TIME_INTENT

"Could you tell me today's date?"
       ↓
DATE_INTENT

"Please search for Python tutorials"
       ↓
SEARCH_INTENT

"Will it rain today?"
       ↓
WEATHER_INTENT
```

Possible intent categories:

```text
GREETING
TIME
DATE
SEARCH
EMAIL
REMINDER
WEATHER
KNOWLEDGE
CUSTOM
EXIT
```

## 8. Email Design

Voice workflow:

```text
User
 ↓
"Send an email"
 ↓
Ask recipient
 ↓
Ask subject
 ↓
Ask message
 ↓
Validate information
 ↓
SMTP server
 ↓
Send email
 ↓
Speak confirmation
```

Security requirements:

- Do not hard-code passwords
- Use environment variables
- Use a test account
- Never commit secrets to GitHub

## 9. Reminder Design

Example:

```text
User:
Remind me after 5 minutes.

        ↓

Extract:
5 minutes

        ↓

Start timer

        ↓

Wait

        ↓

Reminder triggered

        ↓

pyttsx3:
"Your reminder is due."
```

## 10. Weather Design

Workflow:

```text
Voice Command
     ↓
Extract City
     ↓
Weather API
     ↓
JSON Response
     ↓
Extract Temperature
     ↓
Extract Weather Condition
     ↓
Generate Sentence
     ↓
Speak Result
```

Example response:

```text
The current temperature is 28 degrees Celsius
with partly cloudy conditions.
```

## 11. Custom Command Design

Store commands in:

```text
config.json
```

Example:

```json
{
    "open github": "https://github.com",
    "open youtube": "https://youtube.com",
    "open google": "https://google.com"
}
```

The command processor checks the configuration before reporting an unknown command.

## 12. User Interaction

The assistant should provide clear spoken feedback.

Example:

```text
Assistant:
Listening...

User:
Hello

Assistant:
Hello! How can I help you?

Assistant:
Listening...

User:
What time is it?

Assistant:
The current time is 7:30 PM.
```

## 13. Exit Design

Supported exit commands:

```text
exit
quit
goodbye
stop
```

Response:

```text
Goodbye! Have a great day.
```

Then the program terminates safely.

## 14. Error States

### Speech Error

```text
Sorry, I couldn't understand.
Please repeat.
```

### Internet Error

```text
I couldn't connect to the internet.
Please try again later.
```

### API Error

```text
The requested service is currently unavailable.
```

### Unknown Command

```text
I don't know how to perform that command yet.
```

### Email Error

```text
I couldn't send the email.
Please check the email configuration.
```

## 15. Privacy Design

The application should clearly explain:

```text
Microphone
   ↓
Speech recognition service
   ↓
Recognized text
   ↓
Command processing
```

The project should document:

- Audio processing
- Speech-recognition service
- Weather API requests
- Email data
- API keys
- Command storage

No sensitive credentials should be included in the source code.