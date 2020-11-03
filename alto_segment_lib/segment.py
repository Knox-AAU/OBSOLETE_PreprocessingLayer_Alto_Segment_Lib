
class Segment:
    type: str
    pos_x: int
    pos_y: int
    lower_x: int
    lower_y: int
    lines: list

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

    def between_x_coords(self, coord: int, margin: float = 0.0):
        return (self.pos_x*(1-margin)) <= coord <= (self.lower_x*(1+margin))

    def __init__(self, type_, top_x, top_y, bot_x, bot_y):
        self.type = type_
        self.pos_x = top_x
        self.pos_y = top_y
        self.lower_x = bot_x
        self.lower_y = bot_y

    def __init__(self):
        pass

    def between_y_coords(self, coord: int, margin: int = 0):
        return (self.pos_y*(1-margin)) <= coord <= (self.lower_y*(1+margin))

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

    def __init__(self, x: int, y: int, x2: int, y2: int):
        self.pos_x = x
        self.pos_y = y
        self.lower_x = x2
        self.lower_y = y2