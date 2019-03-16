import json
import pytz
from datetime import datetime, timedelta
from typing import Optional, Union


def _now():
    return datetime.now(pytz.utc)


class DatetimeSerializer:
    DT_FORMAT = '%Y-%m-%d %H:%M:%S.%f%z'

    @classmethod
    def export(cls, dt: Optional[datetime]):
        return dt.strftime(cls.DT_FORMAT) if dt else None

    @classmethod
    def import_(cls, dt_str: Optional[str]):
        return datetime.strptime(dt_str, cls.DT_FORMAT) if dt_str else None


class TimedeltaSerializer:
    @classmethod
    def export(cls, td: Union[timedelta, str]):
        if isinstance(td, str):
            return td
        return int(td.total_seconds())

    @classmethod
    def import_(cls, td_str: Union[str, int]) -> Union[timedelta, str]:
        if isinstance(td_str, str):
            return td_str
        return timedelta(seconds=td_str)


class DeliveryRule:
    DEFAULT_CONTENT_TTL = 604800  # one week in seconds

    FREQUENCY_ONE_TIME = 'one-time'

    def __init__(self, start: Optional[datetime] = None, end: Optional[datetime] = None,
                 frequency: Optional[timedelta] = None):
        self.start = start if start else _now()
        ttl = timedelta(seconds=self.DEFAULT_CONTENT_TTL)
        self.end = end if end else self.start + ttl

        self.frequency = frequency if frequency else self.FREQUENCY_ONE_TIME

        assert self.start.tzinfo is not None, (
            "`start` must be timezone aware (non-naive)."
        )

        assert self.end.tzinfo is not None, (
            "`end` must be timezone aware (non-naive)."
        )

        assert self.start < self.end, (
            "`start` must be before `end`"
        )

    def is_alive(self, time: Optional[datetime] = None):
        """
        For a given time check if the time start-end interval is alive.
        The interval may be in the future, it is assumed to be alive in this case, too

        :param time:
        :return: bool
        """
        time = time if time else _now()
        return time < self.end

    def is_expired(self, time: Optional[datetime] = None):
        """
        For a given time check if the time interval is expired.
        This function exists although `is_alive` function exists
        for the sake of avoiding natural language confusions,
        e.g. double negation is hard to understand when said "not is_expired"

        :param time:
        :return: bool
        """
        return not self.is_alive(time)

    def in_interval(self, time: Optional[datetime] = None):
        time = time if time else _now()
        return self.start <= time <= self.end

    def is_deliverable(self, num_times_played_before, previously_played: Optional[datetime] = None,
                       time: Optional[datetime] = None):

        if num_times_played_before > 0:
            assert previously_played is not None, (
                "If num_times_played_before is greater than 0 "
                "`is_deliverable` requires `previously_played` to be set to a datetime (not None)"
            )

        time = time if time else _now()

        if not self.in_interval(time):
            return False

        if num_times_played_before == 0:
            return True

        if self.frequency == self.FREQUENCY_ONE_TIME:
            return False

        return (previously_played + self.frequency) <= time

    def export(self) -> str:
        data = {
            'start': DatetimeSerializer.export(self.start),
            'end': DatetimeSerializer.export(self.end),
            'frequency': TimedeltaSerializer.export(self.frequency),
        }

        return json.dumps(data)

    @staticmethod
    def import_(rule_str: str) -> 'DeliveryRule':
        rule_dict = json.loads(rule_str)

        start = DatetimeSerializer.import_(rule_dict['start'])
        end = DatetimeSerializer.import_(rule_dict['end'])
        frequency = TimedeltaSerializer.import_(rule_dict['frequency'])

        return DeliveryRule(start=start, end=end, frequency=frequency)


class InjectableContent:
    def __init__(self, *, audio_url, **kwargs):
        self._audio_url = audio_url

        self._jingle_url = kwargs.get('jingle_url')

        rule = kwargs.get('delivery_rule')

        if rule:
            assert (kwargs.get('start') is None) and (kwargs.get('end') is None) \
                   and (kwargs.get('frequency') is None), (
                "When `delivery_rule` is provided, `start`, `end` and `frequency` cannot be specified."
            )

        self._delivery_rule = rule if rule else DeliveryRule(start=kwargs.get('start'), end=kwargs.get('end'),
                                                             frequency=kwargs.get('frequency'))

        self._previously_played = kwargs.get('previously_played')
        self._num_times_played = kwargs.get('num_times_played', 0)

    def mark_delivery(self, time: Optional[datetime] = None):
        time = time if time else _now()
        self._previously_played = time
        self._num_times_played += 1

    def __getattr__(self, item):
        if item.startswith('_'):
            raise AttributeError("No attribute starting with underscore is exposed")

        key_name = "_{item}".format(item=item)

        if not hasattr(self, key_name):
            raise AttributeError("No attribute '{}' is available".format(item))

        return getattr(self, key_name)

    def export(self) -> str:
        data = {
            'audio_url': self.audio_url,
            'jingle_url': self.jingle_url,
            'delivery_rule': self.delivery_rule.export(),
            'previously_played': DatetimeSerializer.export(self.previously_played),
            'num_times_played': self.num_times_played,
        }
        return json.dumps(data)

    @staticmethod
    def import_(content_str: str) -> 'InjectableContent':
        content_dict = json.loads(content_str)

        delivery_rule = DeliveryRule.import_(content_dict.get('delivery_rule'))

        previously_played = DatetimeSerializer.import_(content_dict.get('previously_played', None))

        num_times_played = content_dict.get('num_times_played', 0)

        return InjectableContent(audio_url=content_dict.get('audio_url'),
                                 jingle_url=content_dict.get('jingle_url'),
                                 delivery_rule=delivery_rule,
                                 previously_played=previously_played,
                                 num_times_played=num_times_played)
