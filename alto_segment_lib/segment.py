import math


class Segment:
    type: str
    x1: int
    y1: int
    x2: int
    y2: int
    lines: list

    def __init__(self, coord: list = None, seg_type: str = "unknown"):
        self.lines = []

        if coord is None:
            coord = []

        if len(coord) == 4:
            self.x1 = coord[0]
            self.y1 = coord[1]
            self.x2 = coord[2]
            self.y2 = coord[3]

        self.type = seg_type

    def compare(self, segment):
        if not isinstance(segment, Segment):
            return False
        return (self.x1 == segment.x1 and self.y1 == segment.y1
                and self.x2 == segment.x2 and self.y2 == segment.y2)

    def between_x_coords(self, coord: int, margin: float = 0.0):
        return (self.x1 * (1 - margin)) <= coord <= (self.x2 * (1 + margin))

    def between_y_coords(self, coord: int, margin: int = 0):
        return (self.y1 * (1 - margin)) <= coord <= (self.y2 * (1 + margin))

    def width(self):
        return self.x2 - self.x1

    def height(self):
        return self.y2 - self.y1


class Line:
    x1: int
    y1: int
    x2: int
    y2: int

    def __init__(self, coord: list = None):
        if coord is None:
            coord = []

        if len(coord) == 4:
            self.x1 = coord[0]
            self.y1 = coord[1]
            self.x2 = coord[2]
            self.y2 = coord[3]

    def width(self):
        return self.x2 - self.x1

    def height(self):
        return self.y2 - self.y1

    def is_box_horizontal(self):
        if (self.x2 - self.x1) > (self.y2 - self.y1):
            return True
