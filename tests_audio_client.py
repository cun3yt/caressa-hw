import unittest
from audio_client import AudioClient
from unittest.mock import patch
import responses
import json
from urllib.parse import parse_qs


class _Response:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)


class TestAudioClient(unittest.TestCase):
    def setUp(self):
        self.client = AudioClient('https://example.com', client_id=1234, client_secret='abcd', user_id=5678,
                                  user_password='qwerasdf1234')

    def test_invalid_initialization(self):
        self.assertRaises(AssertionError, AudioClient, 'https://example.com')
        self.assertRaises(AssertionError, AudioClient, 'https://example.com', client_id=1234)
        self.assertRaises(AssertionError, AudioClient, 'https://example.com', client_id=1234, client_secret='abcd')
        self.assertRaises(AssertionError, AudioClient, 'https://example.com', client_id=1234, user_id=5678)
        self.assertRaises(AssertionError, AudioClient, 'https://example.com', client_secret='abcd', user_id=5678)

    def test_initialization(self):
        try:
            audio_client = AudioClient('https://example.com', client_id=1234, client_secret='abcd', user_id=5678)
        except Exception:
            self.fail('No exception is expected')

        self.assertEqual(audio_client.streaming_url, 'https://example.com/streaming')
        self.assertEqual(audio_client.channel_url, 'https://example.com/api/users/me/channels/')
        self.assertEqual(audio_client.user_id, 5678)
        self.assertEqual(audio_client.client_secret, 'abcd')
        self.assertEqual(audio_client.user_password, '')
        self.assertIsNone(audio_client.access_token)
        self.assertIsNone(audio_client.refresh_token)

    def test_initialization_with_password(self):
        audio_client = AudioClient('https://example.com', client_id=1234, client_secret='abcd', user_id=5678,
                                   user_password='qwerasdf1234')

        self.assertEqual(audio_client.user_id, 5678)
        self.assertEqual(audio_client.user_password, 'qwerasdf1234')

    @patch('audio_client.AudioClient._common_request')
    def test_fetching_channels(self, mock_common_request):
        self.client.get_channels()
        mock_common_request.assert_called_once_with('https://example.com/api/users/me/channels/')

    @responses.activate
    @patch('audio_client.AudioClient._authenticate')
    def test_get_channels_no_access_token(self, mock_authenticate):
        def _set_access_token():
            self.client.access_token = 'some-access-token'
            self.client.refresh_token = 'some-refresh-token'

        mock_authenticate.side_effect = _set_access_token

        responses.add(method=responses.GET,
                      url='https://example.com/api/users/me/channels/',
                      json={'channels': ['channel.X', 'channel.Y']},
                      status=200)

        self.client.access_token = None

        response = self.client.get_channels()

        mock_authenticate.called_once_with()

        self.assertEqual(len(responses.calls), 1)
        call = responses.calls[0]
        self.assertEqual(call.request.headers['Authorization'], 'Bearer some-access-token')

        self.assertEqual(json.loads(call.request.body.decode("utf-8")), {})

        self.assertEqual(call.request.method, 'GET')
        self.assertEqual(call.request.url, 'https://example.com/api/users/me/channels/')

        self.assertEqual(response.status_code, 200)
        response_dict = json.loads(response.text)
        self.assertEqual(response_dict['channels'], ['channel.X', 'channel.Y'])

    @responses.activate
    @patch('audio_client.AudioClient._authenticate')
    def test_get_channels_with_access_token(self, mock_authenticate):
        self.client.access_token = 'some-access-token'
        self.client.refresh_token = 'some-refresh-token'

        responses.add(method=responses.GET,
                      url='https://example.com/api/users/me/channels/',
                      json={'channels': ['channel.X', 'channel.Y']},
                      status=200)

        self.client.get_channels()
        mock_authenticate.assert_not_called()

    @responses.activate
    @patch('audio_client.AudioClient._authenticate')
    @patch('audio_client.AudioClient._refresh_access_token')
    def test_get_channels_with_invalid_access_and_invalid_refresh(self, mock_refresh, mock_authenticate):
        self.client.access_token = 'invalid-access-token'
        self.client.refresh_token = 'some-refresh-token'

        responses.add(method=responses.GET,
                      url='https://example.com/api/users/me/channels/',
                      json={'error': 'not allowed'},
                      status=401)

        mock_refresh.return_value = _Response(status_code=200)

        self.client.get_channels()
        self.assertEqual(len(responses.calls), 3)
        mock_refresh.assert_called_once_with()
        mock_authenticate.assert_called_once_with()

    @responses.activate
    @patch('audio_client.AudioClient._refresh_access_token')
    def test_get_channels_invalid_access_code(self, mock_refresh):
        self.client.access_token = 'some-access-token'
        responses.add(method=responses.GET,
                      url='https://example.com/api/users/me/channels/',
                      json={'error': 'not allowed'},
                      status=401)

        mock_refresh.return_value = _Response(status_code=200)

        responses.add(method=responses.GET,
                      url='https://example.com/api/users/me/channels/',
                      json={'channels': ['channel.X', 'channel.Y']},
                      status=200)

        response = self.client.get_channels()
        self.assertEqual(len(responses.calls), 2)
        mock_refresh.assert_called_once_with()
        response_dict = json.loads(response.text)
        self.assertEqual(response_dict['channels'], ['channel.X', 'channel.Y'])

    @responses.activate
    @patch('audio_client.AudioClient._authenticate')
    @patch('audio_client.AudioClient._refresh_access_token')
    def test_get_channels_refresh_token_failure(self, mock_refresh, mock_authenticate):
        def _set_access_token():
            self.client.access_token = 'new-access-token'
            self.client.refresh_token = 'new-refresh-token'

        mock_authenticate.side_effect = _set_access_token

        self.client.access_token = 'some-access-token'

        responses.add(method=responses.GET,
                      url='https://example.com/api/users/me/channels/',
                      json={'error': 'not allowed'},
                      status=401)

        mock_refresh.return_value = _Response(status_code=400)

        responses.add(method=responses.GET,
                      url='https://example.com/api/users/me/channels/',
                      json={'channels': ['channel.X', 'channel.Y']},
                      status=200)

        response = self.client.get_channels()

        self.assertEqual(len(responses.calls), 2)
        mock_authenticate.assert_called_once_with()
        response_dict = json.loads(response.text)
        self.assertEqual(response_dict['channels'], ['channel.X', 'channel.Y'])

    @patch('audio_client.AudioClient._streaming_request')
    def test_launch(self, mock_streaming_request):
        self.client.launch()
        mock_streaming_request.assert_called_once_with(request_type='LaunchRequest')

    @patch('audio_client.AudioClient._common_request')
    def test_launch_stream(self, mock_common_request):
        self.client.launch()
        mock_common_request.assert_called_once_with('https://example.com/streaming',
                                                    method='post',
                                                    body={
                                                        'context': {
                                                            'AudioPlayer': {
                                                                'offsetInMilliseconds': 0,
                                                                'token': None,
                                                            }
                                                        },
                                                        'request': {
                                                            'type': 'LaunchRequest',
                                                            'intent': {
                                                                'name': None,
                                                            },
                                                        }
                                                    })

    @responses.activate
    def test_authentication(self):
        responses.add(method=responses.POST,
                      url='https://example.com/o/token/',
                      json={'access_token': 'new-access-token', 'refresh_token': 'new-refresh-token', },
                      status=200)
        self.client._authenticate()
        self.assertEqual(len(responses.calls), 1)
        call = responses.calls[0]
        self.assertEqual(call.request.url, 'https://example.com/o/token/')
        self.assertEqual(call.request.method.lower(), 'post')

        query_params = parse_qs(call.request.body)
        self.assertEqual(query_params['grant_type'][0], 'password')
        self.assertEqual(query_params['client_id'][0], '1234')
        self.assertEqual(query_params['client_secret'][0], 'abcd')
        self.assertEqual(query_params['username'][0], '5678@proxy.caressa.ai')
        self.assertEqual(query_params['password'][0], 'qwerasdf1234')

        self.assertEqual(self.client.access_token, 'new-access-token')
        self.assertEqual(self.client.refresh_token, 'new-refresh-token')

    @responses.activate
    def test_authentication_failure(self):
        responses.add(method=responses.POST,
                      url='https://example.com/o/token/',
                      json={'error': 'authentication failed', },
                      status=400)
        self.assertRaises(AssertionError, self.client._authenticate)

    @responses.activate
    def test_refresh_token(self):
        responses.add(method=responses.POST,
                      url='https://example.com/o/token/',
                      json={'access_token': 'new-access-token', 'refresh_token': 'new-refresh-token', },
                      status=200)
        self.client.refresh_token = 'some-valid-refresh-token'
        self.client._refresh_access_token()
        self.assertEqual(self.client.access_token, 'new-access-token')
        self.assertEqual(self.client.refresh_token, 'new-refresh-token')

        self.assertEqual(len(responses.calls), 1)
        call = responses.calls[0]
        self.assertEqual(call.request.url, 'https://example.com/o/token/')
        self.assertEqual(call.request.method.lower(), 'post')

        query_params = parse_qs(call.request.body)
        self.assertEqual(query_params['grant_type'][0], 'refresh_token')
        self.assertEqual(query_params['refresh_token'][0], 'some-valid-refresh-token')
        self.assertEqual(query_params['client_id'][0], '1234')
        self.assertEqual(query_params['client_secret'][0], 'abcd')

    @patch('audio_client.AudioClient._streaming_request')
    def test_pause(self, mock_streaming_request):
        self.client.pause()
        mock_streaming_request.assert_called_once_with(request_type='PlaybackController.PauseCommandIssued')

    @patch('audio_client.AudioClient._streaming_request')
    def test_playback_nearly_finished(self, mock_streaming_request):
        self.client.send_playback_nearly_finished_signal()
        mock_streaming_request.assert_called_once_with(request_type='AudioPlayer.PlaybackNearlyFinished')

    @patch('audio_client.AudioClient._streaming_request')
    def test_playback_started(self, mock_streaming_request):
        self.client.send_playback_started_signal('token-value')
        mock_streaming_request.assert_called_once_with(request_type='AudioPlayer.PlaybackStarted', token='token-value')