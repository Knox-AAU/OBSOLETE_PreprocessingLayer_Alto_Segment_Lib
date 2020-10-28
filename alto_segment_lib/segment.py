
class Segment:
    type: str
    pos_x: int
    pos_y: int
    lower_x: int
    lower_y: int
    lines: list = []

    def compare(self, segment):
        if not isinstance(segment, Segment):
            return False
        return (self.pos_x == segment.pos_x and self.pos_y == segment.pos_y
                and self.lower_x == segment.lower_x and self.lower_y == segment.lower_y)

    def __init__(self, type_, top_x, top_y, bot_x, bot_y):
        self.type = type_
        self.pos_x = top_x
        self.pos_y = top_y
        self.lower_x = bot_x
        self.lower_y = bot_y

    def __init__(self):
        pass


class Line:
    pos_x: int
    pos_y: int
    lower_x: int
    lower_y: int

    def __init__(self, x: int, y: int, x2: int, y2: int):
        self.pos_x = x
        self.pos_y = y
        self.lower_x = x2
        self.lower_y = y2