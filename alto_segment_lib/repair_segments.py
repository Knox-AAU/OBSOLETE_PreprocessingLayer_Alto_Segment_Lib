from alto_segment_lib.segment import Segment
from alto_segment_lib.segment_helper import SegmentHelper
import statistics


def add_segment(segments: list, coordinates: list, lines, seg_type: str):
    segment = Segment(coordinates)
    segment.lines = lines
    segment.type = seg_type
    segments.append(segment)


class RepairSegments:

    def __init__(self, segments, lines, threshold: int = 10):
        self.__segments = segments
        self.__threshold = threshold
        self.__lines = lines
        self.__new_segments = []
        self.__median_paragraph_width = 0
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

        if seg_width > max_width and self.does_line_overlap_segment(segment):
            return True
        return False

    def does_line_overlap_segment(self, segment):
        for line in self.__lines:
            # finds 5% of the width and height as a buffer
            width_5_percent = (segment.x2 - segment.x1) * 0.05
            height_5_percent = (segment.y2 - segment.y1) * 0.05
            # checks if a line is going through one of the lines of the segment
            # width/height is a buffer so we dont get false positives due to crooked lines
            if line.is_horizontal():
                if segment.y1 + height_5_percent < line.y1 < segment.y2 - height_5_percent:
                    if line.x1 < segment.x1 < line.x2 or line.x1 < segment.x2 < line.x2:
                        return True
            else:
                if segment.x1 + width_5_percent < line.x1 < segment.x2 - width_5_percent:
                    if line.y1 < segment.y1 < line.y2 or line.y1 < segment.y2 < line.y2:
                        return True
        return False

    def repair_columns(self):
        for segment in self.__segments:
            if self.__need_repair(segment):
                cur_seg_width = (segment.x2 - segment.x1)
                segment.x2 = segment.x1 + (cur_seg_width / 2) - 5

                # Make segment
                coords = [segment.x1 + (cur_seg_width / 2) + 5, segment.y1, segment.x2 + (cur_seg_width / 2),
                          segment.y2]
                add_segment(self.__segments, coords, [], segment.type)

        return self.__segments.copy()

    @staticmethod
    def __remove_surrounded_segments(segment, subsegment):
        # Checks if both y-coordinates for the subsegment is within the segment: remove the subsegment
        if segment.between_y_coords(subsegment.y1 + 5) \
                and segment.between_y_coords(subsegment.y2 - 5) \
                and segment.between_x_coords(subsegment.x1 + 5) \
                and segment.between_x_coords(subsegment.x2 - 5):
            return True
        return False

    def repair_rows(self, range_span: int = 50):
        return_segments = self.__segments.copy()
        segment_helper = SegmentHelper()
        thresh_within = 5
        thresh_close_to = 20

        # Iterates through all segments and all other segments
        for segment in self.__segments:
            for subsegment in self.__segments:
                if not segment.compare(subsegment):
                    # Checks if both y and x-coordinates for the subsegment is within the segment
                    if segment.between_y_coords(subsegment.y1 + thresh_within) \
                            and segment.between_y_coords(subsegment.y2 - thresh_within) \
                            and segment.between_x_coords(subsegment.x1 + thresh_within) \
                            and segment.between_x_coords(subsegment.x2 - thresh_within) \
                            and subsegment in return_segments:
                        return_segments.remove(subsegment)
                    # Checks if subsegment is vertically close to segment
                    elif (segment.between_x_coords(subsegment.x1 + thresh_close_to)
                            or segment.between_x_coords(subsegment.x2 - thresh_close_to)) \
                            and subsegment in return_segments:
                        # Checks if the upper y-coordinate for subsegment is withing segment
                        if segment.between_y_coords(subsegment.y1):
                            return_segments.remove(subsegment)
                            # Move y-coordinate to be beside segment
                            subsegment.y1 = segment.y2
                            return_segments.append(subsegment)
                        # Checks if the lower y-coordinate for subsegment is within segment
                        elif segment.between_y_coords(subsegment.y2):
                            return_segments.remove(subsegment)
                            # Move y-coordinate to be beside segment
                            subsegment.y2 = segment.y1
                            return_segments.append(subsegment)
        return return_segments.copy()

    def get_median_column_width(self):
        return self.__median_paragraph_width

