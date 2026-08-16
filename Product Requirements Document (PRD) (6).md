# Product Requirements Document (PRD)

# TASK 1 – Voice Assistant

## 1. Project Overview

**Project Name:** Python Voice Assistant

**Project Type:** Voice-Based Personal Assistant

**Technology Stack:**
- Python
- SpeechRecognition
- PyAudio
- pyttsx3
- datetime
- webbrowser
- re
- NLTK / Transformers
- smtplib
- Weather API
- Jupyter Notebook / VS Code

The objective is to build a Python-based voice assistant that listens to spoken commands, understands the user's request and responds through speech.

The project can be implemented in two levels:

- Beginner Tier
- Advanced Tier

## 2. Objective

The voice assistant should:

- Capture voice input through a microphone
- Convert speech into text
- Understand basic commands
- Respond using text-to-speech
- Tell the current date and time
- Perform web searches
- Handle speech-recognition errors gracefully
- Support advanced natural-language commands
- Send emails using voice commands
- Set timed reminders
- Provide weather information
- Answer general knowledge questions
- Allow custom commands
- Document privacy considerations

## 3. Target Users

The application is designed for:

- Beginners learning Python
- Students
- Developers
- Users who prefer voice interaction
- Accessibility-focused applications
- Personal productivity use

## 4. Core Workflow

```text
User
  ↓
Microphone
  ↓
Speech Recognition
  ↓
Speech-to-Text
  ↓
Intent Detection
  ↓
Command Processing
  ↓
Action
  ↓
Text Response
  ↓
Text-to-Speech
  ↓
Speaker
```

## 5. Beginner Tier Requirements

### 5.1 Voice Input

The application must capture spoken input using:

```python
speech_recognition
```

The microphone should be used as the audio source.

### 5.2 Greeting

The assistant must respond to commands such as:

```text
Hello
Hi
Hey
```

Example:

```text
User: Hello
Assistant: Hello! How can I help you?
```

### 5.3 Date and Time

The assistant should respond to commands such as:

```text
What is the time?
What time is it?
Tell me today's date.
What is today's date?
```

Example:

```text
User: What time is it?
Assistant: The current time is 7:30 PM.
```

### 5.4 Web Search

The assistant should allow users to request a search.

Example:

```text
User: Search Python tutorials
Assistant: Searching for Python tutorials.
```

The browser should open with the requested search query.

### 5.5 Error Handling

If speech cannot be understood:

```text
Assistant:
Sorry, I didn't understand that.
Please repeat.
```

If the microphone or recognition service encounters an error, the application should not crash.

### 5.6 Text-to-Speech

Every assistant response should be spoken using:

```python
pyttsx3
```

## 6. Advanced Tier Requirements

The advanced implementation includes all beginner features.

### 6.1 Natural Language Understanding

The assistant should understand free-form sentences instead of relying only on exact keywords.

Example:

```text
"Could you tell me what time it is?"
```

should be interpreted as a time request.

Possible technologies:

- NLTK
- Transformers
- Rule-based intent classification
- Machine-learning intent classification

### 6.2 Voice Email

The assistant should support voice-controlled email sending.

Example:

```text
User:
Send an email to my friend saying I will call later.

Assistant:
What is the recipient email address?

User:
example@gmail.com

Assistant:
What should I send?

User:
I will call you later.

Assistant:
Sending the email.
```

Use:

```python
smtplib
```

A test/dummy account should be used during development.

Credentials must not be hard-coded into the source code.

### 6.3 Timed Reminder

The assistant should allow users to set reminders.

Example:

```text
User:
Remind me after 10 minutes.

Assistant:
Reminder set for 10 minutes.
```

After the specified duration:

```text
Assistant:
Your reminder is due.
```

The reminder should generate an audible alert.

### 6.4 Weather Information

The assistant should retrieve live weather information through a weather API.

Example:

```text
User:
What is the weather in Anantapur?

Assistant:
Fetching the current weather information.
```

The application may use OpenWeatherMap or another suitable weather API.

API keys must be stored securely and not committed to GitHub.

### 6.5 General Knowledge

The assistant should answer general questions using:

- A QA API
- Local knowledge base
- NLP model
- Other appropriate service

Example:

```text
User:
Who developed Python?

Assistant:
Python was created by Guido van Rossum.
```

### 6.6 Custom Commands

Users should be able to add their own commands through:

- Configuration file
- JSON file
- Python configuration
- Voice-based command registration

Example configuration:

```json
{
    "open github": "https://github.com",
    "open youtube": "https://youtube.com"
}
```

## 7. Command Categories

The assistant should recognize commands belonging to categories such as:

| Intent | Example |
|---|---|
| Greeting | Hello |
| Time | What time is it? |
| Date | What is today's date? |
| Search | Search Python |
| Email | Send an email |
| Reminder | Remind me after 5 minutes |
| Weather | What is the weather? |
| Knowledge | Who invented Python? |
| Custom | Open GitHub |

## 8. Error Handling Requirements

The application must handle:

- Microphone unavailable
- Speech not recognized
- Speech recognition timeout
- Internet unavailable
- API failure
- Invalid command
- Invalid email address
- Invalid reminder duration
- Missing API key
- Email authentication failure

The application should provide a spoken error message rather than terminating unexpectedly.

## 9. Privacy Requirements

The README must document:

- When microphone input is captured
- Whether audio is stored
- Which external services receive text
- What API data is sent
- How email credentials are handled
- Where API keys are stored
- Whether command history is saved

The assistant should avoid permanently storing microphone recordings unless explicitly required.

## 10. Non-Functional Requirements

The application should be:

- Easy to use
- Responsive
- Modular
- Secure
- Beginner-friendly
- Well commented
- Easy to extend
- Error tolerant

## 11. Expected Output

The completed project should demonstrate:

- Voice input
- Speech recognition
- Spoken responses
- Greeting
- Date/time
- Web search
- Error handling
- Optional NLP intent recognition
- Email functionality
- Reminder functionality
- Weather functionality
- Knowledge answering
- Custom commands

## 12. Success Criteria

### Beginner

- [ ] Microphone captures voice
- [ ] Speech is converted to text
- [ ] Hello command works
- [ ] Date command works
- [ ] Time command works
- [ ] Web search works
- [ ] Errors are handled
- [ ] pyttsx3 speaks responses

### Advanced

- [ ] NLP intent recognition works
- [ ] Voice email works with a test account
- [ ] Timed reminder works
- [ ] Audible reminder works
- [ ] Weather API works
- [ ] General knowledge answering works
- [ ] Custom commands work
- [ ] Privacy documentation is included

## 13. Final Deliverables

```text
Voice-Assistant/
│
├── app.py
├── assistant.py
├── config.json
├── requirements.txt
├── README.md
│
├── modules/
│   ├── speech.py
│   ├── commands.py
│   ├── weather.py
│   ├── email.py
│   └── reminder.py
│
└── assets/
```