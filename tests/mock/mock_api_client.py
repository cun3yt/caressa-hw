import json


class Response:
    def __init__(self, text):
        self.text = text


class ApiClient:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def send_playback_nearly_finished_signal():
        d = {
            'response': {
                'directives': [
                    {
                        'type': 'AudioPlayer.Play',
                        'playBehavior': 'ENQUEUE',
                        'audioItem': {
                            'stream': {
                                'url': 'https://example.com/song1234.mp3',
                                'hash': 'abcd1234',
                                'token': 'abcd',
                            }
                        }
                    }
                ]
            }
        }
        return Response(text=json.dumps(d))

    @staticmethod
    def send_playback_started_signal(token):
        pass

    @staticmethod
    def launch():
        d = {
            'response': {
                'directives': [
                    {
                        'type': 'AudioPlayer.Play',
                        'audioItem': {
                            'stream': {
                                'url': 'http://example.com/audio1.mp3',
                                'hash': 'fdsjo11f3',
                                'token': '1234',
                            }
                        }
                    }
                ]
            }
        }
        return Response(text=json.dumps(d))

    @staticmethod
    def pause():
        return '{}'

    @staticmethod
    def post_button_action(url, method='POST', **kwargs):
        pass

    @staticmethod
    def post_content_signal(hash_, signal):
        pass

    @staticmethod
    def injectable_content_download_fn() -> str:
        return '[]'

    @staticmethod
    def injectable_content_upload_fn(content: str):
        return

    @staticmethod
    def injectable_content_fetch_available_content_fn():
        return []

    @staticmethod
    def make_service_request():
        pass
