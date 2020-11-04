from alto_segment_lib.segment import Segment
from line_extractor.extractor import LineExtractor
import statistics


def add_segment(segments: list, coordinates: list, lines, seg_type: str):
    segment = Segment(coordinates)
    segment.lines = lines
    segment.type = seg_type
    segments.append(segment)


class RepairSegments:
    __segments: list
    __new_segments: list = []
    __lines: list = []
    __median_paragraph_width: float
    __threshold: int

    def __init__(self, segments, lines, threshold: int = 10):
        self.__segments = segments
        self.__threshold = threshold
        self.__lines = lines
        self.__new_segments = []
        self.__median_paragraph_width
        self.__analyze_coordinates()

    def __analyze_coordinates(self):
        all_para = []
        for segment in self.__segments:
            all_para.append(segment.x2 - segment.x1)
        self.__median_paragraph_width = statistics.median(all_para)

    def __need_repair(self, segment: Segment):
        seg_width = segment.x2 - segment.x1
        min_width = self.__median_paragraph_width - self.__threshold
        max_width = self.__median_paragraph_width + self.__threshold

        if seg_width > max_width and does_line_overlap_segment(segment):
            return True
        return False

    def does_line_overlap_segment(self, segment):
        for line in self.__lines:
            #xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
            xdiff = (line.x1 - line.x2, segment.x1 - segment.x2)
            #ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])
            ydiff = (line.y1 - line.y2, segment.y1 - segment.y2)

            def det(a, b):
                return a[0] * b[1] - a[1] * b[0]

            div = det(xdiff, ydiff)
            if div == 0:
               raise Exception('lines do not intersect')

            d = (det(*line1), det(*line2))
            x = det(d, xdiff) / div
            y = det(d, ydiff) / div
            return x, y

    def repair_columns(self):
        for segment in self.__segments:
            if self.__need_repair(segment):
                cur_seg_width = (segment.x2 - segment.x1)
                segment.x2 = segment.x1 + (cur_seg_width / 2) - 5

                # Make segment
                coords = [segment.x1 + (cur_seg_width / 2) + 5, segment.y1, segment.x2 + (cur_seg_width / 2), segment.y2]
                add_segment(self.__segments, coords, [], segment.type)

        return self.__segments.copy()

    def repair_rows(self, range_span: int = 50):
        return_segments = self.__segments.copy()

        # Iterates throupg all segments and all other segments
        for segment in self.__segments:
            for subsegment in self.__segments:
                if not segment.compare(subsegment):
                    lines = segment.lines
                    grouped_lines = []

                    # Checks if subsegment is vertically close to segment
                    if (segment.x1 - range_span) <= subsegment.x1 <= (segment.x1 + range_span):

                        # Checks if both y-coordinates for the subsegment is within the segment: remove the subsegment
                        if segment.between_y_coords(subsegment.y1) and segment.between_y_coords(subsegment.y2):
                            return_segments.remove(subsegment)
                        # Checks if  the  upper y-coordinate for subsegment is within segment: move y-coordinate to
                        # be beside segment
                        elif segment.between_y_coords(subsegment.y1):
                            subsegment.y1 = segment.y2
                        # Checks if  the  lower y-coordinate for subsegment is within segment: move y-coordinate to
                        # be beside segment
                        elif segment.between_y_coords(subsegment.y2):
                            subsegment.y2 = segment.y1

                    # hvis subsegment ligger Segment med forskellige x-koordinater: split op i mindre bokse
                    elif (segment.between_y_coords(subsegment.y1) or segment.between_y_coords(subsegment.y2)) \
                            and (segment.between_x_coords(subsegment.x1) or segment.between_x_coords(subsegment.x2)) \
                            and segment in return_segments:

                        counter: int = 0

                        print('{0}, {1}, {2}, {3}'.format(segment.x1, segment.y1, segment.x2, segment.y2))

                        while counter < (len(lines) - 1):
                            line_diff = 0.3  # minimum percentage difference between lines for it to be considered new seg
                            line1_changed = False
                            line2_changed = False

                            line = lines[counter]
                            length = line.width()

                            # Checks if it is the last line (so we prohibit illegal compare)
                            if len(lines) - 1 >= counter + 1:
                                next_line = lines[counter + 1]
                                next_line_length = next_line.width()

                                # Checks if the next line is changed more than line_diff
                                if next_line_length not in range(int(round(length * (1 - line_diff))),
                                                                 int(round(length * (1 + line_diff)))):
                                    line1_changed = True

                                # Checks if it is the second last line (so we prohibit illegal compare)
                                if len(lines) - 1 > counter + 2:
                                    next_line2 = lines[counter + 2]
                                    next_line2_length = next_line2.width()

                                    # Checks if the next next line is changed more than line_diff
                                    if next_line2_length not in range(int(round(length * (1 - line_diff))),
                                                                      int(round(length * (1 + line_diff)))):
                                        line2_changed = True

                            # Checks if the next and the next next line are changed
                            if line1_changed and line2_changed:
                                grouped_lines.append(line)
                                new_coordinates = self.__make_box_around_lines(grouped_lines)

                                if new_coordinates is not None:
                                    add_segment(self.__new_segments, new_coordinates, grouped_lines, segment.type)

                                grouped_lines.clear()
                                grouped_lines.append(lines[counter + 1])
                                counter += 1
                            else:
                                grouped_lines.append(line)
                            counter += 1

                        if len(grouped_lines) > 0:
                            grouped_lines.append(lines[counter])
                            coordinates = self.__make_box_around_lines(grouped_lines)

                            if coordinates is not None:
                                add_segment(self.__new_segments, coordinates, grouped_lines, segment.type)

                            grouped_lines.clear()
                            return_segments.remove(segment)

        return_segments.extend(self.__new_segments)
        return return_segments
        return return_segments.copy()

    def get_median_column_width(self):
        return self.__median_paragraph_width

    def add_last_segment(self, lines, counter, grouped_lines, return_segments, segment):
        if not counter >= len(lines):
            grouped_lines.append(lines[counter])
            if len(grouped_lines) > 0:
                new_coordinates = self.__make_box_around_lines(grouped_lines)

                if new_coordinates is not None:
                    self.__add_segment(self.__new_segments, new_coordinates[0], new_coordinates[1], new_coordinates[2], new_coordinates[3], grouped_lines, segment.type)
                grouped_lines.clear()
                return_segments.remove(segment)

    def __add_segment(self, segments: list, x, y, x2, y2, lines, type: str):
        segment = Segment()
        segment.x1 = x
        segment.y1 = y
        segment.x2 = x2
        segment.y2 = y2
        segment.lines = lines
        segment.type = type
        segments.append(segment)

    def get_avg_column_width(self):
        return self.__avg_paragraph_width

    def __make_box_around_lines(self, lines: list):
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
