import statistics
from itertools import count
from os import environ
from xml.dom import minidom
import operator
import enum
from matplotlib.patches import ConnectionPatch

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
from alto_segment_lib.segment import Segment
from line_extractor.extractor import LineExtractor
from line_extractor import Line
environ["OPENCV_IO_ENABLE_JASPER"] = "true"
import cv2


class SegmentOrdering:
    File_path = "/Users/Alexi/Desktop/KnoxFiler/4/"
    File_name = "aalborgstiftstidende-1942-01-02-01-0026B"
    Paragraph_normal_width: float

    def __init__(self, file_path="/Users/Alexi/Desktop/KnoxFiler/4/", file_name="aalborgstiftstidende-1942-01-02-01-0028B"):
        self.File_path = file_path
        self.File_name = file_name

    def distributeSegmentsIntoArticles(self, headers_org, paragraphs):
        """ Distributes the segments into articles
        :param headers_org: List of header segments
        :param paragraphs: List of paragraph segments
        """
        self.Paragraph_normal_width = self.__median_para_width(paragraphs)
        headers: list = []
        for header in headers_org:
            headers.append(header)

        # Remove Date, paper name, page number
        self.__y_cord_of_top_vertical_line()
        headers = self.__removeDatePapernamePagenumber(headers)
        paragraphs = self.__removeDatePapernamePagenumber(paragraphs)

        # Match headers with subheaders
        headers_with_subheaders = self.__matchHeadersWithSubheaders(headers, self.Paragraph_normal_width)
        # self.__displayHeaderPairs(headers_with_subheaders)

        # Match paragraphs with each other in order per article
        # articles: list = [[]]       # A list of articles with their paragraphs in an ordered list, and their header(s) as the first (and second) element(s)
        # articles = self.__matchParagraphsWithHeaders(headers_with_subheaders, paragraphs)

    def __removeDatePapernamePagenumber(self, segments: list):
        """ Removes the date paper name and page number from the list of segments. These are always found at the top of
        the page, and is therefore found from the position. This should maybe be done by the page header line.
        :param segments: A list of segments
        :return: The list of segments without null entries and date, paper name, page number
        """
        page_header_ends_at = 300
        segments = [i for i in segments if i]
        for segment in segments:
            if segment.pos_y < page_header_ends_at:
                segments.remove(segment)
        return segments

    def __y_cord_of_top_vertical_line(self):
        line_extractor = LineExtractor()
        all_lines = line_extractor.extract_lines_via_path(self.File_path + self.File_name + ".jp2")
        lines: list = [Line]

        # Find the right line
        for line in all_lines:
            if line.y1 > 500 or line.y2 > 500 or line.y1 < 50:
                continue
            print(line)
            lines.append(line)

        # Find the top three lines
        average_y = self.__find_top_three_lines(lines)


        # img = cv2.imread(self.File_path + self.File_name + ".jp2", cv2.CV_8UC1)
        # line_extractor.show_lines_on_image(img, great_lines)

        self.__displayLines(lines)

    def __sort(self):

    def __find_top_three_lines(self, lines) -> int:
        current_max_y = -1
        top_three_lines: list = []

        for line in lines:
            if current_max_y == -1:
                top_three_lines.append(line)
                current_max_y



    def __sort_by_y_cord(self, header: Segment):
        """ Simply used to sort a list of headers by their y coordinate
        :param header: Header to check
        :return: The headers y coordinate
        """
        return header.pos_y

    def __matchHeadersWithSubheaders(self, headers, median_line_width: float):
        """ Finds header, subheader pairs and returns them
        :param headers: Header pairs
        :param median_line_width: Normal paragraph width
        :return: A list of pairs of headers with subheaders. These pairs also contains pairs with a single element,
            these are the the headers without a subheader
        """
        headers_with_subheaders: list = []
        index_to_delete: list = []
        headers.sort(key=self.__sort_by_y_cord)

        # Finds header pairs
        for header in headers:
            for checking_header in headers:
                if checking_header == header:
                    continue
                if self.__is_subheader(header, checking_header, median_line_width):
                    pair: list = [header, checking_header]
                    headers_with_subheaders.append(pair)
                    # Adds the header to be removed later
                    if not index_to_delete.__contains__(header):
                        index_to_delete.append(header)
                    if not index_to_delete.__contains__(checking_header):
                        index_to_delete.append(checking_header)
        # Removes headers from headers list, to find the single headers
        for elm in index_to_delete:
            headers.remove(elm)

        # Add the last non header pairs
        for header in headers:
            headers_with_subheaders.append([header])

        return headers_with_subheaders

    def __is_subheader(self, header: Segment, possible_subheader: Segment, median_line_width: float):
        """ Checks if the possible_subheader is a subheader to the header
        :param header: Header segment
        :param possible_subheader: The header segment to check if it's a subheader to the header
        :param median_line_width: Normal paragraph width
        :return: True if they are a pair, false if aren't
        """
        header_width = header.lower_x - header.pos_x
        subheader_height = possible_subheader.lower_y - possible_subheader.pos_y

        if (-20 <= possible_subheader.pos_y - header.lower_y < 200 and -header_width <= header.pos_x - possible_subheader.pos_x <= header_width) \
                or (header.lower_x - header.pos_x < median_line_width * 0.6
                    and -subheader_height <= possible_subheader.pos_y - header.lower_y < subheader_height and -50 <= header.lower_x -
                    possible_subheader.pos_x <= header_width):
            return True
        else:
            return False

    def __median_para_width(self, segments: list):
        """ Finds the normal paragraph width
        :param segments: A list of segments
        :return: The normal paragraph width
        """
        all_para = []
        for segment in segments:
            all_para.append(segment.lower_x - segment.pos_x)
        return float(statistics.median(all_para))

    def __displayHeaderPairs(self, headers_with_subheaders: list):
        """ Outputs a picture with headers and subheaders marked
        :param headers_with_subheaders: A list of pairs and non pairs of headers
        """
        plt.imshow(Image.open(self.File_path + self.File_name + ".jp2"))
        plt.rcParams.update({'font.size': 3, 'text.color': "red", 'axes.labelcolor': "red"})

        for pair in headers_with_subheaders:
            for elm in pair:
                plt.gca().add_patch(
                    Rectangle((elm.pos_x, elm.pos_y), (elm.lower_x - elm.pos_x), (elm.lower_y - elm.pos_y), linewidth=0.3, edgecolor='b',
                              facecolor='none'))
            if len(pair) > 1:
                plt.gca().add_patch(
                    Rectangle((pair[0].pos_x, pair[0].pos_y), (pair[1].lower_x - pair[0].pos_x), (pair[1].lower_y - pair[0].pos_y),
                              linewidth=0.3, edgecolor='r',
                              facecolor='none'))

        plt.savefig(self.File_path + "Pairs75.png", dpi=1000, bbox_inches='tight')

    def __displayLines(self, lines: list):
        """ Outputs a picture with headers and subheaders marked
        :param headers_with_subheaders: A list of pairs and non pairs of headers
        """
        plt.imshow(Image.open(self.File_path + self.File_name + ".jp2"))
        plt.rcParams.update({'font.size': 3, 'text.color': "red", 'axes.labelcolor': "red"})

        for line in lines:
            plt.gca().add_patch(
                ConnectionPatch((line[0][0], line[0][1]), (line[1][0], line[1][1]), coordsA='data',linewidth=0.3, edgecolor='r', facecolor='none'))

        plt.savefig(self.File_path + "Lines.png", dpi=1000, bbox_inches='tight')

    def __matchParagraphsWithHeaders(self, headers_with_subheaders, paragraphs):
        pass

