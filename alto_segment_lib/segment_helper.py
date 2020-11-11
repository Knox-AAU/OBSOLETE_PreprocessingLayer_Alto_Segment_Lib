import statistics

from alto_segment_lib.segment import Segment


class SegmentHelper:
    def __init__(self):
        pass

    @staticmethod
    def find_line_height_median(lines):
        height = []
        for line in lines:
            height.append(line.height())
        return statistics.median(height)

    @staticmethod
    def find_line_width_median(lines):
        width = []
        for line in lines:
            width.append(line.width())
        return statistics.median(width)

    def group_lines_into_paragraph_headers(self, lines):
        paragraph = []
        header = []
        median = self.find_line_height_median(lines)
        threshold = 17

        for line in lines:
            if line.height() > median + threshold:
                header.append(line)
            else:
                paragraph.append(line)

        return header, paragraph

    def combine_lines_into_segments(self, lines):
        segment = []
        column_groups = self.group_same_column(lines)
        segment_groups = self.group_same_segment(column_groups)

        for group in segment_groups:
            if len(group) > 0:
                coords = self.make_box_around_lines(group)
                new_segment = Segment(coords)
                new_segment.lines = group
                new_segment.type = "paragraph"
                segment.append(new_segment)
        return segment

    def group_same_column(self, lines):
        previous_line = None
        temp = []
        column_groups = []
        median = self.find_line_width_median(lines) * 0.4

        lines = sorted(lines, key=lambda sorted_line: sorted_line.x1)

        for line in lines:
            if previous_line is None:
                previous_line = line
                temp = [line]
                continue
            if line.x1 - previous_line.x1 < median:
                temp.append(line)
            else:
                column_groups.append(temp)
                temp = [line]
                previous_line = line
        if len(temp) > 1:
            column_groups.append(temp)
        return column_groups

    def group_same_segment(self, column_groups):
        temp = []
        segment_groups = []

        for group in column_groups:
            group = sorted(group, key=lambda sorted_group: sorted_group.y1)
            median = self.find_line_height_median(group) * 1.05 #add a 5 % margin
            print(median)
            previous_line = None
            for line in group:
                if previous_line is None:
                    previous_line = line
                    temp = [line]
                    continue
                if line.y1 - previous_line.y2 < median:
                    temp.append(line)
                else:
                    segment_groups.append(temp)
                    temp = [line]
                previous_line = line
            if len(temp) > 1:
                segment_groups.append(temp)
                temp = []
        return segment_groups

    @staticmethod
    def make_box_around_lines(lines: list):
        if len(lines) == 0:
            return None

        box_height = 0
        box_width = 0
        pos_x = lines[0].x1
        pos_y = lines[0].y1
        coordinates = []

        # Finds width and height line and change box height and width accordingly
        for line in lines:
            line_width = line.width()

            # Find x-coordinate upper left corner
            if line.x1 < pos_x:
                pos_x = line.x1

            # Find y-coordinate upper left corner
            if line.y1 < pos_y:
                pos_y = line.y1

            # Find box height
            if line.y2 > box_height:
                box_height = line.y2

            # Find box width
            if line_width > box_width:
                box_width = line_width

        coordinates.append(pos_x)
        coordinates.append(pos_y)
        coordinates.append(pos_x + box_width)
        coordinates.append(box_height)

        return coordinates
