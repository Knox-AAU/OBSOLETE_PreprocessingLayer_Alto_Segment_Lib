from alto_segment_lib.repair_segments import RepairSegments
from alto_segment_lib.segmenter import Segmenter
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image

#filepath = "/Users/tlorentzen/Desktop/Example/1942/aalborgstiftstidende-1942-01-02-01-0028B"
filepath = "/Users/tlorentzen/Desktop/Example/2006/nordjyskestiftstidende-2006-10-10-01-0829A"

if __name__ == '__main__':
    segmenter = Segmenter(filepath + ".alto.xml")
    segmenter.set_dpi(300)
    segmenter.set_margin(0)

    #segments_paragraphs = segmenter.find_blocks()
    segments = segmenter.extract_segments()
    #segments_para = segmenter.find_segs_with_type(FindType.Paragraph)

    print("Repair segments")

    paragraphs = [segment for segment in segments if segment.type == "paragraph"]
    repair = RepairSegments(paragraphs, 30)
    repair.repair_columns()
    rep_rows_segments = repair.repair_rows()

    for seg in segments:
        print('x:{0} y:{1} x1:{2} y2:{3} - {4}'.format(str(seg.pos_x), str(seg.pos_y), str(seg.lower_x), str(seg.lower_y), seg.type))


    #segmenter.font_statistics()
    #segments = segmenter.find_lines()

    #plt.imshow(Image.open("/home/tlorentzen/Desktop/Example/1942/aalborgstiftstidende-1942-01-02-01-0028B.tiff"))
    plt.imshow(Image.open(filepath+".jp2"))
    plt.rcParams.update({'font.size': 3, 'text.color': "red", 'axes.labelcolor': "red"})

    counter = 1

    # Add the patch to the Axes

    plt.hlines(100, 100, 100+repair.get_avg_column_width(), colors='k', linestyles='solid', label='Avg. paragraph width')

    for segment in segments:
        plt.gca().add_patch(Rectangle((segment.pos_x, segment.pos_y), (segment.lower_x-segment.pos_x), (segment.lower_y-segment.pos_y), linewidth=0.3, edgecolor='r', facecolor='none'))
        plt.text(segment.pos_x+25, segment.pos_y+30, "["+str(counter)+"]", horizontalalignment='left', verticalalignment='top')
        # plt.text(seg[0]+45, seg[1] + 200, str((seg[2]-seg[0])), horizontalalignment='left', verticalalignment='top')
        counter += 1

    plt.savefig(filepath+"-out.png",dpi=300, bbox_inches='tight')
