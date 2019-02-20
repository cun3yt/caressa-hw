from requests import request
import json

request_types = [
    'LaunchRequest',
    'PlaybackController.PlayCommandIssued',
    'SessionEndedRequest',
    'PlaybackController.NextCommandIssued',
    'AudioPlayer.PlaybackNearlyFinished',
    'AudioPlayer.PlaybackStarted',
    'PlaybackController.PauseCommandIssued',
]


class AudioClient:
    def __init__(self, url, **kwargs):
        self._url = url
        self.streaming_url = '{}/streaming'.format(url)
        self.channel_url = '{}/api/users/me/channels/'.format(url)
        self.user_session_id = kwargs.get('user_session_id', 'hw-user-session-id')
        self.user_id = kwargs.get('user_id')
        self.user_password = kwargs.get('user_password')
        self.device_id = kwargs.get('device_id', 'hw-device-id')
        self.client_id = kwargs.get('client_id')
        self.client_secret = kwargs.get('client_secret')
        self.access_token = None
        self.refresh_token = None

        assert self.client_id and self.client_secret and self.user_id, (
            "User ID, Client ID and Client Secret cannot be null. Please check your configuration file"
        )

    def get_channels(self):
        return self._common_request(self.channel_url)

    def _common_request(self, url, method='GET', **kwargs):
        if not self.access_token:
            self._authenticate()

        body = kwargs.get('body', {})
        headers = {'Authorization': 'Bearer {}'.format(self.access_token)}

        response = request(method=method, url=url, json=body, headers=headers)

        if response.status_code == 200:
            return response

        response = self._refresh_access_token()

        if response.status_code == 200:
            response = request(method=method, url=url, json=body, headers=headers)

            if response.status_code == 200:
                return response

        self._authenticate()

        response = request(method=method, url=url, json=body, headers=headers)

        return response

    def _streaming_request(self, **kwargs):
        request_type = kwargs.get('request_type', None)
        intent_name = kwargs.get('intent_name', None)
        token = kwargs.get('token', None)
        offset = kwargs.get('offset', 0)

        body = {
            'context': {
                'AudioPlayer': {
                    'offsetInMilliseconds': offset,
                    'token': token,
                }
            },
            'request': {
                'type': request_type,
                'intent': {
                    'name': intent_name,
                },
            }
        }

        return self._common_request(self.streaming_url, method='post', body=body)

    def _authenticate(self):
        token_url = '{}/o/token/'.format(self._url)
        res = request(method='post',
                      url=token_url,
                      data={
                          'grant_type': 'password',
                          'username': '{}@proxy.caressa.ai'.format(self.user_id),
                          'password': self.user_password,
                          'client_id': self.client_id,
                          'client_secret': self.client_secret,
                      }, )

        res_body = json.loads(res.text)

        if res.status_code != 200:
            # todo: tts "there is an account problem message", trigger message to Caressa team (e.g. datadog)"
            # todo: how to trap so that it will not repeat the message every X seconds specified in the service
            print("authentication problem!")
            exit(1)

        print(res_body)

        self.access_token = res_body['access_token']
        self.refresh_token = res_body['refresh_token']

        print('Got access_token: {}'.format(self.access_token))
        print('Got refresh_token: {}'.format(self.refresh_token))

    def _refresh_access_token(self):
        token_url = '{}/o/token/'.format(self._url)
        res = request(method='post',
                      url=token_url,
                      data={
                          'grant_type': 'refresh_token',
                          'refresh_token': self.refresh_token,
                          'client_id': self.client_id,
                          'client_secret': self.client_secret,
                      }, )

        res_body = json.loads(res.text)
        print(res_body)

        self.access_token = res_body['access_token']
        self.refresh_token = res_body['refresh_token']

        print('Got new access_token: {}'.format(self.access_token))
        print('Got new refresh_token: {}'.format(self.refresh_token))
        return res

    def launch(self):
        res = self._streaming_request(request_type='LaunchRequest')
        return res

    def pause(self):
        return self._streaming_request(request_type='PlaybackController.PauseCommandIssued')

    def send_playback_nearly_finished_signal(self):
        return self._streaming_request(request_type='AudioPlayer.PlaybackNearlyFinished')

    def send_playback_started_signal(self, token):
        self._streaming_request(request_type='AudioPlayer.PlaybackStarted', token=token)
