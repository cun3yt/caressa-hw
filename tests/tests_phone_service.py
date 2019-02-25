import unittest
from phone_service import make_urgency_call
from settings import twilio_account_sid, twilio_auth_token


class TestAudio(unittest.TestCase):
    def test_call(self):
        call = make_urgency_call()
        self.assertEqual(call.to, '+14155337523')
        self.assertEqual(call.from_, '+15109015152')
        self.assertEqual(call.url, 'https://s3-us-west-1.amazonaws.com/caressa-prod/development-related/urgent-button-from-user-maggy.xml')
        self.assertEqual(call.method.lower(), 'get')
        self.assertEqual(call.twilio_account_sid, twilio_account_sid)
        self.assertEqual(call.twilio_auth_token, twilio_auth_token)
