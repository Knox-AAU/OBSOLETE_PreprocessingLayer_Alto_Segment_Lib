from xml.dom import minidom
import operator
import enum
from alto_segment_lib.segment import Segment
from alto_segment_lib.segment import Line
import statistics
import re


class FindType(enum.Enum):
    Paragraph = 1
    Header = 2


def determine_most_frequent_list_element(the_list: list):
    return max(set(the_list), key=the_list.count)


class AltoSegmentExtractor:
    __path: str
    __dpi: int
    __margin: int
    __xmldoc: minidom
    __para_fonts = []
    __head_fonts = []

    def __init__(self, alto_path: str = "", dpi: int = 300, margin: int = 0, lines: list = None):
        if lines is None:
            lines = []
        self.__dpi = dpi
        self.__margin = margin
        self.__lines = lines
        if not alto_path == "":
            self.set_path(alto_path)

    def set_path(self, path: str):
        self.__path = path
        self.__xmldoc = minidom.parse(self.__path)
        self.__font_statistics()

    def set_dpi(self, dpi: int):
        self.__dpi = dpi

    def get_dpi(self):
        return self.__dpi

    def set_margin(self, margin: int):
        self.__margin = margin

    def get_margin(self):
        return self.__margin

    def __find_segments_by_tag_name(self, tagname: str):
        segments: list = []
        elements = self.__xmldoc.getElementsByTagName(tagname)

        for element in elements:
            coordinate = self.__extract_coordinates(element)
            segments.append(Segment(coordinate))

        return segments

    def find_blocks_coordinates(self):
        return self.__find_segments_by_tag_name('TextBlock')

    def find_lines_coordinates(self):
        return self.__find_segments_by_tag_name('TextLine')

    def find_lines_in_segment(self, elem: minidom):
        segments: list = []

        text_lines = elem.getElementsByTagName('TextLine')

        for text_line in text_lines:
            coordinate = self.__extract_coordinates(text_line)
            segments.append(coordinate)

        return segments

    def find_headlines(self):
        return self.__find_segs_with_type(FindType.Header)

    def find_paragraphs(self):
        return self.__find_segs_with_type(FindType.Paragraph)

    def __find_segs_with_type(self, SegmentsToExtract: FindType):
        segments: list = []
        lines: list = []

        text_blocks = self.__xmldoc.getElementsByTagName('TextBlock')

        for text_block in text_blocks:
            text_lines = text_block.getElementsByTagName('TextLine')
            text_lines_coord = self.find_lines_in_segment(text_block)
            coordinate = None

            if SegmentsToExtract == FindType.Header:
                if text_lines[0].attributes['STYLEREFS'].value in self.__para_fonts:
                    coordinate = self.__extract_coordinates(text_block)
            elif SegmentsToExtract == FindType.Paragraph:
                if text_lines[0].attributes['STYLEREFS'].value not in self.__para_fonts:
                    coordinate = self.__extract_coordinates(text_block)

            if coordinate is not None:
                coordinate.append(text_lines_coord)
                segments.append(coordinate)

        return segments

    def extract_segments(self):
        segments = []
        text_blocks = self.__xmldoc.getElementsByTagName('TextBlock')

        for text_block in text_blocks:
            text_block_coordinates = self.__extract_coordinates(text_block)
            segment = Segment(text_block_coordinates)
            text_lines = text_block.getElementsByTagName('TextLine')
            text_line_fonts = []

            for text_line in text_lines:
                text_line_coordinates = self.__extract_coordinates(text_line)
                line = Line(text_line_coordinates)
                if segment.between_x_coords(line.x1 + 10) and segment.between_x_coords(line.x2 - 10):
                    text_line_fonts.append(text_line.attributes['STYLEREFS'].value)
                    segment.lines.append(line)

            style = determine_most_frequent_list_element(text_line_fonts)

            if style in self.__para_fonts:
                segment.type = "paragraph"
            elif style in self.__head_fonts:
                segment.type = "headline"
            else:
                segment.type = "Unknown"

            segments.append(segment)

        return segments

    def extract_lines(self):
        lines = []
        text_lines = self.__xmldoc.getElementsByTagName('TextLine')

        for text_line in text_lines:
            text_line_coordinates = self.__extract_coordinates(text_line)
            line = Line(text_line_coordinates)

            lines.append(line)

        return lines

    def __extract_coordinates(self, element: minidom):
        coordinates = [
            int(element.attributes['HPOS'].value),
            int(element.attributes['VPOS'].value),
            int(element.attributes['WIDTH'].value) + int(element.attributes['HPOS'].value),
            int(element.attributes['HEIGHT'].value) + int(element.attributes['VPOS'].value)
        ]

        for idx in range(4):
            va = coordinates[idx]
            if isinstance(va, int):
                coordinates[idx] = self.inch1200_to_px(coordinates[idx])

        if self.__margin > 0:
            coordinates[0] -= self.__margin
            coordinates[1] -= self.__margin
            coordinates[2] += self.__margin
            coordinates[3] += self.__margin

        return coordinates

    def inch1200_to_px(self, inch1200: int):
        return int(round((inch1200 * self.__dpi) / 1200))

    def find_line_height_median(self, lines):
        height = []
        for line in lines:
            height.append(line.height())
        return statistics.median(height)

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
        x_groups = self.group_same_x(lines)
        y_groups = self.group_same_y(x_groups)

        for group in y_groups:
            if len(group) > 0:
                new_segment = group[0]
                min_x = min(group, key=lambda line: line.x1)
                max_x = max(group, key=lambda line: line.x2)
                min_y = min(group, key=lambda line: line.y1)
                max_y = max(group, key=lambda line: line.y2)
                new_segment.x1 = min_x.x1
                new_segment.y1 = min_y.y1
                new_segment.x2 = max_x.x2
                new_segment.y2 = max_y.y2
                segment.append(new_segment)
        return segment

    def group_same_x(self, lines):
        previous_line = None
        temp = []
        x_groups = []

        lines = sorted(lines, key=lambda sorted_line: sorted_line.x1)

        for line in lines:
            if previous_line is None:
                previous_line = line
                continue
            if line.x1 - previous_line.x1 < 100:
                x_diff = line.x1 - previous_line.x1
                temp.append(line)
            else:
                x_groups.append(temp)
                temp = [line]
                previous_line = line
        return x_groups

    def group_same_y(self, x_group):
        previous_line = None
        temp = []
        y_groups = []

        for group in x_group:
            group = sorted(group, key=lambda sorted_group: sorted_group.y1)
            previous_line = None
            for line in group:
                if previous_line is None:
                    previous_line = line
                    temp = [line]
                    continue
                if line.y1 - previous_line.y2 < 15:
                    temp.append(line)
                else:
                    y_groups.append(temp)
                    temp = [line]
                previous_line = line
            if len(temp) > 1:
                y_groups.append(temp)
                temp = []
        return y_groups

    def __font_statistics(self):
        fonts: dict = self.__find_font_sizes()
        stats = {}

        for key in fonts:
            lines = self.__xmldoc.getElementsByTagName('TextLine')
            for line in lines:
                if line.attributes['STYLEREFS'].value == key:
                    if not stats.__contains__(key):
                        stats[key] = 1
                    else:
                        stats[key] += 1

        most_used_font = max(stats.items(), key=operator.itemgetter(1))[0]
        #print(most_used_font)

        for key in fonts:
            if fonts.get(key) <= fonts.get(most_used_font) + 1:
                self.__para_fonts.append(key)
                #print("Para: " + key)
            else:
                self.__head_fonts.append(key)
                #print("Head: " + key)

    def __find_font_sizes(self):
        fonts = {}
        styles = self.__xmldoc.getElementsByTagName('TextStyle')
        for style in styles:
            fonts[str(style.attributes['ID'].value)] = float(style.attributes['FONTSIZE'].value)
        return fonts

    def repair_text_lines(self, text_lines):
        margin = 5
        for text_line in text_lines:
            if text_line.is_horizontal:
                (does_line_intersect, lines) = self.does_line_intersect_text_line(text_line)
                if does_line_intersect:
                    for line in lines:
                        coords = [line.x1 + margin, text_line.y1, text_line.x2, text_line.y2]
                        text_line.x2 = line.x1 - margin

                        text_lines.append(Line(coords))

        return text_lines

    def does_line_intersect_text_line(self, text_line):
        new_lines = []
        for line in self.__lines:
            # finds 5% of the width and height as a buffer
            width_5_percent = (text_line.x2 - text_line.x1) * 0.05
            # checks if a line is going through one of the lines of the text_line
            # width/height is a buffer so we dont get false positives due to crooked lines
            if not line.is_horizontal():
                if text_line.x1 + width_5_percent < line.x1 < text_line.x2 - width_5_percent:
                    if line.y1 < text_line.y1 < line.y2 or line.y1 < text_line.y2 < line.y2:
                        new_lines.append(line)

        if len(new_lines) != 0:
            return True, new_lines
        else:
            return False, None

