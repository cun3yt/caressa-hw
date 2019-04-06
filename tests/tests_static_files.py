import unittest
import os.path


class TestStaticFiles(unittest.TestCase):
    def test_notification_file_exists(self):
        self.assertTrue(os.path.isfile('./sounds/message-notification.wav'))

    def test_positive_feedback_file_exists(self):
        self.assertTrue(os.path.isfile('./sounds/positive-feedback.wav'))

    def test_negative_feedback_file_exists(self):
        self.assertTrue(os.path.isfile('./sounds/negative-feedback.wav'))
