"""
Unit Tests for Python Voice Assistant Intent Classifier, Reminder, Email, and Knowledge Modules.
"""

import unittest
from modules.commands import IntentClassifier, CommandProcessor
from modules.reminder import ReminderManager
from modules.email import EmailService
from modules.knowledge import KnowledgeService


class TestVoiceAssistant(unittest.TestCase):

    def setUp(self):
        custom_cmds = {
            "open github": "https://github.com",
            "open youtube": "https://youtube.com"
        }
        self.classifier = IntentClassifier(custom_commands=custom_cmds)
        self.cmd_processor = CommandProcessor()

    def test_greeting_intent(self):
        intent, _ = self.classifier.classify("hello there")
        self.assertEqual(intent, IntentClassifier.INTENT_GREETING)

        intent, _ = self.classifier.classify("hi")
        self.assertEqual(intent, IntentClassifier.INTENT_GREETING)

    def test_time_intent(self):
        intent, _ = self.classifier.classify("what is the current time")
        self.assertEqual(intent, IntentClassifier.INTENT_TIME)

        intent, _ = self.classifier.classify("tell me the time")
        self.assertEqual(intent, IntentClassifier.INTENT_TIME)

    def test_date_intent(self):
        intent, _ = self.classifier.classify("what is today's date")
        self.assertEqual(intent, IntentClassifier.INTENT_DATE)

        intent, _ = self.classifier.classify("tell me the date")
        self.assertEqual(intent, IntentClassifier.INTENT_DATE)

    def test_search_intent(self):
        intent, entities = self.classifier.classify("search Python tutorials")
        self.assertEqual(intent, IntentClassifier.INTENT_SEARCH)
        self.assertEqual(entities.get("query"), "Python tutorials")

        intent, entities = self.classifier.classify("google machine learning courses")
        self.assertEqual(intent, IntentClassifier.INTENT_SEARCH)
        self.assertEqual(entities.get("query"), "machine learning courses")

    def test_weather_intent(self):
        intent, entities = self.classifier.classify("what is the weather in London")
        self.assertEqual(intent, IntentClassifier.INTENT_WEATHER)
        self.assertEqual(entities.get("city"), "London")

    def test_reminder_duration_parsing(self):
        self.assertEqual(ReminderManager.parse_duration_to_seconds("remind me in 5 minutes"), 300)
        self.assertEqual(ReminderManager.parse_duration_to_seconds("set a timer for 30 seconds"), 30)
        self.assertEqual(ReminderManager.parse_duration_to_seconds("remind me in 1 hour"), 3600)
        self.assertEqual(ReminderManager.parse_duration_to_seconds("remind me after half an hour"), 1800)

    def test_email_validation(self):
        self.assertTrue(EmailService.validate_email("test@example.com"))
        self.assertTrue(EmailService.validate_email("user.name+tag@sub.domain.org"))
        self.assertFalse(EmailService.validate_email("invalid_email"))
        self.assertFalse(EmailService.validate_email("test@.com"))

    def test_spoken_email_cleanup(self):
        cleaned = EmailService.clean_spoken_email("john dot doe at gmail dot com")
        self.assertEqual(cleaned, "john.doe@gmail.com")

    def test_custom_command_intent(self):
        intent, entities = self.classifier.classify("could you open github please")
        self.assertEqual(intent, IntentClassifier.INTENT_CUSTOM)
        self.assertEqual(entities.get("action"), "https://github.com")

    def test_knowledge_clean_query(self):
        cleaned = KnowledgeService.clean_query("who invented python?")
        self.assertEqual(cleaned, "python")

        cleaned = KnowledgeService.clean_query("tell me about quantum computing")
        self.assertEqual(cleaned, "quantum computing")

    def test_exit_intent(self):
        for phrase in ["exit", "quit", "goodbye", "bye nova", "stop"]:
            intent, _ = self.classifier.classify(phrase)
            self.assertEqual(intent, IntentClassifier.INTENT_EXIT)

    def test_cmd_processor_time_and_date(self):
        time_str = self.cmd_processor.get_time()
        self.assertIn("The current time is", time_str)

        date_str = self.cmd_processor.get_date()
        self.assertIn("Today is", date_str)

    def test_cmd_processor_help(self):
        help_str = self.cmd_processor.get_help()
        self.assertIn("Here is what I can do", help_str)

    def test_local_knowledge_answers(self):
        service = KnowledgeService()
        ans = service.answer_question("who created python")
        self.assertIn("Guido van Rossum", ans)


if __name__ == "__main__":
    unittest.main()
