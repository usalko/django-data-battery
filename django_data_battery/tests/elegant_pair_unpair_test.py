from unittest import TestCase
from django_data_battery.utils.useful_tools import _elegant_pair, _elegant_unpair



class ElegantPairUnpairTest(TestCase):

    def test_pair_default(self):

        x = 1
        y = 2
        self.assertEqual(_elegant_pair(x, y), 5)

    def test_pair_unpair_case1(self):
        x = 1
        y = 2

        z = _elegant_pair(x, y)
        print(z)

        x_after, y_after = _elegant_unpair(z)
        self.assertEqual(x, x_after)
        self.assertEqual(y, y_after)

    def test_pair_unpair_case2(self):
        x = 2
        y = 1

        z = _elegant_pair(x, y)

        x_after, y_after = _elegant_unpair(z)
        self.assertEqual(x, x_after)
        self.assertEqual(y, y_after)
