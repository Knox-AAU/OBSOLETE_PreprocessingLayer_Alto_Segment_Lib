import math


class Line:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.length = math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1), 2))

    @classmethod
    def from_array(cls, array):
        return Line(array[0],array[1],array[2],array[3])

    def get_orientation(self):
        '''get orientation of a line, using its length
        https://en.wikipedia.org/wiki/Atan2
        '''
        orientation = math.atan2(abs((self.x1 - self.x2)), abs((self.y1 - self.y2)))
        return math.degrees(orientation)