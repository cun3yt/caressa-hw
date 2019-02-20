import unittest
from utils import deep_get


class TestDeepGet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dict_empty = {}
        cls.dict_1x5 = {
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4,
            'e': 5,
        }
        cls.dict_2x3 = {
            'level_1_a': {
                'level_2_a': 'aa',
                'level_2_b': 'ab',
                'level_2_c': 'ac',
            },
            'level_1_b': {
                'level_2_a': 'ba',
                'level_2_b': 'bb',
                'level_2_c': 'bc',
            },
        }
        cls.dict_deep = {
            'a': {'b': {'c': {'d': {'e': {'f': {'g': {'h': 'very_deep'}}}}}}}
        }
        cls.dict_case_sensitive = {
            'abc': {
                'DeF': 'hapat',
                'def': 'zapata',
            },
            'aBC': 2,
            'AbC': 3,
        }

    def test_deep_default_value(self):
        self.assertIsNone(deep_get(self.dict_empty, 'question_mark'))
        self.assertEqual(deep_get(self.dict_empty, 'question_mark', 'n/a'), 'n/a')

        self.assertIsNone(deep_get(self.dict_empty, 'a.b.c.d'))
        self.assertEqual(deep_get(self.dict_empty, 'a.b.c.d', 1234), 1234)

        self.assertIsNone(deep_get(self.dict_1x5, 'a.b.c.d'))
        self.assertEqual(deep_get(self.dict_1x5, 'a.b.c.d', 1234), 1234)

        self.assertIsNone(deep_get(self.dict_1x5, 'z'))
        self.assertEqual(deep_get(self.dict_1x5, 'z', 1234), 1234)

        self.assertIsNone(deep_get(self.dict_2x3, 'level_1_a.xyz'))
        self.assertEqual(deep_get(self.dict_2x3, 'level_1_a.xyz', 1234), 1234)

        self.assertIsNone(deep_get(self.dict_2x3, 'xyz.level_2_a'))
        self.assertEqual(deep_get(self.dict_2x3, 'xyz.level_2_a', 1234), 1234)

        self.assertIsNone(deep_get(self.dict_2x3, 'level_1_a.level_2_a.level3'))
        self.assertEqual(deep_get(self.dict_2x3, 'level_1_a.level_2_a.level3', 1234), 1234)

        self.assertIsNone(deep_get(self.dict_2x3, 'level_1_X'))
        self.assertEqual(deep_get(self.dict_2x3, 'level_1_X', 1234), 1234)

    def test_level_1(self):
        self.assertEqual(deep_get(self.dict_1x5, 'a'), 1)
        self.assertEqual(deep_get(self.dict_2x3, 'level_1_a'), {
            'level_2_a': 'aa',
            'level_2_b': 'ab',
            'level_2_c': 'ac',
        })

    def test_level_2(self):
        self.assertEqual(deep_get(self.dict_2x3, 'level_1_a.level_2_a'), 'aa')
        self.assertEqual(deep_get(self.dict_2x3, 'level_1_a.level_2_b'), 'ab')
        self.assertEqual(deep_get(self.dict_2x3, 'level_1_b.level_2_c'), 'bc')
        self.assertEqual(deep_get(self.dict_2x3, 'level_1_b.level_2_a'), 'ba')

    def test_very_deep(self):
        self.assertEqual(deep_get(self.dict_deep, 'a.b.c.d.e.f.g.h'), 'very_deep')
        self.assertEqual(deep_get(self.dict_deep, 'a.b.c.d.e.f.g'), {'h': 'very_deep'})
        self.assertIsNone(deep_get(self.dict_deep, 'a.b.c.d.e.f.g.h.i.j.k'))
        self.assertIsNone(deep_get(self.dict_deep, 'a.b.c.d.e.f.g.h.i'))
        self.assertIsNone(deep_get(self.dict_deep, 'a.b.c.d.e.f.XX'))

    def test_case_sensitive(self):
        self.assertIsNone(deep_get(self.dict_case_sensitive, 'ABC'))
        self.assertIsNone(deep_get(self.dict_case_sensitive, 'abc.dEF'))
        self.assertEqual(deep_get(self.dict_case_sensitive, 'abc.DeF'), 'hapat')
        self.assertEqual(deep_get(self.dict_case_sensitive, 'AbC'), 3)
        self.assertEqual(deep_get(self.dict_case_sensitive, 'abc'), {
            'DeF': 'hapat',
            'def': 'zapata',
        })
