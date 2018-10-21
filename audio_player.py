from inspect import stack as call_stack
import json
from subprocess import call as os_call
from threading import Thread

from alsaaudio import Mixer as AlsaMixer, mixers as alsa_mixers
from aiy import voicehat
from utils import deep_get

from state import State, StateStack
from list_player import ListPlayer


BTN_DEBOUNCE_TIME = 0.15
VOLUME_INCREMENT = 7
URGENT_MAIL_VOLUME_MIN = 80
VOLUME_MAX = 100
VOLUME_MIN = 15


class AudioPlayer:
    # todo: consume an API for
    # todo:     1. unheard voice_mails
    # todo:     2. urgent_mails that are not delivered in the last X amount of time

    def __init__(self, api_client, **kwargs):
        self.client = api_client
        self.token = None

        self._mixer = AlsaMixer(alsa_mixers()[0])

        processing_indicator_fn = kwargs.get('processing_indicator_fn', lambda: 0)
        processing_off_indicator_fn = kwargs.get('processing_off_indicator', lambda: 0)

        (self.main_player, self.voice_mail_player, self.urgent_mail_player, self.players) = \
            self._init_players(processing_indicator_fn, processing_off_indicator_fn)

        self.current_state = State(current_player='main', playing_state=False)  # type: State
        self.state_stack = StateStack()
        self.button = self._init_btn()

        print('AudioPlayer is ready')

    @property
    def player(self):
        player_name = self.current_player_name
        return self.players[player_name]

    @property
    def current_player_name(self):
        return self.current_state.current_player

    def save_state(self):
        print('saving state: {}'.format(self.current_state))
        self.state_stack.push(self.current_state)

    def restore_state(self):
        print('restore_state is called (callback call)')
        if self.state_stack.count < 1:
            print('nothing to restore')
            return

        self._pause()
        self.current_state = self.state_stack.pop()

        self._set_led_state()

        if self.current_state.playing_state:
            self._play()

    def button_press_what_next(self):
        print('button_press_what_next, voice-mail count: {}'.format(self.voice_mail_player.count))

        if self.voice_mail_player.count > 0 and self.player != self.voice_mail_player:
            self.save_state()
            self._pause()
            self.current_state = State(current_player='voice-mail', playing_state=False)

        self.play_pause()
        return

    def play_pause(self):
        fn = self._pause if self.current_state.playing_state else self._play
        Thread(target=fn).start()

    def urgent_mail_arrived(self, *args, **kwargs):
        print('urgent mail arrived')
        self.urgent_mail_player.add_content({'url': args[0]})

        if self.player != self.urgent_mail_player:
            self.notify()
            self.save_state()
            self._pause()
            self.current_state = State(current_player='urgent-mail', playing_state=False)
            self.set_volume_minimum(URGENT_MAIL_VOLUME_MIN)

        self._play()
        return

    def voice_mail_arrived(self, *args, **kwargs):
        self._set_led_state(voicehat.LED.BLINK)
        print('voice_mail_arrived')
        self.voice_mail_player.add_content({'url': args[0]})
        print('voice-mail count: {}'.format(self.voice_mail_player.count))
        self.notify()

    def set_volume_minimum(self, min_volume):
        current_vol, *_ = self._mixer.getvolume()
        new_vol = max(min_volume, current_vol)
        self._mixer.setvolume(new_vol)

    def volume_up(self, *args, **kwargs):
        current_vol, *_ = self._mixer.getvolume()
        new_vol = min(VOLUME_MAX, current_vol + VOLUME_INCREMENT)
        print('volume up from {} to {}'.format(current_vol, new_vol))
        self._mixer.setvolume(new_vol)

    def volume_down(self, *args, **kwargs):
        current_vol, *_ = self._mixer.getvolume()
        new_vol = max(VOLUME_MIN, current_vol - VOLUME_INCREMENT)
        print('volume down from {} to {}'.format(current_vol, new_vol))
        self._mixer.setvolume(new_vol)

    def next_command(self, *args, **kwargs):
        print('next command came... current player: {}'.format(self.current_player_name))
        if self.current_player_name != 'main':
            return

        fn = self.player.play_next if self.current_state.playing_state else self.play_pause
        fn()

    @staticmethod
    def notify():
        os_call(['aplay', './sounds/notification-doorbell.wav'])

    def _init_players(self, processing_indicator_fn, processing_off_indicator_fn):
        main_player = ListPlayer(next_item_callback=self._content_started)
        voice_mail_player = ListPlayer(list_finished_callback=self._voice_mail_all_consumed)
        urgent_mail_player = ListPlayer(list_finished_callback=self._urgent_mail_all_consumed)

        players = {
            'main': main_player,
            'voice-mail': voice_mail_player,
            'urgent-mail': urgent_mail_player,
        }

        url = self._get_first_audio_url()
        main_player.add_content({'url': url})
        return main_player, voice_mail_player, urgent_mail_player, players

    def _queue_up(self):
        # todo: Sometimes causing json decode problem, can a solution be repeated requests?
        print('{} is called'.format(call_stack()[0][3]))
        response = self.client.send_playback_nearly_finished_signal()

        try:
            res_body = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            print("This response caused error: {}\n".format(response.text))
            return -1

        directive = deep_get(res_body, 'response.directives')[0]
        assert(deep_get(directive, 'type') == 'AudioPlayer.Play')
        assert(deep_get(directive, 'playBehavior') == 'ENQUEUE')
        stream = deep_get(directive, 'audioItem.stream')
        assert(stream.get('expectedPreviousToken') == self.token)
        self.main_player.add_content({'url': stream.get('url')})
        self.token = stream.get('token')

    def _content_started(self, *args, **kwargs):
        print('_content_started is called (probably callback call)')
        self.client.send_playback_started_signal(token=self.token)
        Thread(target=self._queue_up).start()

    def _get_first_audio_url(self):
        print('{} is called'.format(call_stack()[0][3]))
        response = self.client.launch()
        res_body = json.loads(response.text)
        directive = deep_get(res_body, 'response.directives')[0]
        assert (deep_get(directive, 'type') == 'AudioPlayer.Play')
        audio_url = deep_get(directive, 'audioItem.stream.url')
        token = deep_get(directive, 'audioItem.stream.token')
        self.token = token
        return audio_url

    def _play(self):
        print('{} is called, current_player: {}'.format(call_stack()[0][3], self.current_player_name))
        self.player.play()
        self.current_state.playing_state = True
        self._set_led_state()

    def _pause(self):
        print('{} is called, current_player: {}'.format(call_stack()[0][3], self.current_player_name))
        self.current_state.playing_state = False
        if not self.player.is_playing():
            return

        self.player.pause()
        Thread(target=self.client.pause).start()
        self._set_led_state()

    def _set_led_state(self, led_state=None):
        led = voicehat.get_led()

        if led_state:
            led.set_state(led_state)
            return

        state = voicehat.LED.ON if self.current_state.playing_state else voicehat.LED.OFF
        led.set_state(state)

    def _init_btn(self):
        play_btn = voicehat.get_button()
        play_btn.debounce_time = BTN_DEBOUNCE_TIME
        play_btn.on_press(self.button_press_what_next)
        self._set_led_state()
        return play_btn

    def _voice_mail_all_consumed(self, *args, **kwargs):
        print('all voice mail consumed!!')
        self.voice_mail_player.clean_playlist()
        self.restore_state()

    def _urgent_mail_all_consumed(self, *args, **kwargs):
        print('all urgent mail consumed!!')
        self.urgent_mail_player.clean_playlist()
        self.restore_state()
