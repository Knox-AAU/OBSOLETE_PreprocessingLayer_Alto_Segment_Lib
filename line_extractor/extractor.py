import configparser
import math
from math import atan2
from os import environ
import numpy as np
from line_extractor.hough_bundler import HoughBundler
from line_extractor.line import Line

environ["OPENCV_IO_ENABLE_JASPER"] = "true"
import cv2


class LineExtractor:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        self.rho = int(self.config['line_extraction']['rho'])  # distance resolution in pixels of the Hough grid
        self.theta = np.pi / int(
            self.config['line_extraction']['theta_divisions'])  # angular resolution in radians of the Hough grid
        self.threshold = int(
            self.config['line_extraction']['threshold'])  # minimum number of votes (intersections in Hough grid cell)
        self.min_line_length = int(
            self.config['line_extraction']['min_line_length'])  # minimum number of pixels making up a line
        self.max_line_gap = int(
            self.config['line_extraction']['max_line_gap'])  # maximum gap in pixels between connectable line segments
        self.diversion = int(self.config['line_extraction']['diversion'])
        self.adaptive_threshold = [int(a) for a in self.config['line_enhancement']['threshold'].split(',')]
        self.vertical_size = int(self.config['line_enhancement']['vertical_size'])
        self.horizontal_size = int(self.config['line_enhancement']['horizontal_size'])

    def extract_lines_via_path(self, image_path):
        image = cv2.imread(image_path, cv2.CV_8UC1)
        lines = self.extract_lines_via_image(image)
        self.show_lines_on_image(image, lines)

    def extract_lines_via_image(self, image):
        enhanced_image = self.enhance_lines(image)
        return self.get_lines_from_binary_image(enhanced_image)

    def enhance_lines(self, image):

        # apply mean tresholding to bring out lines
        image_thresh = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,
                                             self.adaptive_threshold[0],
                                             self.adaptive_threshold[1])
        # saves the thresholding image for later use
        image_horizontal = image_thresh
        image_vertical = image_thresh

        # gets height and width of image, and specifies how long a line can be
        horizontal_size, vertical_size = image_thresh.shape
        horizontal_size = int(horizontal_size / self.horizontal_size)
        vertical_size = int(vertical_size / self.vertical_size)

        # opencv function to find horizontal/vertical lines
        horizontal_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
        vertical_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vertical_size))

        kernel = np.ones((1, 1), np.uint8)
        image_horizontal = cv2.erode(image_horizontal, horizontal_structure, kernel)
        image_horizontal = cv2.dilate(image_horizontal, horizontal_structure, kernel)

        kernel = np.ones((1, 1), np.uint8)
        image_vertical = cv2.erode(image_vertical, vertical_structure, kernel)
        image_vertical = cv2.dilate(image_vertical, vertical_structure, kernel)

        merged_image = cv2.addWeighted(image_horizontal, 1, image_vertical, 1, 0)

        cv2.namedWindow("image", cv2.WINDOW_NORMAL)
        cv2.imshow("image", merged_image)
        cv2.waitKey(0)

        return merged_image

    def get_lines_from_binary_image(self, image):
        lines = cv2.HoughLinesP(image, self.rho, self.theta, self.threshold, np.array([]),
                                self.min_line_length, self.max_line_gap)

        line_objects = [Line.from_array(line[0]) for line in lines]

        lines_groups = HoughBundler().process_lines(line_objects)

        return self.filter_by_angle_diversion_from_horizontal_and_vertical(lines_groups)

    def filter_by_angle_diversion_from_horizontal_and_vertical(self, lines_groups):
        min_horizontal_angle = -self.diversion
        max_horizontal_angle = self.diversion
        min_vertical_angle = 90 - self.diversion
        max_vertical_angle = 90 + self.diversion
        filtered_lines = []
        for line in lines_groups:
            angle = atan2(line.y2 - line.y1, line.x2 - line.x1) * 180.0 / math.pi
            if min_vertical_angle < angle < max_vertical_angle or min_horizontal_angle < angle < max_horizontal_angle:
                filtered_lines.append(line)
        return filtered_lines

    @staticmethod
    def show_lines_on_image(image, lines):
        line_image = np.copy(image) * 0  # creating a blank to draw lines on
        line_image = cv2.cvtColor(line_image, cv2.COLOR_GRAY2RGB)
        for line in lines:
            cv2.line(line_image, (line.x1, line.y1), (line.x2, line.y2), (0, 0, 255), 3)

        image_in_color = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        lines_edges = cv2.addWeighted(image_in_color, 0.5, line_image, 1, 0)

        cv2.namedWindow("image", cv2.WINDOW_NORMAL)
        cv2.imshow("image", lines_edges)
        cv2.waitKey(0)
