import unittest
import responses
import json

from button import button_action


class TestAudioClient(unittest.TestCase):
    @responses.activate
    def test_get_channels_with_access_token(self):
        def _actual_fn():
            return {'called': '_actual_fn', 'state_from': 'from', 'state_to': 'to'}

        button_callback = button_action('sample-button',
                                        _actual_fn,
                                        'https://example.com/api/user-activity-log/')

        responses.add(method=responses.POST,
                      url='https://example.com/api/user-activity-log/',
                      json={'channels': ['channel.X', 'channel.Y']},
                      status=200)

        button_callback()

        self.assertEqual(len(responses.calls), 1)
        request_body = json.loads(responses.calls[0].request.body.decode("utf-8"))
        self.assertEqual(request_body['activity'], 'sample-button')
        self.assertEqual(request_body['data'], {'called': '_actual_fn',
                                                'state_to': 'to',
                                                'state_from': 'from', })
