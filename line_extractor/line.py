import math


class Line:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.length = math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1), 2))
        self.orientation = self.get_orientation()


    @classmethod
    def from_array(cls, array):
        return Line(array[0],array[1],array[2],array[3])

    def get_orientation(self):
        '''get orientation of a line, using its length
        https://en.wikipedia.org/wiki/Atan2
        '''
        orientation = math.atan2(abs((self.x1 - self.x2)), abs((self.y1 - self.y2)))
        return math.degrees(orientation)

    def __eq__(self,other):
        return self.x1 == other.x1 and self.y1 == other.y1 and self.x2 == other.x2 and self.y2 == other.y2

    def is_horizontal(self):
        orientation = self.get_orientation()
        # if horizontal
        if 45 < orientation < 135:
            return True

    def is_horizontal_or_vertical(self):
        orientation = self.get_orientation()
        # if horizontal
        if 85 <= orientation <= 95:
            return True
        elif 0 <= orientation <= 20:
            return True

        return False
