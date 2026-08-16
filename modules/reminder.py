"""
Reminder Module: Handles setting background timed reminders with audible notifications.
"""

import re
import time
import threading
import logging
import sys
from typing import Callable, Optional, List, Dict

logger = logging.getLogger(__name__)


class ReminderManager:
    """Manages asynchronous timed reminders with audible and voice alerts."""

    def __init__(self, alert_callback: Optional[Callable[[str], None]] = None):
        self.alert_callback = alert_callback
        self.active_reminders: List[Dict] = []

    @staticmethod
    def parse_duration_to_seconds(text: str) -> Optional[int]:
        """
        Extract duration from strings like '5 minutes', '30 seconds', '1 hour', '2 mins'.
        """
        text = text.lower()

        # Check for seconds
        sec_match = re.search(r"(\d+)\s*(?:seconds?|secs?|s\b)", text)
        min_match = re.search(r"(\d+)\s*(?:minutes?|mins?|m\b)", text)
        hr_match = re.search(r"(\d+)\s*(?:hours?|hrs?|h\b)", text)

        total_seconds = 0
        found = False

        if sec_match:
            total_seconds += int(sec_match.group(1))
            found = True
        if min_match:
            total_seconds += int(min_match.group(1)) * 60
            found = True
        if hr_match:
            total_seconds += int(hr_match.group(1)) * 3600
            found = True

        # Handle 'half an hour'
        if "half an hour" in text or "half hour" in text:
            total_seconds += 1800
            found = True

        # If only a raw number was found near remind or after
        if not found:
            raw_match = re.search(r"(?:after|in|for)\s+(\d+)\b", text)
            if raw_match:
                # Default to minutes if unit is omitted
                total_seconds = int(raw_match.group(1)) * 60
                found = True

        return total_seconds if found and total_seconds > 0 else None

    def _play_alert_sound(self) -> None:
        """Produce an audible sound alert."""
        try:
            if sys.platform == "win32":
                import winsound
                # Play 3 short distinct beeps
                for _ in range(3):
                    winsound.Beep(1000, 250)
                    time.sleep(0.1)
            else:
                # Terminal bell for non-Windows platforms
                print("\a\a\a", end="", flush=True)
        except Exception as e:
            logger.debug(f"Could not play sound beep: {e}")

    def _trigger_reminder(self, reminder_text: str, duration_sec: int) -> None:
        """Internal callback invoked when timer expires."""
        logger.info(f"Reminder triggered: {reminder_text}")
        self._play_alert_sound()

        msg = f"🔔 Reminder alert! Your reminder is due: {reminder_text}"
        if self.alert_callback:
            self.alert_callback(msg)
        else:
            print(f"\n{msg}")

    def set_reminder(self, text: str, custom_message: Optional[str] = None) -> str:
        """
        Parse command and schedule background timer.
        """
        seconds = self.parse_duration_to_seconds(text)
        if not seconds:
            return "I couldn't determine the reminder duration. Please specify like 'remind me after 5 minutes'."

        reminder_note = custom_message or "Time is up!"
        
        # Format human-friendly time description
        if seconds < 60:
            time_str = f"{seconds} second{'s' if seconds != 1 else ''}"
        elif seconds < 3600:
            mins = seconds // 60
            secs = seconds % 60
            time_str = f"{mins} minute{'s' if mins != 1 else ''}" + (f" {secs} seconds" if secs else "")
        else:
            hrs = seconds // 3600
            mins = (seconds % 3600) // 60
            time_str = f"{hrs} hour{'s' if hrs != 1 else ''}" + (f" {mins} minutes" if mins else "")

        timer = threading.Timer(seconds, self._trigger_reminder, args=[reminder_note, seconds])
        timer.daemon = True
        timer.start()

        self.active_reminders.append({"timer": timer, "note": reminder_note, "duration": seconds})
        return f"Reminder set for {time_str} from now."
