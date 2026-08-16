"""
Main Entry Point for the Python Voice Assistant Application.
"""

import sys
import argparse

try:
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from assistant import VoiceAssistant

BANNER = r"""
 =========================================================
   🤖 PYTHON VOICE ASSISTANT (BEGINNER & ADVANCED TIERS)
 =========================================================
   • Voice Input & Text-to-Speech (pyttsx3)
   • Date & Time / Web Search
   • Live Weather (OpenWeatherMap)
   • Timed Background Reminders & Audible Alerts
   • Voice Email Dispatcher (SMTP)
   • General Knowledge & Encyclopedic Q&A
   • Configurable Custom Commands
 =========================================================
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="Python Voice Assistant - Interactive Voice & Text Assistant"
    )
    parser.add_argument(
        "-t", "--text-mode",
        action="store_true",
        help="Run in interactive text-only mode (bypasses microphone)"
    )
    parser.add_argument(
        "-c", "--config",
        type=str,
        default="config.json",
        help="Path to custom configuration JSON file (default: config.json)"
    )
    return parser.parse_args()


def main():
    print(BANNER)
    args = parse_args()

    mode_str = "Text-Only Mode" if args.text_mode else "Voice Recognition Mode (with Text Fallback)"
    print(f"[*] Starting assistant in: {mode_str}")
    print("[*] Say or type 'help' for commands, or 'exit' / 'goodbye' to quit.\n")

    assistant = VoiceAssistant(config_path=args.config, text_only=args.text_mode)
    try:
        assistant.run()
    except (KeyboardInterrupt, EOFError):
        print("\n\n[!] Session interrupted by user. Exiting safely.")
    except Exception as e:
        print(f"\n[!] Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
