import unittest
from phone_service import make_urgency_call


class TestAudio(unittest.TestCase):
    def test_call(self):
        call = make_urgency_call()
        self.assertEqual(call.get('to'), '+14155337523')
        self.assertEqual(call.get('from'), '+15109015152')
        self.assertEqual(call.get('command'), 'twilio.call')
        self.assertEqual(call.get('url'), 'https://s3-us-west-1.amazonaws.com/caressa-prod/development-related/urgent-button-from-user-maggy.xml')
