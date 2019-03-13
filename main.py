import json

from audio_client import AudioClient
from audio_player import AudioPlayer
from settings import PUSHER_KEY_ID, PUSHER_CLUSTER, PUSHER_SECRET, SUBDOMAIN as SERVER_URL
from phone_service import make_urgency_call
from logger import get_logger
from button import button_action

from conditional_imports import get_main_dependencies

gi, Gtk, GLib, Button, Thread, Pusher, config_filename = get_main_dependencies()

LEFT_BLACK_BTN_ID = 7
RIGHT_BLACK_BTN_ID = 8
BIG_RED_BTN_ID = 9
SMALL_RED_BTN_ID = 10

logger = get_logger()


# `user_channels` and `player` are set in `main()` function
user_channels = []
player = None
user_id = None


class PusherService:
    _instance = None

    def __init__(self):
        raise ValueError("You cannot initiate PusherSingleton, instead use `get_instance()`")

    @classmethod
    def get_instance(cls) -> Pusher:
        if cls._instance is None:
            cls._instance = Pusher(key=PUSHER_KEY_ID,
                                   cluster=PUSHER_CLUSTER,
                                   secure=True,
                                   secret=PUSHER_SECRET)
        return cls._instance


def handle_mail(audio_player, msg_type):

    def _send_to_player(*args, **kwargs):
        data = json.loads(args[0])
        url = data.get('url')

        is_selected_recipient_type = data.get('is_selected_recipient_type', False)
        selected_recipient_ids = data.get('selected_recipient_ids', None)

        assert user_id, (
            "user_id needs to be set for real-time communication"
        )

        if selected_recipient_ids and not is_selected_recipient_type:
            logger.error("selected_recipient_ids cannot be used without is_selected_recipient_type set to True")
            return

        if is_selected_recipient_type:
            if selected_recipient_ids is None:
                logger.error("selected_recipient_ids is not specified for selected recipient type message, "
                             "it must be specified in the message delivered "
                             "for is_selected_recipient_type = True messages!")
                return

            if user_id not in selected_recipient_ids:
                logger.debug('message received but skipped since the device user is not in the recipient list')
                return

        if msg_type == 'voice_mail':
            audio_player.voice_mail_arrived(url)
        elif msg_type == 'urgent_mail':
            audio_player.urgent_mail_arrived(url)
        else:
            logger.error("Unknown message type for handle_mail function: {}".format(msg_type))

    return _send_to_player


def connect_handler(*args, **kwargs):
    logger.info("connect_handler")

    channels = kwargs.get('injected_user_channels', user_channels)
    audio_player = kwargs.get('injected_player', player)

    for channel_id in channels:
        channel = PusherService.get_instance().subscribe(channel_id)
        channel.bind('voice_mail', handle_mail(audio_player, 'voice_mail'))
        channel.bind('urgent_mail', handle_mail(audio_player, 'urgent_mail'))
        logger.info("connected to {channel_id}".format(channel_id=channel_id))


def setup_realtime_update():
    PusherService.get_instance().connection.bind('pusher:connection_established', connect_handler)
    PusherService.get_instance().connect()
    logger.info("pusher is connected")


def setup_client():
    with open(config_filename) as json_data_file:
        conf = json.load(json_data_file)

    client = AudioClient(url=SERVER_URL,
                         user_id=conf['user']['id'],
                         user_password=conf['user']['hash'],
                         client_id=conf['api']['client_id'],
                         client_secret=conf['api']['client_secret'], )
    return client


def setup_user_channels_and_player():
    client = setup_client()

    user_info_response = client.get_user_data()
    user_info_response_body = json.loads(user_info_response.text)
    _user_id = user_info_response_body['pk']

    channels_response = client.get_channels()
    channels_response_body = json.loads(channels_response.text)
    _user_channels = channels_response_body['channels']
    _player = AudioPlayer(client)

    return _user_channels, _player, _user_id, client


def main():
    global user_channels, player, user_id

    user_channels, player, user_id, client = setup_user_channels_and_player()

    volume_up_btn = Button(RIGHT_BLACK_BTN_ID)
    volume_up_btn.when_pressed = button_action('press.volume-up', player.volume_up, client)

    volume_down_btn = Button(LEFT_BLACK_BTN_ID)
    volume_down_btn.when_pressed = button_action('press.volume-down', player.volume_down, client)

    next_btn = Button(BIG_RED_BTN_ID)
    next_btn.when_pressed = button_action('press.next-button', player.next_command, client)

    emergency_btn = Button(SMALL_RED_BTN_ID)
    emergency_btn.when_pressed = button_action('press.emergency-button', make_urgency_call, client)

    Thread(target=setup_realtime_update).start()
    Gtk.main()

    return volume_up_btn, volume_down_btn, next_btn, emergency_btn


if __name__ == '__main__':
    main()
