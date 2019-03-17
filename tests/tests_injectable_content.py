import pytz
import unittest
from injectable_content.models import DatetimeSerializer, TimedeltaSerializer, DeliveryRule, InjectableContent
from injectable_content.list import List
from datetime import datetime, timedelta, timezone


class TestDatetimeSerializer(unittest.TestCase):
    def test_export(self):
        dt = datetime(2019, 3, 16, 5, 2, 52, 931285, tzinfo=pytz.utc)
        exported = DatetimeSerializer.export(dt)
        self.assertEqual(exported, '2019-03-16 05:02:52.931285+0000')

    def test_import(self):
        str_dt = '2019-03-16 05:02:52.931285+0000'
        dt = DatetimeSerializer.import_(str_dt)
        self.assertEqual(dt.year, 2019)
        self.assertEqual(dt.month, 3)
        self.assertEqual(dt.day, 16)
        self.assertEqual(dt.hour, 5)
        self.assertEqual(dt.minute, 2)
        self.assertEqual(dt.second, 52)
        self.assertEqual(dt.microsecond, 931285)
        self.assertEqual(dt.tzinfo, timezone.utc)

    def test_export_import(self):
        dt = datetime(2019, 3, 16, 5, 2, 52, 931285, tzinfo=pytz.utc)
        exported = DatetimeSerializer.export(dt)
        imported = DatetimeSerializer.import_(exported)
        self.assertEqual(dt, imported)


class TestTimedeltaSerializer(unittest.TestCase):
    def test_export(self):
        td = timedelta(minutes=1)
        exported = TimedeltaSerializer.export(td)
        self.assertEqual(exported, 60)

    def test_export_one_time(self):
        td = DeliveryRule.FREQUENCY_ONE_TIME
        exported = TimedeltaSerializer.export(td)
        self.assertEqual(exported, 'one-time')

    def test_import(self):
        td = TimedeltaSerializer.import_(65)
        self.assertIsInstance(td, timedelta)
        self.assertEqual(td.total_seconds(), 65)

    def test_import_one_time(self):
        td = TimedeltaSerializer.import_('one-time')
        self.assertEqual(td, DeliveryRule.FREQUENCY_ONE_TIME)


class TestDeliveryRuleSetup(unittest.TestCase):
    def test_defaults_are_set(self):
        rule = DeliveryRule()
        self.assertIsInstance(rule.start, datetime)
        self.assertIsInstance(rule.end, datetime)
        self.assertEqual(rule.frequency, DeliveryRule.FREQUENCY_ONE_TIME)

    def test_default_content_ttl(self):
        now = datetime.now(pytz.utc)
        rule = DeliveryRule(start=now + timedelta(days=1))
        interval = rule.end - rule.start
        self.assertEqual(interval.total_seconds()/(60*60*24), 7, "TTL is supposed to be 7 days")

    def test_tz_awareness(self):
        with self.assertRaises(AssertionError):
            DeliveryRule(start=datetime.now())

        with self.assertRaises(AssertionError):
            DeliveryRule(end=datetime.now())

    def test_start_is_before_end(self):
        now = datetime.now(pytz.utc)
        with self.assertRaises(AssertionError):
            DeliveryRule(start=now+timedelta(days=1), end=now)

    def test_setting_frequency(self):
        rule = DeliveryRule(frequency=timedelta(hours=1))
        self.assertIsInstance(rule.frequency, timedelta)
        self.assertEqual(rule.frequency.total_seconds()/(60*60), 1)


class TestDeliveryRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.now = datetime.now(pytz.utc)
        cls.in_interval = (cls.now-timedelta(days=1), cls.now+timedelta(days=1))
        cls.ahead_interval = (cls.now+timedelta(days=10), cls.now+timedelta(days=12))
        cls.past_interval = (cls.now-timedelta(days=12), cls.now-timedelta(days=10))

    def test_alive_in_interval(self):
        start, end = self.in_interval
        rule = DeliveryRule(start=start, end=end)
        self.assertTrue(rule.is_alive())
        self.assertFalse(rule.is_expired())

    def test_alive_ahead_interval(self):
        start, end = self.ahead_interval
        rule = DeliveryRule(start=start, end=end)
        self.assertTrue(rule.is_alive())
        self.assertFalse(rule.is_expired())

    def test_expired(self):
        start, end = self.past_interval
        rule = DeliveryRule(start=start, end=end)
        self.assertFalse(rule.is_alive())
        self.assertTrue(rule.is_expired())

    def test_in_interval(self):
        start, end = self.in_interval
        rule = DeliveryRule(start=start, end=end)
        self.assertTrue(rule.in_interval(time=self.now))

    def test_in_interval_past(self):
        start, end = self.past_interval
        rule = DeliveryRule(start=start, end=end)
        self.assertFalse(rule.in_interval(time=self.now))

    def test_in_interval_ahead(self):
        start, end = self.ahead_interval
        rule = DeliveryRule(start=start, end=end)
        self.assertFalse(rule.in_interval(time=self.now))

    def test_cannot_deliver_first_time_past_interval(self):
        start, end = self.past_interval
        rule = DeliveryRule(start=start, end=end)
        self.assertFalse(rule.is_deliverable(num_times_played_before=0))

    def test_cannot_deliver_first_time_in_ahead_interval(self):
        start, end = self.ahead_interval
        rule = DeliveryRule(start=start, end=end)
        self.assertFalse(rule.is_deliverable(num_times_played_before=0))

    def test_can_deliver_first_time_in_interval(self):
        start, end = self.in_interval
        rule = DeliveryRule(start=start, end=end)
        self.assertTrue(rule.is_deliverable(num_times_played_before=0))

    def test_cannot_deliver_once_deliverable_twice(self):
        start, end = self.in_interval
        rule = DeliveryRule(start=start, end=end, frequency=DeliveryRule.FREQUENCY_ONE_TIME)
        self.assertFalse(rule.is_deliverable(num_times_played_before=1,
                                             previously_played=self.now-timedelta(hours=1)))

    def test_can_deliver_first_time_with_frequency(self):
        start, end = self.in_interval
        rule = DeliveryRule(start=start, end=end, frequency=timedelta(hours=1))
        self.assertTrue(rule.is_deliverable(num_times_played_before=0, time=self.now))

    def test_cannot_deliver_second_time_if_too_frequent(self):
        start, end = self.in_interval
        rule = DeliveryRule(start=start, end=end, frequency=timedelta(hours=1))
        self.assertFalse(rule.is_deliverable(num_times_played_before=1,
                                             previously_played=self.now-timedelta(minutes=30), time=self.now))

    def test_can_deliver_second_time_if_passed_frequency(self):
        start, end = self.in_interval
        rule = DeliveryRule(start=start, end=end, frequency=timedelta(hours=1))
        self.assertTrue(rule.is_deliverable(num_times_played_before=1,
                                            previously_played=self.now - timedelta(hours=1), time=self.now))
        self.assertTrue(rule.is_deliverable(num_times_played_before=1,
                                            previously_played=self.now - timedelta(minutes=70), time=self.now))


class TestDeliveryRuleExportImport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        start = datetime(2019, 3, 16, 5, 2, 52, 931285, tzinfo=pytz.utc)
        end = datetime(2019, 4, 2, 17, 11, 2, 801285, tzinfo=pytz.utc)
        frequency = timedelta(minutes=55)
        cls.rule1 = DeliveryRule(start=start, end=end, frequency=frequency)

        start = datetime(2019, 3, 16, 5, 2, 52, 931285, tzinfo=pytz.utc)
        end = datetime(2019, 4, 2, 17, 11, 2, 801285, tzinfo=pytz.utc)
        frequency = DeliveryRule.FREQUENCY_ONE_TIME
        cls.rule2 = DeliveryRule(start=start, end=end, frequency=frequency)

    def test_export(self):
        rule = DeliveryRule()
        exported = rule.export()
        self.assertIsInstance(exported, str)

    def test_export_import(self):
        exported = self.rule1.export()
        imported_rule = DeliveryRule.import_(exported)

        self.assertEqual(self.rule1.start, imported_rule.start)
        self.assertEqual(self.rule1.end, imported_rule.end)
        self.assertEqual(self.rule1.frequency, imported_rule.frequency)

    def test_export_import_one_time_frequency(self):
        exported = self.rule2.export()
        imported_rule = DeliveryRule.import_(exported)

        self.assertEqual(self.rule2.start, imported_rule.start)
        self.assertEqual(self.rule2.end, imported_rule.end)
        self.assertEqual(self.rule2.frequency, imported_rule.frequency)


class TestInjectableContent(unittest.TestCase):
    def test_rule_and_start_assertion(self):
        rule = DeliveryRule()
        with self.assertRaises(AssertionError):
            InjectableContent(audio_url='https://example.com/audio1.mp3',
                              delivery_rule=rule,
                              start=datetime.now())

    def test_rule_and_end_assertion(self):
        rule = DeliveryRule()
        with self.assertRaises(AssertionError):
            InjectableContent(audio_url='https://example.com/audio1.mp3',
                              delivery_rule=rule,
                              end=datetime.now()+timedelta(minutes=5))

    def test_rule_and_frequency_assertion(self):
        rule = DeliveryRule()
        with self.assertRaises(AssertionError):
            InjectableContent(audio_url='https://example.com/audio1.mp3',
                              delivery_rule=rule,
                              frequency=timedelta(minutes=2))

    def test_default_properties(self):
        content = InjectableContent(audio_url='https://example.com/audio1.mp3')
        self.assertEqual(content.audio_url, 'https://example.com/audio1.mp3')
        self.assertIsNone(content.jingle_url)
        self.assertIsInstance(content.delivery_rule, DeliveryRule)
        self.assertIsNone(content.previously_played)
        self.assertEqual(content.num_times_played, 0)

    def test_setting_delivery_rul(self):
        _rule = DeliveryRule(start=datetime(2019, 3, 16, 5, 2, 52, 931285, tzinfo=pytz.utc),
                             end=datetime(2019, 4, 2, 17, 11, 2, 801285, tzinfo=pytz.utc),
                             frequency=timedelta(minutes=5), )

        content = InjectableContent(audio_url='https://example.com/audio1.mp3', delivery_rule=_rule)
        rule = content.delivery_rule

        self.assertEqual(rule.start.month, 3)
        self.assertEqual(rule.start.day, 16)
        self.assertEqual(rule.start.hour, 5)
        self.assertEqual(rule.start.minute, 2)
        self.assertEqual(rule.end.year, 2019)
        self.assertEqual(rule.end.month, 4)
        self.assertEqual(rule.end.microsecond, 801285)
        self.assertEqual(rule.frequency.total_seconds(), 5*60)

    def test_unknown_attribute(self):
        content = InjectableContent(audio_url='https://example.com/audio1.mp3')
        with self.assertRaises(AttributeError):
            content.unknown_attribute

    def test_mark_delivery(self):
        content = InjectableContent(audio_url='https://example.com/audio1.mp3')
        now = datetime.now(pytz.utc)

        delivery_time = now-timedelta(days=1)
        content.mark_delivery(time=delivery_time)
        self.assertEqual(content.num_times_played, 1)
        self.assertEqual(content.previously_played, delivery_time)

        second_delivery_time = now
        content.mark_delivery(time=second_delivery_time)
        self.assertEqual(content.num_times_played, 2)
        self.assertEqual(content.previously_played, second_delivery_time)

    def test_expired_past(self):
        content = InjectableContent(audio_url='https://example.com/audio1.mp3',
                                    start=datetime.now(pytz.utc)-timedelta(days=5),
                                    end=datetime.now(pytz.utc)-timedelta(days=3))
        self.assertTrue(content.is_expired)
        self.assertFalse(content.is_alive)

    def test_not_expired_current(self):
        content = InjectableContent(audio_url='https://example.com/audio1.mp3',
                                    start=datetime.now(pytz.utc) - timedelta(days=2),
                                    end=datetime.now(pytz.utc) + timedelta(days=2))
        self.assertFalse(content.is_expired)
        self.assertTrue(content.is_alive)

    def test_not_expired_upcoming(self):
        content = InjectableContent(audio_url='https://example.com/audio1.mp3',
                                    start=datetime.now(pytz.utc) + timedelta(days=2),
                                    end=datetime.now(pytz.utc) + timedelta(days=4))
        self.assertFalse(content.is_expired)
        self.assertTrue(content.is_alive)

    def test_not_deliverable_past(self):
        content = InjectableContent(audio_url='https://example.com/audio1.mp3',
                                    start=datetime.now(pytz.utc) - timedelta(days=5),
                                    end=datetime.now(pytz.utc) - timedelta(days=3))
        self.assertFalse(content.is_deliverable)

    def test_deliverable_current(self):
        content = InjectableContent(audio_url='https://example.com/audio1.mp3',
                                    start=datetime.now(pytz.utc) - timedelta(days=2),
                                    end=datetime.now(pytz.utc) + timedelta(days=2))
        self.assertTrue(content.is_deliverable)

    def test_not_deliverable_upcoming(self):
        content = InjectableContent(audio_url='https://example.com/audio1.mp3',
                                    start=datetime.now(pytz.utc) + timedelta(days=2),
                                    end=datetime.now(pytz.utc) + timedelta(days=4))
        self.assertFalse(content.is_deliverable)


class TestInjectableExportImport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content1 = InjectableContent(audio_url='https://example.com/audio1.mp3',
                                         jingle_url='https://example.com/jingle1.mp3',
                                         start=datetime(2019, 3, 16, 5, 2, 52, 931285, tzinfo=pytz.utc),
                                         end=datetime(2019, 4, 2, 17, 11, 2, 801285, tzinfo=pytz.utc),
                                         frequency=DeliveryRule.FREQUENCY_ONE_TIME, )
        cls.content2 = InjectableContent(audio_url='https://example.com/audio2.mp3',
                                         start=datetime(2019, 2, 16, 5, 2, 52, 931285, tzinfo=pytz.utc),
                                         end=datetime(2019, 7, 2, 17, 11, 2, 801285, tzinfo=pytz.utc),
                                         frequency=timedelta(minutes=5),
                                         previously_played=datetime(2019, 2, 17, 5, 2, 52, 123456, tzinfo=pytz.utc),
                                         num_times_played=12, )

    def test_export_content1(self):
        exported = self.content1.export()
        content = InjectableContent.import_(exported)
        self.assertEqual(content.audio_url, 'https://example.com/audio1.mp3')
        self.assertEqual(content.jingle_url, 'https://example.com/jingle1.mp3')

        self.assertEqual(content.delivery_rule.start.month, 3)
        self.assertEqual(content.delivery_rule.start.day, 16)
        self.assertEqual(content.delivery_rule.start.minute, 2)

        self.assertEqual(content.delivery_rule.end.year, 2019)
        self.assertEqual(content.delivery_rule.end.month, 4)
        self.assertEqual(content.delivery_rule.end.microsecond, 801285)

        self.assertEqual(content.delivery_rule.frequency, 'one-time')
        self.assertEqual(content.previously_played, None)

        self.assertEqual(content.num_times_played, 0)

    def test_export_content2(self):
        exported = self.content2.export()
        content = InjectableContent.import_(exported)

        self.assertEqual(content.audio_url, 'https://example.com/audio2.mp3')
        self.assertIsNone(content.jingle_url)

        self.assertEqual(content.delivery_rule.start.month, 2)
        self.assertEqual(content.delivery_rule.start.day, 16)
        self.assertEqual(content.delivery_rule.start.hour, 5)
        self.assertEqual(content.delivery_rule.start.minute, 2)
        self.assertEqual(content.delivery_rule.start.second, 52)
        self.assertEqual(content.delivery_rule.start.microsecond, 931285)

        self.assertEqual(content.delivery_rule.end.month, 7)
        self.assertEqual(content.delivery_rule.end.day, 2)
        self.assertEqual(content.delivery_rule.end.hour, 17)
        self.assertEqual(content.delivery_rule.end.minute, 11)
        self.assertEqual(content.delivery_rule.end.second, 2)
        self.assertEqual(content.delivery_rule.end.microsecond, 801285)

        self.assertEqual(content.delivery_rule.frequency.total_seconds(), 300)
        self.assertEqual(content.previously_played.day, 17)
        self.assertEqual(content.previously_played.microsecond, 123456)
        self.assertEqual(content.num_times_played, 12)


class TestList(unittest.TestCase):
    def setUp(self):
        self.lst = List()
        self.now = datetime.now(pytz.utc)
        self.one_day = timedelta(days=1)
        self.two_day = timedelta(days=2)

        self.content_current = InjectableContent(audio_url='https://example.com/audio1.mp3',
                                                 start=self.now - self.one_day, end=self.now + self.one_day)
        self.content_past = InjectableContent(audio_url='https://example.com/audio2.mp3',
                                              start=self.now - self.two_day, end=self.now - self.one_day)
        self.content_upcoming = InjectableContent(audio_url='https://example.com/audio3.mp3',
                                                  start=self.now + self.one_day, end=self.now + self.two_day)

    def test_list_add(self):
        self.assertEqual(len(self.lst), 0)

        content = InjectableContent(audio_url='https://example.com/audio1.mp3')
        self.lst.add(content)
        self.assertEqual(len(self.lst), 1)

    def test_collect_garbage(self):
        self.lst.add(self.content_current)
        self.lst.add(self.content_past)
        self.lst.add(self.content_upcoming)

        self.assertEqual(len(self.lst), 3)

        self.lst.collect_garbage()
        self.assertEqual(len(self.lst), 2)
        audio_urls = set(content.audio_url for content in self.lst.set())
        self.assertEqual(audio_urls, {'https://example.com/audio1.mp3', 'https://example.com/audio3.mp3'})

    def test_deliverables(self):
        self.lst.add(self.content_current)
        self.lst.add(self.content_past)
        self.lst.add(self.content_upcoming)
        self.assertEqual(len(self.lst), 3)

        deliverables = self.lst.deliverables()

        self.assertEqual(len(deliverables), 1)
        self.assertEqual(deliverables[0].audio_url, 'https://example.com/audio1.mp3')

    def test_export_import(self):
        self.lst.add(self.content_current)
        self.lst.add(self.content_past)

        lst_exported = self.lst.export()
        lst_imported = List.import_(lst_exported)

        self.assertEqual(len(lst_imported), 2)
        audio_urls = set(content.audio_url for content in lst_imported.set())
        self.assertEqual(audio_urls, {'https://example.com/audio1.mp3', 'https://example.com/audio2.mp3'})
