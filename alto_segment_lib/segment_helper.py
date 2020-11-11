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
        median = self.find_line_width_median(lines) * 0.4 # Add a 40 % margin

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
        if len(temp) > 0:
            column_groups.append(temp)
        return column_groups

    def group_same_segment(self, column_groups):
        temp = []
        segment_groups = []

        for group in column_groups:
            group = sorted(group, key=lambda sorted_group: sorted_group.y1)
            median = self.find_line_height_median(group)
            previous_line = None
            for line in group:
                if previous_line is None:
                    previous_line = line
                    temp = [line]
                    continue

                line_diff = line.width() - previous_line.width()
                max_diff = 100

                if line.y1 - previous_line.y2 < median and line_diff in range(-max_diff, max_diff):
                    temp.append(line)
                else:
                    segment_groups.append(temp)
                    temp = [line]
                previous_line = line
            if len(temp) > 0:
                segment_groups.append(temp)
                temp = []
        return segment_groups

    @staticmethod
    def make_box_around_lines(lines: list):
        if len(lines) == 0:
            return None

        x1 = lines[0].x1
        x2 = lines[0].x2
        y1 = lines[0].y1
        y2 = lines[0].y2
        coordinates = []

        # Finds width and height line and change box height and width accordingly
        for line in lines:
            # Find x-coordinate upper left corner
            if line.x1 < x1:
                x1 = line.x1

            # Find x-coordinate lower right corner
            if line.x2 > x2:
                x2 = line.x2

            # Find y-coordinate upper left corner
            if line.y1 < y1:
                y1 = line.y1

            # Find y-coordinate lower right corner
            if line.y2 > y2:
                y2 = line.y2

        coordinates.append(x1)
        coordinates.append(y1)
        coordinates.append(x2)
        coordinates.append(y2)

        return coordinates
