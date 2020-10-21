from xml.dom import minidom
import operator


class RepairSegments:

    __segments: list
    __avg_paragraph_width: float

    def __init__(self, segments: list):
        self.__segments = segments
        self.__analyze_coordinates()

    def __analyze_coordinates(self):
        sum_width = 0
        for segment in self.__segments:
            sum_width += (segment[2]-segment[0])
        self.__avg_paragraph_width = sum_width/len(self.__segments)
        print("Avg. paragraph width: "+(str(self.__avg_paragraph_width)))

