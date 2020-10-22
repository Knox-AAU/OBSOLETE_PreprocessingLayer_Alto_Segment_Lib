from xml.dom import minidom
import operator


# First fixed column overlap then row overlap

class RepairSegments:

    __segments: list
    __avg_paragraph_width: float
    __threshold: int

    def __init__(self, segments: list, threshold: int = 10):
        self.__segments = segments
        self.__threshold = threshold
        self.__analyze_coordinates()

    def __analyze_coordinates(self):
        sum_width = 0
        for segment in self.__segments:
            sum_width += (segment[2]-segment[0])
        self.__avg_paragraph_width = sum_width/len(self.__segments)
        print("Avg. paragraph width: "+(str(self.__avg_paragraph_width)))

    def __is_valid_segment(self, segment: list):
        seg_width = (segment[2] - segment[0])
        min_width = self.__avg_paragraph_width-self.__threshold
        max_width = self.__avg_paragraph_width+self.__threshold

        if min_width < seg_width < max_width:
            return 0
        elif seg_width < min_width:
            return -1
        else:
            return 1

    def repair_columns(self):
        for segment in self.__segments:
            col_size = self.__is_valid_segment(segment)

            if col_size == 1:
                print("Hest")
                # Bigger then it should be

            if col_size == -1:
                print("Flodhest")
                # Smaller then it should be

