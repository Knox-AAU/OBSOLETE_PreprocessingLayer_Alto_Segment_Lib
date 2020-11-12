import argparse
import os

import line_extractor
from alto_segment_lib.repair_segments import RepairSegments
from alto_segment_lib.alto_segment_extractor import AltoSegmentExtractor
import matplotlib.pyplot as plt

from alto_segment_lib.segment_helper import SegmentHelper
from alto_segment_lib.segment_ordering import SegmentOrdering
from matplotlib.patches import Rectangle
from PIL import Image
from matplotlib.patches import ConnectionPatch

from line_extractor.extractor import LineExtractor

base_path: str
filename: str
filepath: str
filetype = ".jp2"


def display_segments(segments_for_display):
    plt.imshow(Image.open(filepath + filetype))
    plt.rcParams.update({'font.size': 3, 'text.color': "red", 'axes.labelcolor': "red"})

    counter = 1

    # Add the patch to the Axes
    # plt.hlines(100, 100, 100+repair.get_median_column_width(), colors='k', linestyles='solid', label='Median paragraph width')

    for segment in segments_for_display:
        plt.gca().add_patch(
            Rectangle((segment.x1, segment.y1), (segment.x2 - segment.x1), (segment.y2 - segment.y1), linewidth=0.3,
                      edgecolor='r', facecolor='none'))
        # plt.text(segment.x1+25, segment.y1+30, "["+str(counter)+"]", horizontalalignment='left', verticalalignment='top')
        # plt.text(seg[0]+45, seg[1] + 200, str((seg[2]-seg[0])), horizontalalignment='left', verticalalignment='top')
        counter += 1

    plt.savefig(filepath + "-repaired.png", dpi=600, bbox_inches='tight')
    plt.gca().clear()
    print("File has been generated: '" + filename + "-out.png'")


def display_lines(headers_for_display, paragraphs_for_display):
    plt.imshow(Image.open(filepath + filetype))
    plt.rcParams.update({'font.size': 3, 'text.color': "red", 'axes.labelcolor': "red"})

    counter = 1

    for segment in headers_for_display:
        plt.gca().add_patch(
            Rectangle((segment.x1, segment.y1), (segment.x2 - segment.x1), (segment.y2 - segment.y1), linewidth=0.3,
                      edgecolor='b', facecolor='none'))
        counter += 1

    for segment in paragraphs_for_display:
        plt.gca().add_patch(
            Rectangle((segment.x1, segment.y1), (segment.x2 - segment.x1), (segment.y2 - segment.y1), linewidth=0.3,
                      edgecolor='r', facecolor='none'))
        counter += 1

    plt.savefig(filepath + "-out.png", dpi=600, bbox_inches='tight')
    plt.gca().clear()
    print("File has been generated: '" + filename + "-out.png'")


def run_multiple_files(base_path):
    for file_name in os.listdir(base_path):
        file_path = os.path.join(base_path, file_name)

        if not os.path.isfile(file_path) or not file_path.endswith(".jp2"):
            continue
        file_path = filepath.split(".jp2")[0]
        print(filepath)

        run_file(file_path)


def run_file(file_path):
    lines = LineExtractor().extract_lines_via_path(file_path + ".jp2")

    altoExtractor = AltoSegmentExtractor(file_path + ".alto.xml")
    altoExtractor.set_dpi(300)
    altoExtractor.set_margin(0)

    segment_helper = SegmentHelper()

    text_lines = altoExtractor.extract_lines()
    text_lines = segment_helper.repair_text_lines(text_lines, lines)
    # display_segments(text_lines)
    lists = segment_helper.group_lines_into_paragraph_headers(text_lines)
    # display_lines(lists[0], lists[1])
    segments = segment_helper.combine_lines_into_segments(lists[1])
    display_segments(segments)

    # print("Repair segments")
    # Extract document dimensions
    # dimensions = segmenter.extract_document_dimensions()

    paragraphs = [segment for segment in segments if segment.type == "paragraph"]
    repair = RepairSegments(paragraphs, lines, 30)
    rep_rows_segments1 = repair.repair_columns()
    rep_rows_segments2 = repair.repair_rows()
    paragraphs.clear()
    segments_para = rep_rows_segments2
    display_segments(segments_para)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # defines input and output path
    parser.add_argument('path', help='The path to the image folder')
    parser.add_argument('filename', help='The name of the file without filetype')

    args = parser.parse_args()

    base_path = args.path
    filename = args.filename
    filepath = base_path + filename

    # run_multiple_files(base_path)
    run_file(filepath)

    # for seg in paragraphs:
    #    print('x:{0} y:{1} x1:{2} y2:{3} - {4}'.format(str(seg.x1), str(seg.y1), str(seg.x2), str(seg.y2), seg.type))

    # segments = segmenter.extract_segments()
    # segments_para = [segment for segment in segments if segment.type == "paragraph"]
    # segments_headers = [segment for segment in segments if segment.type == "headline"]

    # segment_order = SegmentOrdering(base_path, filename)
    # segments_in_articles = segment_order.distribute_segments_into_articles(segments_headers, segments_para)
    # display_segments(segments_headers)

    # Display lines
    # segment_order.display_lines(lines)
