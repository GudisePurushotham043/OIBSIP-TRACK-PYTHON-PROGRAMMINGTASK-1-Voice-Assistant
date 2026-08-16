# Project Implementation Phases

# TASK 1 – Voice Assistant

## Phase 1 – Research

- [ ] Search YouTube for “Python voice assistant tutorial speech_recognition pyttsx3”
- [ ] Study SpeechRecognition library setup
- [ ] Study pyttsx3 text-to-speech
- [ ] Study Python datetime
- [ ] Study Python webbrowser
- [ ] Study microphone configuration
- [ ] For advanced implementation, study NLP intent recognition
- [ ] Study OpenWeatherMap API
- [ ] Study Python SMTP email
- [ ] Study secure API-key storage

## Phase 2 – Environment Setup

Create the project folder:

```text
Voice-Assistant/
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install beginner dependencies:

```bash
pip install SpeechRecognition pyttsx3 PyAudio
```

Advanced dependencies can include:

```bash
pip install nltk requests python-dotenv
```

Create:

```text
requirements.txt
```

## Phase 3 – Project Structure

Create:

```text
Voice-Assistant/
│
├── app.py
├── assistant.py
├── config.json
├── .env
├── .gitignore
├── requirements.txt
├── README.md
│
└── modules/
    ├── speech.py
    ├── commands.py
    ├── weather.py
    ├── email.py
    └── reminder.py
```

## Phase 4 – Microphone Setup

- [ ] Import SpeechRecognition
- [ ] Create Recognizer object
- [ ] Create microphone object
- [ ] Test microphone input
- [ ] Adjust ambient noise
- [ ] Listen for speech
- [ ] Convert speech to text
- [ ] Print recognized text
- [ ] Test multiple voice inputs

Expected:

```text
Listening...
You said: hello
```

## Phase 5 – Text-to-Speech

- [ ] Import pyttsx3
- [ ] Initialize engine
- [ ] Create `speak()` function
- [ ] Configure voice
- [ ] Test speech output
- [ ] Use `speak()` for every assistant response

Expected:

```text
Assistant:
Hello! How can I help you?
```

## Phase 6 – Beginner Commands

Implement:

### Greeting

- [ ] Detect hello
- [ ] Respond with greeting

### Time

- [ ] Import datetime
- [ ] Get current time
- [ ] Format time
- [ ] Speak time

### Date

- [ ] Get current date
- [ ] Format date
- [ ] Speak date

### Web Search

- [ ] Extract search query
- [ ] Create search URL
- [ ] Open browser
- [ ] Confirm search through speech

## Phase 7 – Error Handling

Implement handling for:

- [ ] Unknown speech
- [ ] Microphone error
- [ ] Recognition timeout
- [ ] Internet failure
- [ ] Unknown command

Example:

```text
Sorry, I didn't understand.
Please repeat.
```

The assistant should continue running rather than crashing.

## Phase 8 – Command Loop

Create the main loop:

```text
Start
 ↓
Listen
 ↓
Recognize
 ↓
Process command
 ↓
Execute action
 ↓
Speak response
 ↓
Listen again
```

Add exit commands:

```text
exit
quit
stop
goodbye
```

## Phase 9 – Advanced NLP

- [ ] Define intent categories
- [ ] Create sample phrases for each intent
- [ ] Implement intent detection
- [ ] Support free-form sentences
- [ ] Extract useful entities such as city, duration and search query
- [ ] Test different sentence variations

Example:

```text
"Could you please tell me what time it is?"
```

should map to:

```text
TIME
```

## Phase 10 – Email Feature

- [ ] Create test email account
- [ ] Configure SMTP
- [ ] Store credentials securely
- [ ] Ask recipient through voice
- [ ] Ask subject
- [ ] Ask message
- [ ] Validate email
- [ ] Send email
- [ ] Handle SMTP errors
- [ ] Speak confirmation

Never store passwords directly inside Python source code.

## Phase 11 – Reminder Feature

- [ ] Detect reminder intent
- [ ] Extract duration
- [ ] Convert duration to seconds
- [ ] Start timer
- [ ] Wait in background where appropriate
- [ ] Trigger reminder
- [ ] Speak audible alert

Test:

```text
Remind me after 1 minute.
```

## Phase 12 – Weather Feature

- [ ] Create OpenWeatherMap account
- [ ] Obtain API key
- [ ] Store API key in `.env`
- [ ] Create weather module
- [ ] Extract city from command
- [ ] Send API request
- [ ] Parse JSON response
- [ ] Extract temperature
- [ ] Extract weather condition
- [ ] Generate spoken response
- [ ] Handle API errors

Example:

```text
What is the weather in Anantapur?
```

## Phase 13 – General Knowledge

Choose one implementation:

- [ ] Local knowledge base
- [ ] QA API
- [ ] NLP model
- [ ] Other suitable knowledge service

Implement:

```text
Question
   ↓
Knowledge system
   ↓
Answer
   ↓
Text-to-speech
```

## Phase 14 – Custom Commands

- [ ] Create `config.json`
- [ ] Add custom commands
- [ ] Load configuration at startup
- [ ] Match user commands
- [ ] Execute configured actions
- [ ] Test custom commands

Example:

```json
{
    "open github": "https://github.com",
    "open youtube": "https://youtube.com"
}
```

## Phase 15 – Privacy Documentation

Create a README privacy section covering:

- [ ] Microphone usage
- [ ] Speech recognition
- [ ] External APIs
- [ ] Weather requests
- [ ] Email processing
- [ ] API-key storage
- [ ] Audio storage
- [ ] Command history
- [ ] Third-party services

## Phase 16 – Testing

### Beginner Tests

- [ ] Say Hello
- [ ] Ask for time
- [ ] Ask for date
- [ ] Perform web search
- [ ] Say an unrecognized command
- [ ] Test microphone failure
- [ ] Test speech output
- [ ] Test exit command

### Advanced Tests

- [ ] Test natural-language intent
- [ ] Send test email
- [ ] Set reminder
- [ ] Test weather request
- [ ] Ask knowledge question
- [ ] Test custom command
- [ ] Test API failure
- [ ] Test missing API key
- [ ] Test internet failure

## Phase 17 – Code Cleanup

- [ ] Add comments
- [ ] Separate functionality into modules
- [ ] Remove duplicate code
- [ ] Add functions
- [ ] Use meaningful variable names
- [ ] Add exception handling
- [ ] Move secrets to `.env`
- [ ] Add `.env` to `.gitignore`
- [ ] Test complete application

## Phase 18 – Final Deliverables

```text
Voice-Assistant/
│
├── app.py
├── assistant.py
├── config.json
├── requirements.txt
├── README.md
├── .gitignore
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

## Phase 19 – Final Checklist

### Beginner Tier

- [ ] Voice input works
- [ ] Speech recognition works
- [ ] Greeting works
- [ ] Current time works
- [ ] Current date works
- [ ] Web search works
- [ ] Error handling works
- [ ] Text-to-speech works

### Advanced Tier

- [ ] Natural-language intent recognition works
- [ ] Voice email works
- [ ] Timed reminder works
- [ ] Audible reminder works
- [ ] Weather API works
- [ ] General knowledge answering works
- [ ] Custom commands work
- [ ] Privacy documentation completed

### Final Quality

- [ ] No API keys committed to GitHub
- [ ] No passwords hard-coded
- [ ] README completed
- [ ] requirements.txt completed
- [ ] All modules tested
- [ ] Application runs without unexpected crashes
- [ ] Final project folder is organized