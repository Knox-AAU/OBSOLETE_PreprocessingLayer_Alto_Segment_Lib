import configparser
import math
from math import atan2
import cv2
from os import environ
import numpy as np
from line_extractor.houghbundler import HoughBundler
environ["OPENCV_IO_ENABLE_JASPER"] = "true"


class LineExtractor:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    def extract_lines_via_path(self, image_path):
        image = cv2.imread(image_path, cv2.CV_8UC1)
        lines = self.extract_lines_via_image(image)
        self.show_lines_on_image(image,lines)

    def extract_lines_via_image(self, image):
        enhanced_image = self.enhance_lines(image)
        return self.convert_lines_into_coordinates(enhanced_image)

    def enhance_lines(self, image):
        image_thresh = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,
                                             int(self.config['line_enhancement']['threshold'].split(',')[0])
                                            ,int(self.config['line_enhancement']['threshold'].split(',')[1]))

        image_horizontal = image_thresh
        image_vertical = image_thresh

        horizontal_size, vertical_size = image_thresh.shape
        horizontal_size = int(horizontal_size / int(self.config['line_enhancement']['horizontal_size']))
        vertical_size = int(vertical_size / int(self.config['line_enhancement']['vertical_size']))

        horizontal_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))

        kernel = np.ones((1, 1), np.uint8)
        image_horizontal = cv2.erode(image_horizontal, horizontal_structure, kernel)
        image_horizontal = cv2.dilate(image_horizontal, horizontal_structure, kernel)

        vertical_structure = cv2.getStructuringElement(cv2.MORPH_CROSS, (1, vertical_size))
        kernel = np.ones((1, 1), np.uint8)
        image_vertical = cv2.erode(image_vertical, vertical_structure, kernel)
        image_vertical = cv2.dilate(image_vertical, vertical_structure, kernel)

        merged_image = cv2.addWeighted(image_horizontal, 1, image_vertical, 1, 0)

        return merged_image

    def convert_lines_into_coordinates(self, image):
        rho = int(self.config['line_extraction']['rho'])  # distance resolution in pixels of the Hough grid
        theta = np.pi / int(self.config['line_extraction']['theta_divisions'])  # angular resolution in radians of the Hough grid
        threshold = int(self.config['line_extraction']['threshold'])  # minimum number of votes (intersections in Hough grid cell)
        min_line_length = int(self.config['line_extraction']['min_line_length'])  # minimum number of pixels making up a line
        max_line_gap = int(self.config['line_extraction']['max_line_gap'])  # maximum gap in pixels between connectable line segments

        diversion = int(self.config['line_extraction']['diversion'])
        min_horizontal_angle = -diversion
        max_horizontal_angle = diversion

        min_vertical_angle = 90 - diversion
        max_vertical_angle = 90 + diversion

        # Run Hough on edge detected image.jp2
        # Output "lines" is an array containing endpoints of detected line segments
        lines = cv2.HoughLinesP(image, rho, theta, threshold, np.array([]),
                                min_line_length, max_line_gap)

        filtered_lines = []

        lines_groups = HoughBundler().process_lines(lines)

        for line in lines_groups:
            angle = atan2(line[1][1] - line[0][1], line[1][0] - line[0][0]) * 180.0 / math.pi
            if min_vertical_angle < angle < max_vertical_angle or min_horizontal_angle < angle < max_horizontal_angle:
                filtered_lines.append(line)

        return filtered_lines

    @staticmethod
    def show_lines_on_image(image, lines):
        line_image = np.copy(image) * 0  # creating a blank to draw lines on
        line_image = cv2.cvtColor(line_image, cv2.COLOR_GRAY2RGB)
        for line in lines:
            cv2.line(line_image, (line[0][0], line[0][1]), (line[1][0], line[1][1]), (0, 0, 255), 2)

        image_in_color = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        lines_edges = cv2.addWeighted(image_in_color, 0.5, line_image, 1, 0)

        cv2.namedWindow("image", cv2.WINDOW_NORMAL)
        cv2.imshow("image", lines_edges)
        cv2.waitKey(0)
