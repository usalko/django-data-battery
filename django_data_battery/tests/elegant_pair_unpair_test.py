from unittest import TestCase
from math import sqrt, floor


def _elegant_pair(x, y):
    '''
    function elegantPair(x, y) {
        return (x >= y) ? (x * x + x + y) : (y * y + x);
    }
    '''
    return x * x + x + y if x >= y else y * y + x


def _elegant_unpair(z):
    '''
    function elegantUnpair(z) {
        var sqrtz = Math.floor(Math.sqrt(z)),
            sqz = sqrtz * sqrtz;
        return ((z - sqz) >= sqrtz) ? [sqrtz, z - sqz - sqrtz] : [z - sqz, sqrtz];
    }
    '''
    sqrtz = int(floor(sqrt(z)))
    sqz = sqrtz * sqrtz
    if (z - sqz) >= sqrtz:
        return (sqrtz, z - sqz - sqrtz)
    else:
        return (z - sqz, sqrtz)


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
