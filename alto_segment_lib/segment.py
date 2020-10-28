
class Segment:
    type: str
    pos_x: int
    pos_y: int
    lower_x: int
    lower_y: int
    lines: list = []

    def __init__(self, coord: list = None, seg_type: str = ""):
        self.lines = []

        if coord is None:
            coord = []

        if len(coord) == 4:
            self.pos_x = coord[0]
            self.pos_y = coord[1]
            self.lower_x = coord[2]
            self.lower_y = coord[3]

        self.type = seg_type

    def compare(self, segment):
        if not isinstance(segment, Segment):
            return False
        return (self.pos_x == segment.pos_x and self.pos_y == segment.pos_y
                and self.lower_x == segment.lower_x and self.lower_y == segment.lower_y)

    def between_x_coords(self, coord: int):
        return self.pos_x <= coord <= self.lower_x

    def between_y_coords(self, coord: int):
        return self.pos_y <= coord <= self.lower_y

    def width(self):
        return self.lower_x - self.pos_x

    def height(self):
        return self.lower_y - self.pos_y


class Line:
    pos_x: int
    pos_y: int
    lower_x: int
    lower_y: int

    def __init__(self, coord: list = None):
        if coord is None:
            coord = []

        if len(coord) == 4:
            self.pos_x = coord[0]
            self.pos_y = coord[1]
            self.lower_x = coord[2]
            self.lower_y = coord[3]

    def width(self):
        return self.lower_x - self.pos_x

    def height(self):
        return self.lower_y - self.pos_y