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
