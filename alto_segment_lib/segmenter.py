from xml.dom import minidom
import operator
import enum
from alto_segment_lib.segment import Segment
from alto_segment_lib.segment import Line

class FindType(enum.Enum):
    Paragraph = 1
    Header = 2

class Segmenter:
    __path: str
    __dpi: int
    __margin: int
    __xmldoc: minidom
    __para_fonts = []
    __head_fonts = []

    def __init__(self, alto_path: str, dpi: int = 300, margin: int = 0):
        self.__path = alto_path
        self.__dpi = dpi
        self.__margin = margin
        self.__xmldoc = minidom.parse(self.__path)
        self.font_statistics()

    def set_dpi(self, dpi: int):
        self.__dpi = dpi

    def set_margin(self, margin: int):
        self.__margin = margin

    def __find_segments_by_tag_name(self, tagname: str):
        segments: list = []
        elements = self.__xmldoc.getElementsByTagName(tagname)

        for element in elements:
            coordinate = self.__extract_coordinates(element)
            segments.append(self.make_segment_by_coordinates(coordinate))

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

    def __find_segs_with_type(self, SegmentsToExtract : FindType):
        segments: list = []
        lines :list = []

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
            segment = self.make_segment_by_coordinates(text_block_coordinates)
            text_lines = text_block.getElementsByTagName('TextLine')
            style = text_lines[0].attributes['STYLEREFS'].value

            if style in self.__para_fonts:
                segment.type = "paragraph"
            else:
                segment.type = "headline"

            for text_line in text_lines:
                text_line_coordinates = self.__extract_coordinates(text_line)
                line = self.make_line_by_coordinates(text_line_coordinates)
                segment.lines.append(line)

            segments.append(segment)

        return segments

    def __extract_coordinates(self, element: minidom):
        coordinates = [
            int(element.attributes['HPOS'].value),
            int(element.attributes['VPOS'].value),
            int(element.attributes['WIDTH'].value)+int(element.attributes['HPOS'].value),
            int(element.attributes['HEIGHT'].value)+int(element.attributes['VPOS'].value)
        ]

        for idx in range(4):
            va = coordinates[idx]
            if isinstance(va, int):
                coordinates[idx] = self.__inch1200_to_px(coordinates[idx])

        if self.__margin > 0:
            coordinates[0] -= self.__margin
            coordinates[1] -= self.__margin
            coordinates[2] += self.__margin
            coordinates[3] += self.__margin

        return coordinates

    def __inch1200_to_px(self, inch1200: int):
        return int(round((inch1200 * self.__dpi)/1200))

    def font_statistics(self):
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

        for key in fonts:
            if fonts.get(key) <= fonts.get(most_used_font)+1:
                self.__para_fonts.append(key)
            else:
                self.__head_fonts.append(key)

    def __find_font_sizes(self):
        fonts = {}
        styles = self.__xmldoc.getElementsByTagName('TextStyle')
        for style in styles:
            fonts[str(style.attributes['ID'].value)] = float(style.attributes['FONTSIZE'].value)
        return fonts

    def make_segment_by_coordinates(self, coordinates: list):
        segment = Segment()
        segment.pos_x = coordinates[0]
        segment.pos_y = coordinates[1]
        segment.lower_x = coordinates[2]
        segment.lower_y = coordinates[3]
        return segment;

    def make_line_by_coordinates(self, coordinates: list):
        return Line(coordinates[0], coordinates[1], coordinates[2], coordinates[3])