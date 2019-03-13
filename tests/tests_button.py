import unittest

from unittest.mock import patch

from audio_client import AudioClient
from button import button_action


class TestAudioClient(unittest.TestCase):
    @patch('audio_client.AudioClient.post_button_action')
    def test_get_channels_with_access_token(self, mock_post_button_action):
        def _actual_fn():
            return {'called': '_actual_fn', 'state_from': 'from', 'state_to': 'to'}

        client = AudioClient('https://example.com/api/', user_id=1,
                             user_password='abcd', client_id='some-client-id',
                             client_secret='some-client-secret')

        button_callback = button_action('sample-button',
                                        _actual_fn,
                                        client,
                                        'https://example.com/api/user-activity-log/')

        button_callback()

        mock_post_button_action.assert_called_once_with('https://example.com/api/user-activity-log/',
                                                        method='POST',
                                                        body={'activity': 'sample-button',
                                                              'data': {'called': '_actual_fn',
                                                                       'state_from': 'from',
                                                                       'state_to': 'to'}
                                                              })
