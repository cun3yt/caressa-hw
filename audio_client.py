import requests


request_types = [
    'LaunchRequest',
    'PlaybackController.PlayCommandIssued',
    'SessionEndedRequest',
    'PlaybackController.NextCommandIssued',
    'AudioPlayer.PlaybackNearlyFinished',
    'AudioPlayer.PlaybackStarted',
    'PlaybackController.PauseCommandIssued',
]

intent_names = [
    'AMAZON.ResumeIntent',
    'AMAZON.NextIntent',
    'AMAZON.PauseIntent',
]


class AudioClient:
    def __init__(self, url, **kwargs):
        self._url = url
        self.user_session_id = kwargs.get('user_session_id', 'hw-user-session-id')
        self.user_id = kwargs.get('user_id', 'hw-user-id')
        self.device_id = kwargs.get('device_id', 'hw-user-id')

    def request(self, **kwargs):
        request_type = kwargs.get('request_type', None)
        intent_name = kwargs.get('intent_name', None)
        token = kwargs.get('token', None)
        offset = kwargs.get('offset', 0)

        body = {
            'session': {
                'sessionId': self.user_session_id,
            },
            'context': {
                'System': {
                    'user': {
                        'userId': self.user_id,
                    },
                    'device': {
                        'deviceId': self.device_id,
                    }
                },
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

        return requests.post(self._url, json=body)

    def launch(self):
        res = self.request(request_type='LaunchRequest')
        return res

    def pause(self):
        return self.request(request_type='PlaybackController.PauseCommandIssued')

    def send_playback_nearly_finished_signal(self):
        return self.request(request_type='AudioPlayer.PlaybackNearlyFinished')

    def send_playback_started_signal(self, token):
        self.request(request_type='AudioPlayer.PlaybackStarted', token=token)

    # def get_item(self):
    #     return {
    #         'token': self.item,
    #         'url': self.data[self.item],
    #         'offset': self.offset,
    #     }
    #
    # def next_item(self, token):
    #     next_token = token+1 if isinstance(token, int) else 0
    #     next_token = next_token if next_token < len(self.data) else 0
    #
    #     return {
    #         'token': next_token,
    #         'url': self.data[next_token],
    #     }


class MockApiClient:
    def __init__(self):
        self.data = [
            'https://s3-us-west-1.amazonaws.com/caressa-prod/song-set/World/Zamfir/08+La+Valse+Muzeta.mp3',
            'https://s3-us-west-1.amazonaws.com/caressa-prod/song-set/World/Zamfir/06+La+Paloma.mp3',
            'https://s3-us-west-1.amazonaws.com/caressa-prod/song-set/World/Zamfir/03+Clair+De+Lune.mp3',
            'https://s3-us-west-1.amazonaws.com/caressa-prod/song-set/World/Tamure+Tahitien/11+Motu+Painu.mp3',
            'https://s3-us-west-1.amazonaws.com/caressa-prod/song-set/Wedding/'
            'Various+-+Baroque+for+Brides+To+Be+-+11+-+Clarke-+Trumpet+Voluntary.mp3',
        ]
        self.item = 0
        self.offset = 0

    def get_item(self):
        return {
            'token': self.item,
            'url': self.data[self.item],
            'offset': self.offset,
        }

    def next_item(self, token):
        next_token = token+1 if isinstance(token, int) else 0
        next_token = next_token if next_token < len(self.data) else 0

        return {
            'token': next_token,
            'url': self.data[next_token],
        }

    def set_state(self, token, offset=0):
        self.item = token
        self.offset = offset
