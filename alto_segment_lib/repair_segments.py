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
    __median_paragraph_width: float
    __threshold: int

    def __init__(self, segments, threshold: int = 10):
        self.__segments = segments
        self.__threshold = threshold
        self.__analyze_coordinates()

    def __analyze_coordinates(self):
        all_para = []
        for segment in self.__segments:
            all_para.append(segment.lower_x - segment.pos_x)
        self.__median_paragraph_width = statistics.median(all_para)

    def __need_repair(self, segment: Segment):
        seg_width = segment.lower_x - segment.pos_x
        min_width = self.__median_paragraph_width - self.__threshold
        max_width = self.__median_paragraph_width + self.__threshold

        if seg_width > max_width:
            return True
        return False

    def repair_columns(self):
        for segment in self.__segments:
            if self.__need_repair(segment):
                cur_seg_width = (segment.lower_x - segment.pos_x)
                segment.lower_x = segment.pos_x + (cur_seg_width / 2) - 5

                # Make segment
                coords = [segment.pos_x + (cur_seg_width / 2) + 5, segment.pos_y, segment.lower_x + (cur_seg_width / 2), segment.lower_y]
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
                    if (segment.pos_x - range_span) <= subsegment.pos_x <= (segment.pos_x + range_span):

                        # Checks if both y-coordinates for the subsegment is within the segment: remove the subsegment
                        if segment.between_y_coords(subsegment.pos_y) and segment.between_y_coords(subsegment.lower_y):
                            return_segments.remove(subsegment)
                        # Checks if  the  upper y-coordinate for subsegment is within segment: move y-coordinate to
                        # be beside segment
                        elif segment.between_y_coords(subsegment.pos_y):
                            subsegment.pos_y = segment.lower_y
                        # Checks if  the  lower y-coordinate for subsegment is within segment: move y-coordinate to
                        # be beside segment
                        elif segment.between_y_coords(subsegment.lower_y):
                            subsegment.lower_y = segment.pos_y

                    # hvis subsegment ligger Segment med forskellige x-koordinater: split op i mindre bokse
                    elif (segment.between_y_coords(subsegment.pos_y) or segment.between_y_coords(subsegment.lower_y)) \
                            and (segment.between_x_coords(subsegment.pos_x) or segment.between_x_coords(subsegment.lower_x)) \
                            and segment in return_segments:

                        counter: int = 0

                        print('{0}, {1}, {2}, {3}'.format(segment.pos_x, segment.pos_y, segment.lower_x, segment.lower_y))

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
        segment.pos_x = x
        segment.pos_y = y
        segment.lower_x = x2
        segment.lower_y = y2
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
        pos_x = lines[0].pos_x
        pos_y = lines[0].pos_y
        coordinates = []

        # Finds width and height line and change box height and width accordingly
        for line in lines:
            line_width = line.width()

            # Find x-coordinate upper left corner
            if line.pos_x < pos_x:
                pos_x = line.pos_x

            # Find y-coordinate upper left corner
            if line.pos_y < pos_y:
                pos_y = line.pos_y

            # Find box height
            if line.lower_y > box_height:
                box_height = line.lower_y

            # Find box width
            if line_width > box_width:
                box_width = line_width

        coordinates.append(pos_x)
        coordinates.append(pos_y)
        coordinates.append(pos_x + box_width)
        coordinates.append(box_height)

        return coordinates
