import unittest
import responses

from unittest.mock import patch

from audio_client import AudioClient
from button import button_action


class TestAudioClient(unittest.TestCase):
    def setUp(self) -> None:
        self.client = AudioClient('https://example.com/api/', user_id=1,
                                  user_password='abcd', client_id='some-client-id',
                                  client_secret='some-client-secret')

    # todo Check other wrong patches (they silently fail!!)
    @patch('button._post_user_action')
    def test_button_action(self, mock_post_user_action):
        def _actual_fn():
            return {'called': '_actual_fn', 'state_from': 'from', 'state_to': 'to'}

        button_callback = button_action('sample-button',
                                        _actual_fn,
                                        self.client,
                                        'https://example.com/api/user-activity-log/')

        button_callback()

        mock_args = mock_post_user_action.call_args_list[0][0]
        self.assertEqual(mock_args[1], 'https://example.com/api/user-activity-log/')
        self.assertDictEqual(mock_args[2], {'activity': 'sample-button',
                                            'data': {'state_from': 'from', 'called': '_actual_fn', 'state_to': 'to'}})

    @patch('button._post_user_action')
    def test_button_action_with_error(self, mock_post_user_action):
        def _actual_fn():
            raise IndexError("This point expects main player, got: urgent-mail")

        button_callback = button_action('sample-button',
                                        _actual_fn,
                                        self.client,
                                        'https://example.com/api/user-activity-log/')

        button_callback()

        mock_args = mock_post_user_action.call_args_list[0][0]
        self.assertEqual(mock_args[1], 'https://example.com/api/user-activity-log/')
        self.assertDictEqual(mock_args[2], {'activity': 'sample-button',
                                            'error': "Unexpected Error: This point expects "
                                                     "main player, got: urgent-mail"})
