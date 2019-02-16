import json


class Response:
    def __init__(self, text):
        self.text = text


class ApiClient:
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
