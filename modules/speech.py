"""
Speech Module: Handles Speech Recognition (STT) and Text-to-Speech (TTS).
Uses sounddevice as the microphone backend (PyAudio replacement for Python 3.14+).
"""

import sys
import queue
import logging
import tempfile
import os
import wave
from typing import Optional

try:
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import sounddevice as sd
    import numpy as np
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False


class SpeechEngine:
    """Encapsulates speech recognition (STT) and text-to-speech (TTS) capabilities."""

    SAMPLE_RATE = 16000
    CHANNELS = 1
    LISTEN_SECONDS = 7          # Max listen duration per command
    CHUNK_DURATION = 0.3        # Seconds per chunk for VAD
    SILENCE_CHUNKS_TO_STOP = 5  # Stop after ~1.5s of silence post-speech

    def __init__(self, rate: int = 175, volume: float = 1.0):
        self.rate = rate
        self.volume = volume
        self.tts_engine = None
        self.recognizer = None
        self.mic_available = False

        self._init_tts()
        self._init_stt()

    # ──────────────────────────────────────────────
    # Text-to-Speech Initialization
    # ──────────────────────────────────────────────

    def _init_tts(self) -> None:
        """Initialize pyttsx3 Text-to-Speech engine."""
        if pyttsx3 is None:
            logger.warning("pyttsx3 is not installed. Spoken audio output will be disabled.")
            return
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty("rate", self.rate)
            self.tts_engine.setProperty("volume", self.volume)
            # Select an English voice if available
            voices = self.tts_engine.getProperty("voices")
            if voices:
                for v in voices:
                    if any(k in v.name.lower() for k in ["english", "zira", "david", "hazel"]):
                        self.tts_engine.setProperty("voice", v.id)
                        break
            logger.info("TTS engine initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3 TTS engine: {e}")
            self.tts_engine = None

    # ──────────────────────────────────────────────
    # Speech Recognition Initialization
    # ──────────────────────────────────────────────

    def _init_stt(self) -> None:
        """Initialize SpeechRecognition recognizer and check microphone via sounddevice."""
        if sr is None:
            logger.warning("SpeechRecognition library is not installed.")
            return

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True

        if not SOUNDDEVICE_AVAILABLE:
            logger.warning("sounddevice / numpy not installed. Falling back to keyboard input.")
            return

        try:
            # Quick sounddevice probe: record 0.1s to confirm microphone works
            sd.rec(int(0.1 * self.SAMPLE_RATE), samplerate=self.SAMPLE_RATE,
                   channels=self.CHANNELS, dtype="int16", blocking=True)
            self.mic_available = True
            logger.info("Microphone detected and working (sounddevice backend).")
        except Exception as e:
            logger.warning(f"Microphone probe failed: {e}. Falling back to keyboard input.")
            self.mic_available = False

    # ──────────────────────────────────────────────
    # Speak
    # ──────────────────────────────────────────────

    def speak(self, text: str, print_output: bool = True) -> None:
        """Output text visually and audibly via pyttsx3."""
        if print_output:
            print(f"\n[Assistant] {text}")

        if self.tts_engine is not None:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS output error: {e}")

    # ──────────────────────────────────────────────
    # Listen
    # ──────────────────────────────────────────────

    def _record_with_sounddevice(self) -> Optional[bytes]:
        """
        Record audio using sounddevice with voice-activity detection (VAD).
        Starts collecting when speech is detected, stops after trailing silence.
        """
        chunk_frames = int(self.CHUNK_DURATION * self.SAMPLE_RATE)
        max_chunks = int(self.LISTEN_SECONDS / self.CHUNK_DURATION)

        print("\n[Mic] Listening... (speak now)", end="", flush=True)

        all_chunks = []
        speech_started = False
        silence_count = 0

        for i in range(max_chunks):
            chunk = sd.rec(
                chunk_frames,
                samplerate=self.SAMPLE_RATE,
                channels=self.CHANNELS,
                dtype="int16",
                blocking=True
            )

            # Compute RMS amplitude to detect speech
            rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))
            is_speech = rms > 200  # Threshold for 16-bit audio (0-32768 range)

            if is_speech:
                if not speech_started:
                    print(" [Recording]", end="", flush=True)
                    speech_started = True
                silence_count = 0
                all_chunks.append(chunk)
            elif speech_started:
                all_chunks.append(chunk)   # Include trailing silence too
                silence_count += 1
                if silence_count >= self.SILENCE_CHUNKS_TO_STOP:
                    break  # User stopped speaking
            else:
                print(".", end="", flush=True)  # Waiting dots

        print()

        if not all_chunks:
            return None

        combined = np.concatenate(all_chunks, axis=0)
        return combined.tobytes()

    def _raw_pcm_to_audio_data(self, raw_bytes: bytes) -> Optional["sr.AudioData"]:
        """Convert raw PCM bytes to a speech_recognition.AudioData object via a temp WAV file."""
        if sr is None:
            return None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name

            with wave.open(tmp_path, "wb") as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(2)           # 16-bit = 2 bytes
                wf.setframerate(self.SAMPLE_RATE)
                wf.writeframes(raw_bytes)

            with sr.AudioFile(tmp_path) as source:
                audio = self.recognizer.record(source)

            os.unlink(tmp_path)
            return audio
        except Exception as e:
            logger.error(f"Failed to convert PCM to AudioData: {e}")
            return None

    def listen(self, timeout: int = 5, phrase_time_limit: int = 8) -> Optional[str]:
        """
        Capture voice from the microphone and return transcribed text.
        Falls back to keyboard input if microphone is unavailable.
        """
        if not self.mic_available or not SOUNDDEVICE_AVAILABLE or self.recognizer is None:
            return self._keyboard_fallback()

        try:
            raw_bytes = self._record_with_sounddevice()
            if raw_bytes is None:
                return None

            audio = self._raw_pcm_to_audio_data(raw_bytes)
            if audio is None:
                return None

            print("[Processing speech...]", end="", flush=True)
            text = self.recognizer.recognize_google(audio)
            print(f"\r[You]: {text}" + " " * 20)
            return text.strip()

        except sr.UnknownValueError:
            self.speak("Sorry, I didn't catch that. Could you please repeat?")
            return None
        except sr.RequestError as e:
            self.speak("Speech recognition service is unavailable. Please check your internet connection.")
            logger.error(f"Google Speech API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while listening: {e}")
            return None

    def _keyboard_fallback(self) -> Optional[str]:
        """Read input from keyboard when microphone is not available."""
        try:
            print("\n[Microphone unavailable - Type your command]: ", end="", flush=True)
            user_input = input().strip()
            return user_input if user_input else None
        except (EOFError, KeyboardInterrupt):
            return "exit"
