from requests import request
import json
from logger import get_logger


logger = get_logger()


class AudioClient:
    def __init__(self, url, **kwargs):
        self._url = url
        self.streaming_url = '{}/streaming'.format(url)
        self.channel_url = '{}/api/users/me/channels/'.format(url)
        self.user_data_url = '{}/api/users/me/'.format(url)
        self.injectable_content_sync_url = '{}/api/users/me/user-content-repository/'.format(url)
        self.injectable_content_api_url = '{}/api/users/me/contents/'.format(url)
        self.service_request_url = '{}/api/users/me/service-requests/'.format(url)
        self.content_signal_url = '{}/api/audio-files/me/signal/'.format(url)
        self.user_id = kwargs.get('user_id')
        self.user_password = kwargs.get('user_password', '')
        self.client_id = kwargs.get('client_id')
        self.client_secret = kwargs.get('client_secret')
        self.access_token = None
        self.refresh_token = None

        assert self.client_id and self.client_secret and self.user_id, (
            "User ID, Client ID and Client Secret cannot be null. Please check your configuration file"
        )

    def get_user_data(self):
        return self._common_request(self.user_data_url)

    def get_channels(self):
        return self._common_request(self.channel_url)

    def make_service_request(self):
        response = self._common_request(self.service_request_url, 'POST')
        return {'command': "service-request",
                'result': "status-code.{}".format(response.status_code)}

    def post_content_signal(self, hash_, signal='positive'):
        body = {'hash': hash_, 'signal': signal}
        return self._common_request(self.content_signal_url, method='POST', body=body)

    def post_button_action(self, url, method='POST', **kwargs):
        self._common_request(url, method, **kwargs)

    @staticmethod
    def _is_success(status_code):
        return status_code in (200, 201)

    def _common_request(self, url, method='GET', **kwargs):
        if not self.access_token:
            self._authenticate()

        body = kwargs.get('body', {})
        headers = {'Authorization': 'Bearer {}'.format(self.access_token)}

        response = request(method=method, url=url, json=body, headers=headers)

        if self._is_success(response.status_code):
            return response

        response = self._refresh_access_token()

        if self._is_success(response.status_code):
            response = request(method=method, url=url, json=body, headers=headers)

            if self._is_success(response.status_code):
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

        # todo: tts "there is an account problem message", trigger message to Caressa team (e.g. datadog)"
        # todo: how to trap so that it will not repeat the message every X seconds specified in the service
        assert self._is_success(res.status_code), (
            "Authentication supposed to work, there must be some credentials problem"
        )

        self.access_token = res_body['access_token']
        self.refresh_token = res_body['refresh_token']

        logger.info("Access and refresh tokens are saved.")

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

        self.access_token = res_body['access_token']
        self.refresh_token = res_body['refresh_token']

        logger.info("Got new access and refresh token")
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

    def injectable_content_download_fn(self) -> str:
        """
        Downloading User State
        """
        response = self._common_request(self.injectable_content_sync_url)
        res_body = json.loads(response.text)
        return json.dumps(res_body['injected_content_repository'])

    def injectable_content_upload_fn(self, content: str):
        """
        Uploading User State
        """
        self._common_request(self.injectable_content_sync_url, method='PATCH',
                             body={'injected_content_repository': json.loads(content)}, )

    def injectable_content_fetch_available_content_fn(self):
        """
        Fetching all available injectable content for the user
        """
        response = self._common_request(self.injectable_content_api_url)
        res_body = json.loads(response.text)
        return res_body['results']
