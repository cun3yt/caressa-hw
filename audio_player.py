import json

from button import button_action
from logger import get_logger
from inspect import stack as call_stack
from state import State, StateStack
from list_player import ListPlayer, Audio
from utils import deep_get
from injectable_content.models import InjectableContent
from injectable_content.list import List as InjectableContentList
from typing import Optional
from signals import ListPlayerConsumedSignal

from conditional_imports import get_audio_player_dependencies

os_call, Thread, AlsaMixer, alsa_mixers, voicehat = get_audio_player_dependencies()


_BTN_DEBOUNCE_TIME = 0.15
_VOLUME_INCREMENT = 7
_URGENT_MAIL_VOLUME_MIN = 80
_VOLUME_MAX = 100
_VOLUME_MIN = 15

STATIC_SOUNDS_DIR = './sounds/{}'
MESSAGE_NOTIFICATION = STATIC_SOUNDS_DIR.format('message-notification.wav')
POSITIVE_FEEDBACK = STATIC_SOUNDS_DIR.format('positive-feedback.wav')
NEGATIVE_FEEDBACK = STATIC_SOUNDS_DIR.format('negative-feedback.wav')

logger = get_logger()


# todo hit API url for 1. unheard voice_mails, 2. urgent_mails that are not delivered in the last X amount of time

class AudioPlayer:
    """
    AudioPlayer is in charge of keeping track of different list players:
        * main list player
        * voice-mail list player
        * urgent-mail list player
    """
    def __init__(self, api_client, **kwargs):
        self.client = api_client
        self.token = None

        self._mixer = AlsaMixer(alsa_mixers()[0])

        (self.main_player, self.voice_mail_player, self.urgent_mail_player, self.players, self.current_state) = \
            self._init_players()

        lst = InjectableContentList(download_fn=api_client.injectable_content_download_fn,
                                    upload_fn=api_client.injectable_content_upload_fn,
                                    api_fetch_fn=api_client.injectable_content_fetch_available_content_fn)
        self.injectable_content_list = lst

        self.main_player.set_injectable_content_list(self.injectable_content_list)

        self.state_stack = StateStack()
        self.button = self._init_btn()

        logger.info("AudioPlayer is ready")

    @property
    def player(self):
        player_name = self.current_player_name
        return self.players[player_name]

    @property
    def current_player_name(self):
        return self.current_state.current_player

    def save_state(self):
        logger.info("saving state: {}".format(self.current_state))
        self.state_stack.push(self.current_state)

    def restore_state(self):
        logger.info("restore_state is called (callback call)")

        if self.state_stack.count < 1:
            logger.info("nothing to restore")
            return

        self._pause()
        self.current_state = self.state_stack.pop()     # type: State

        self._set_led_state()

        if self.current_state.playing_state:
            self._play()

    def button_press_on_off(self):
        """
        Purpose: Main Button Handler
        """

        logger.info("button_press_on_off, voice-mail count: {}".format(self.voice_mail_player.count))

        if self.voice_mail_player.count > 0 and self.player != self.voice_mail_player:
            logger.info("delivering voice-mail")
            self.save_state()
            self._pause()
            audio = self.voice_mail_player.check_upcoming_content()
            self.current_state = State(current_player='voice-mail', playing_state=False, audio=audio)

        fn = self.play_pause()
        return {'command': 'main',
                'player': self.current_player_name,
                'result': "fn-call.{}".format(getattr(fn, '__name__', fn))}

    def play_pause(self, *args, **kwargs):
        fn = self._pause if self.current_state.playing_state else self._play
        Thread(target=fn).start()
        return fn

    def injectable_content_arrived(self, *args, **kwargs):
        data = args[0]
        url, start, end, hash_ = data.get('url'), data.get('start'), data.get('end'), data.get('hash')

        content = InjectableContent(audio_url=url, hash_=hash_, start=start, end=end)
        self.injectable_content_list.add(content)

        logger.info("injectable_content arrived with hash: {}, url: {}".format(hash_, url))

    def urgent_mail_arrived(self, url, hash_, *args, **kwargs):
        logger.info("urgent mail arrived")

        audio = Audio(url=url, hash_=hash_)
        self.urgent_mail_player.add_content(audio)

        if self.player != self.urgent_mail_player:
            self.notify()
            self.save_state()
            self._pause()
            self.current_state = State(current_player='urgent-mail', playing_state=False, audio=audio)
            self.set_volume_minimum(_URGENT_MAIL_VOLUME_MIN)

        self._play()
        return

    def voice_mail_arrived(self, url, hash_, *args, **kwargs):
        self._set_led_state(voicehat.LED.BLINK)
        logger.info("voice_mail_arrived")
        self.voice_mail_player.add_content({'url': url, 'hash': hash_})
        logger.info("voice-mail count: {}".format(self.voice_mail_player.count))
        self.notify()

    def set_volume_minimum(self, min_volume):
        """
        Increase the volume to `min_volume` if `current_volume` < `min_val`
        :param min_volume:
        :return:
        """
        current_vol, *_ = self._mixer.getvolume()
        new_vol = max(min_volume, current_vol)
        self._mixer.setvolume(new_vol)

    def volume_up(self, *args, **kwargs):
        current_vol, *_ = self._mixer.getvolume()
        new_vol = min(_VOLUME_MAX, current_vol + _VOLUME_INCREMENT)
        logger.info("volume up from {} to {}".format(current_vol, new_vol))
        self._mixer.setvolume(new_vol)
        return {'command': 'volume-up', 'from': current_vol, 'to': new_vol}

    def volume_down(self, *args, **kwargs):
        current_vol, *_ = self._mixer.getvolume()
        new_vol = max(_VOLUME_MIN, current_vol - _VOLUME_INCREMENT)
        logger.info("volume down from {} to {}".format(current_vol, new_vol))
        self._mixer.setvolume(new_vol)
        return {'command': 'volume-down', 'from': current_vol, 'to': new_vol}

    def next_command(self, *args, **kwargs):
        """
        Purpose: Skip Button Handler

        todo: This function is mingled with the list-player consumption. There is a need of better handling!
        """
        result = {'command': 'next-command'}

        self._react_to_content(signal='negative')

        logger.info("next command came... current player: {}".format(self.current_player_name))
        if self.current_player_name == 'urgent-mail':
            return {**result, 'current-state': 'urgent-mail-action', 'result': 'do-nothing', }

        result = {**result, 'current-state': self.current_state.playing_state}
        fn = self.player.play_next if self.current_state.playing_state else self.play_pause

        audio = fn()    # type: Union['Audio', 'type', None]

        if audio is ListPlayerConsumedSignal:
            if self.current_player_name == 'voice-mail':    # todo move string literals to constants
                self._voice_mail_all_consumed()
            else:   # pragma: no cover
                assert self.current_player_name == 'main', (
                    "This point expects main player, got: %s" % self.current_player_name
                )
                error_msg = "Unexpected consumption of the main player!"
                logger.error(error_msg)
                return {**result,
                        'error': error_msg,
                        'player': self.current_player_name,
                        'result': "fn-call.{}".format(getattr(fn, '__name__', fn))}

        if isinstance(audio, Audio):
            self.current_state.set_audio(audio)

        return {**result,
                'player': self.current_player_name,
                'result': "fn-call.{}".format(getattr(fn, '__name__', fn))}

    def _react_to_content(self, signal):
        """
        Positive/Negative Button Click from User
        :return:
        """
        audio_url = self.current_state.audio_url
        audio_hash = self.current_state.audio_hash

        def fn():
            logger.info('yes_or_like_current_content: '
                        'content: {url}, hash: {hash}'.format(url=audio_url, hash=audio_hash))
            if audio_hash is None:
                logger.error("audio_hash is not set for yes/like button action, skipping it")
                return
            self.client.post_content_signal(hash_=audio_hash, signal=signal)

        self.feedback_notice(signal)
        Thread(target=fn).start()
        return fn

    def yes_command(self, *args, **kwargs):
        """
        This function is the handler for the yes button
        """

        result = {'command': "yes-command"}
        logger.info("yes command came... current player: {}".format(self.current_player_name))

        if not self.current_state.playing_state:
            fn, fn_kwargs = self.play_pause, {}
        else:
            fn, fn_kwargs = self._react_to_content, {'signal': 'positive'}
        fn(**fn_kwargs)

        return {**result,
                'player': self.current_player_name,
                'result': "fn-call.{}".format(getattr(fn, '__name__', fn))}

    def feedback_notice(self, signal):
        fn = self.positive_feedback if signal == 'positive' else self.negative_feedback
        fn()

    @staticmethod
    def notify():
        os_call(['aplay', MESSAGE_NOTIFICATION, ])

    @staticmethod
    def positive_feedback():
        os_call(['aplay', POSITIVE_FEEDBACK, ])

    @staticmethod
    def negative_feedback():
        os_call(['aplay', NEGATIVE_FEEDBACK, ])

    def _init_players(self):
        main_player = ListPlayer(next_item_callback=self._content_started)
        voice_mail_player = ListPlayer(list_finished_callback=self._voice_mail_all_consumed)
        urgent_mail_player = ListPlayer(list_finished_callback=self._urgent_mail_all_consumed)

        players = {
            'main': main_player,
            'voice-mail': voice_mail_player,
            'urgent-mail': urgent_mail_player,
        }

        audio = self._get_first_audio()
        main_player.add_content(audio)
        current_state = State(current_player='main', playing_state=False, audio=audio)  # type: State
        return main_player, voice_mail_player, urgent_mail_player, players, current_state

    def _queue_up(self):
        # todo: Sometimes causing json decode problem, can a solution be repeated requests?
        logger.info("{} is called".format(call_stack()[0][3]))
        response = self.client.send_playback_nearly_finished_signal()

        try:
            res_body = json.loads(response.text)
        except json.decoder.JSONDecodeError:    # pragma: no cover
            logger.info("This response caused error: {}\n".format(response.text))
            return -1

        directive = deep_get(res_body, 'response.directives')[0]
        assert(deep_get(directive, 'type') == 'AudioPlayer.Play')
        assert(deep_get(directive, 'playBehavior') == 'ENQUEUE')
        stream = deep_get(directive, 'audioItem.stream')

        self.main_player.add_content({'url': stream.get('url'), 'hash': stream.get('hash')})
        self.token = stream.get('token')

    def _content_started(self, *args, **kwargs):
        logger.info("_content_started is called (probably callback call)")
        self.client.send_playback_started_signal(token=self.token)
        Thread(target=self._queue_up).start()

    def _get_first_audio(self) -> Audio:
        logger.info("{} is called".format(call_stack()[0][3]))
        response = self.client.launch()
        res_body = json.loads(response.text)
        directive = deep_get(res_body, 'response.directives')[0]
        assert (deep_get(directive, 'type') == 'AudioPlayer.Play')
        audio_url = deep_get(directive, 'audioItem.stream.url')
        audio_hash = deep_get(directive, 'audioItem.stream.hash')
        token = deep_get(directive, 'audioItem.stream.token')
        self.token = token
        return Audio(url=audio_url, hash_=audio_hash)

    def _play(self):
        logger.info("{} is called, current_player: {}".format(call_stack()[0][3], self.current_player_name))
        audio = self.player.play()
        if audio is not None:
            self.current_state.set_audio(audio)
        self.current_state.playing_state = True
        self._set_led_state()
        return audio

    def _pause(self):
        logger.info("{} is called, current_player: {}".format(call_stack()[0][3], self.current_player_name))
        self.current_state.playing_state = False

        if not self.player.is_playing():
            return

        self.player.pause()
        Thread(target=self.client.pause).start()
        self._set_led_state()
        return 0

    def _set_led_state(self, led_state=None):
        led = voicehat.get_led()

        if self.voice_mail_player.count > 0:
            led.set_state(voicehat.LED.BLINK)
            return

        if led_state:
            led.set_state(led_state)
            return

        state = voicehat.LED.ON if self.current_state.playing_state else voicehat.LED.OFF
        led.set_state(state)

    def _init_btn(self):
        play_btn = voicehat.get_button()
        play_btn.debounce_time = _BTN_DEBOUNCE_TIME
        play_btn.on_press(button_action('press.main-button', self.button_press_on_off, self.client))
        self._set_led_state()
        return play_btn

    def _voice_mail_all_consumed(self, *args, **kwargs):    # pragma: no cover
        # callbacks for list_player
        logger.info("all voice mail consumed!!")
        self.voice_mail_player.clean_playlist()
        self.restore_state()

    def _urgent_mail_all_consumed(self, *args, **kwargs):   # pragma: no cover
        # callbacks for list_player
        logger.info("all urgent mail consumed!!")
        self.urgent_mail_player.clean_playlist()
        self.restore_state()
