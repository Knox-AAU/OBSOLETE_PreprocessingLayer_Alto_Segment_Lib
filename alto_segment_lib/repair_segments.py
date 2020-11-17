from alto_segment_lib.segment import Segment
from alto_segment_lib.segment_helper import SegmentHelper
import statistics


def add_segment(segments: list, coordinates: list, lines, seg_type: str):
    segment = Segment(coordinates)
    segment.lines = lines
    segment.type = seg_type
    segments.append(segment)


class RepairSegments:

    def __init__(self, segments, threshold: int = 10):
        self.__segments = segments
        self.__threshold = threshold
        self.__new_segments = []
        self.__median_paragraph_width = 0
        self.__analyze_coordinates()

    def __analyze_coordinates(self):
        all_para = []
        for segment in self.__segments:
            all_para.append(segment.x2 - segment.x1)
        self.__median_paragraph_width = statistics.median(all_para)

    def repair_rows(self):
        return_segments = self.__segments.copy()
        thresh_within = 5

        # Iterates through all segments and all other segments
        for segment in self.__segments:
            for subsegment in self.__segments:
                if not segment.compare(subsegment):
                    thresh_close_to = subsegment.width() * 0.05
                    if subsegment in return_segments:
                        subsegment_index = return_segments.index(subsegment)
                    else:
                        continue

                    # Checks if the subsegment is entirely within the segment
                    if segment.between_y_coords(subsegment.y1 + thresh_within) \
                            and segment.between_y_coords(subsegment.y2 - thresh_within) \
                            and segment.between_x_coords(subsegment.x1 + thresh_within) \
                            and segment.between_x_coords(subsegment.x2 - thresh_within):
                        return_segments.remove(subsegment)
                    # Checks if subsegment's x-coords are close to segment
                    elif (segment.between_x_coords(subsegment.x1 + thresh_close_to) \
                            or segment.between_x_coords(subsegment.x2 - thresh_close_to)):
                        # Checks if the upper y-coordinate for subsegment is withing segment
                        if segment.between_y_coords(subsegment.y1):
                            # Move y-coordinate to be beside segment
                            return_segments[subsegment_index].y1 = segment.y2
                        # Checks if the lower y-coordinate for subsegment is within segment
                        elif segment.between_y_coords(subsegment.y2):
                            # Move y-coordinate to be beside segment
                            return_segments[subsegment_index].y2 = segment.y1

        return return_segments.copy()

    def get_median_column_width(self):
        return self.__median_paragraph_width
