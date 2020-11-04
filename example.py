import argparse

from alto_segment_lib.repair_segments import RepairSegments
from alto_segment_lib.alto_segment_extractor import AltoSegmentExtractor
from alto_segment_lib.segmenter import Segmenter, FindType
from alto_segment_lib.segmentOrdering import SegmentOrdering
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image

base_path: str
filename: str
filepath: str
filetype = ".jp2"


def display_segments(segments_for_display):
    #plt.imshow(Image.open("/home/tlorentzen/Desktop/Example/1942/aalborgstiftstidende-1942-01-02-01-0028B.tiff"))
    plt.imshow(Image.open(filepath+filetype))
    plt.rcParams.update({'font.size': 3, 'text.color': "red", 'axes.labelcolor': "red"})

    counter = 1

    # Add the patch to the Axes
    #plt.hlines(100, 100, 100+repair.get_median_column_width(), colors='k', linestyles='solid', label='Median paragraph width')

    for segment in segments_for_display:
        plt.gca().add_patch(Rectangle((segment.pos_x, segment.pos_y), (segment.lower_x-segment.pos_x), (segment.lower_y-segment.pos_y), linewidth=0.3, edgecolor='r', facecolor='none'))
        # plt.text(segment.pos_x+25, segment.pos_y+30, "["+str(counter)+"]", horizontalalignment='left', verticalalignment='top')
        # plt.text(seg[0]+45, seg[1] + 200, str((seg[2]-seg[0])), horizontalalignment='left', verticalalignment='top')
        counter += 1

    plt.savefig(filepath+"-out.png", dpi=300, bbox_inches='tight')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # defines input and output path
    parser.add_argument('path', help='The path to the image folder')
    parser.add_argument('filename', help='The name of the file without filetype')

    args = parser.parse_args()

    base_path = args.path
    filename = args.filename
    filepath = base_path + filename

    segmenter = AltoSegmentExtractor(filepath + ".alto.xml")
    segmenter.set_dpi(300)
    segmenter.set_margin(0)
    #
    segments = segmenter.extract_segments()

    # print("Repair segments")

    paragraphs = [segment for segment in segments if segment.type == "paragraph"]
    repair = RepairSegments(paragraphs, 30)
    rep_rows_segments1 = repair.repair_columns()
    rep_rows_segments2 = repair.repair_rows()

    # for seg in paragraphs:
    #    print('x:{0} y:{1} x1:{2} y2:{3} - {4}'.format(str(seg.pos_x), str(seg.pos_y), str(seg.lower_x), str(seg.lower_y), seg.type))

    segments = segmenter.extract_segments()
    segments_para = [segment for segment in segments if segment.type == "paragraph"]
    segments_headers = [segment for segment in segments if segment.type == "headline"]

    segment_order = SegmentOrdering(base_path, filename)
    segments_in_articles = segment_order.distribute_segments_into_articles(segments_headers, segments_para)
    display_segments(segments)
