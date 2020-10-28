from alto_segment_lib.repair_segments import RepairSegments
from alto_segment_lib.segmenter import Segmenter, FindType
from alto_segment_lib.segmentOrdering import SegmentOrdering
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image

#filepath = "/Users/tlorentzen/Desktop/Example/1942/aalborgstiftstidende-1942-01-02-01-0028B"
# filepath = "/Users/tlorentzen/Desktop/Example/2006/nordjyskestiftstidende-2006-10-10-01-0829A"
filepath = "/Users/Alexi/Desktop/KnoxFiler/4/aalborgstiftstidende-1942-01-02-01-0026B"
File_path = "/Users/Alexi/Desktop/KnoxFiler/4/"
File_name = "aalborgstiftstidende-1942-01-02-01-0026B"


def displaySegments(segments):
    #plt.imshow(Image.open("/home/tlorentzen/Desktop/Example/1942/aalborgstiftstidende-1942-01-02-01-0028B.tiff"))
    plt.imshow(Image.open(filepath+".jp2"))
    plt.rcParams.update({'font.size': 3, 'text.color': "red", 'axes.labelcolor': "red"})

    counter = 1

    # Add the patch to the Axes

    plt.hlines(100, 100, 100+repair.get_avg_column_width(), colors='k', linestyles='solid', label='Avg. paragraph width')

    for segment in segments:
        plt.gca().add_patch(Rectangle((segment.pos_x, segment.pos_y), (segment.lower_x-segment.pos_x), (segment.lower_y-segment.pos_y), linewidth=0.3, edgecolor='r', facecolor='none'))
        plt.text(segment.pos_x+25, segment.pos_y+30, "["+str(counter)+"]", horizontalalignment='left', verticalalignment='top')
        counter += 1

    plt.savefig(filepath+"-out.png", dpi=300, bbox_inches='tight')

if __name__ == '__main__':
    segmenter = Segmenter(filepath + ".alto.xml")
    segmenter.set_dpi(300)
    segmenter.set_margin(0)

    segments = segmenter.extract_segments()
    segments_para = [segment for segment in segments if segment.type == "paragraph"]
    segments_headers = [segment for segment in segments if segment.type == "headline"]

    segmentOrder = SegmentOrdering(File_path, File_name)
    segmentsInArticles = segmentOrder.distributeSegmentsIntoArticles(segments_headers, segments_para)

    if False:
        print("Repair segments")

        paragraphs = [segment for segment in segments if segment.type == "paragraph"]
        repair = RepairSegments(paragraphs, 30)
        rep_rows_segments1 = repair.repair_columns()
        rep_rows_segments2 = repair.repair_rows()

        # for seg in segments:
        #     print('x:{0} y:{1} x1:{2} y2:{3} - {4}'.format(str(seg.pos_x), str(seg.pos_y), str(seg.lower_x), str(seg.lower_y), seg.type))


        #segmenter.font_statistics()
        #segments = segmenter.find_lines()
        displaySegments(segments)



