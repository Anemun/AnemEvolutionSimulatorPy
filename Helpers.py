def isCoordsInRect(coords: tuple, rect: tuple) -> bool:
    if rect[0] <= coords[0] <= rect[0] + rect[2] and \
       rect[1] <= coords[1] <= rect[1] + rect[3]:
        return True
    else:
        return False


def clampValue(val, minVal, maxVal):
    if val < minVal:
        return minVal
    elif val > maxVal:
        return maxVal
    else:
        return val


def loopValue(val, minVal, maxVal):
    if val < minVal:
        val = maxVal + val - minVal + 1
    if val > maxVal:
        val = val - (maxVal-minVal+1)
    return val


class Test(object):
    def __init__(self):
        self._x = [3] * 5

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value+1
