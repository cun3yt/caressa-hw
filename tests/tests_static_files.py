import unittest
import os.path


class TestStaticFiles(unittest.TestCase):
    def test_notification_file_exists(self):
        self.assertTrue(os.path.isfile('./sounds/message-notification.mp3'))

    def test_positive_feedback_file_exists(self):
        self.assertTrue(os.path.isfile('./sounds/positive-feedback.mp3'))

    def test_negative_feedback_file_exists(self):
        self.assertTrue(os.path.isfile('./sounds/negative-feedback.mp3'))
