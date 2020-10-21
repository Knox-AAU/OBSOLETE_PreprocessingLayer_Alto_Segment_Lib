from xml.dom import minidom
import operator
import enum


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

    def set_dpi(self, dpi: int):
        self.__dpi = dpi

    def set_margin(self, margin: int):
        self.__margin = margin

    def find_blocks(self):
        segments: list = []
        text_blocks = self.__xmldoc.getElementsByTagName('TextBlock')

        for text_block in text_blocks:
            coordinate = self.__extract_coordinates(text_block)
            segments.append(coordinate)

        return segments

    def find_lines(self):
        segments: list = []
        text_blocks = self.__xmldoc.getElementsByTagName('TextBlock')

        for text_block in text_blocks:
            text_lines = text_block.getElementsByTagName('TextLine')
            for line in text_lines:
                coordinate = self.__extract_coordinates(line)
                segments.append(coordinate)

        return segments

    def find_headers(self, SegmentsToExtract : FindType):
        # self.__findFontSizes()
        self.font_statistics()

        segments: list = []
        text_blocks = self.__xmldoc.getElementsByTagName('TextBlock')

        for text_block in text_blocks:
            text_lines = text_block.getElementsByTagName('TextLine')

            if SegmentsToExtract == 1:
                if text_lines[0].attributes['STYLEREFS'].value in self.__para_fonts:
                    coordinate = self.__extract_coordinates(text_block)
                    if coordinate is not None:
                        segments.append(coordinate)
            elif SegmentsToExtract == 2:
                if text_lines[0].attributes['STYLEREFS'].value not in self.__para_fonts:
                    coordinate = self.__extract_coordinates(text_block)
                    if coordinate is not None:
                        segments.append(coordinate)
        return segments

    def __extract_coordinates(self, element: minidom):
        coordinates = [
            int(element.attributes['HPOS'].value),
            int(element.attributes['VPOS'].value),
            int(element.attributes['WIDTH'].value)+int(element.attributes['HPOS'].value),
            int(element.attributes['HEIGHT'].value)+int(element.attributes['VPOS'].value),
            str(element.attributes['ID'].value)
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

        if int(self.__inch1200_to_px(int(element.attributes['WIDTH'].value))) <= 50:
            return None

        return coordinates

    def __inch1200_to_px(self, inch1200: int):
        return int(round((inch1200 * self.__dpi)/1200))

    def __check_lines(self, lines: minidom):
        print("")

        for text_line in lines:
            print(self.__inch1200_to_px(int(text_line.attributes['WIDTH'].value)))

        print("")

        return []

    def __findFontSizes(self):
        fonts = {}
        styles = self.__xmldoc.getElementsByTagName('TextStyle')
        for style in styles:
            fonts[str(style.attributes['ID'].value)] = float(style.attributes['FONTSIZE'].value)
        return fonts

    def font_statistics(self):
        fonts: dict = self.__findFontSizes()
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

        print("Most used fontsize: "+str(most_used_font))

        for key in fonts:
            if fonts.get(key) <= fonts.get(most_used_font)+1:
                print("Paragraph: "+key)
                self.__para_fonts.append(key)
            else:
                print("Header: " + key)
                self.__head_fonts.append(key)
