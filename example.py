from segmenter import Segmenter
from segmenter import FindType
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image

def find_pairs(segments):
    for segment1, segment2 in segments:
        segment1
        #if segment1 ???? segment2:



if __name__ == '__main__':
    #segmenter = Segmenter("/Users/tlorentzen/Desktop/Example/2006/nordjyskestiftstidende-2006-10-10-01-0829A.alto.xml")
    segmenter = Segmenter("/Users/idath/Desktop/Test/aalborgstiftstidende-1942-01-02-01-0028B.alto.xml")
    segmenter.set_dpi(300)
    segmenter.set_margin(0)
    segments_paragraphs = segmenter.find_blocks()
    segments_headers = segmenter.find_segs_with_type(FindType.Header)
    segments_para = segmenter.find_segs_with_type(FindType.Paragraph)
    segmenter.font_statistics()
    #segments = segmenter.find_lines()

    # Find pairs
    #find_pairs(segments_para)

    # Display the image
    #plt.imshow(Image.open("/Users/tlorentzen/Desktop/Example/2006/nordjyskestiftstidende-2006-10-10-01-0829A.jp2"))
    plt.imshow(Image.open("/Users/idath/Desktop/Test/aalborgstiftstidende-1942-01-02-01-0028B.jp2"))
    plt.rcParams.update({'font.size': 3, 'text.color': "red", 'axes.labelcolor': "red"})

    counter = 1

    # Add the patch to the Axes
    for seg in segments_para:
        plt.gca().add_patch(Rectangle((seg[0], seg[1]), (seg[2]-seg[0]), (seg[3]-seg[1]), linewidth=0.3, edgecolor='r', facecolor='none'))
        # plt.text(seg[0]+25, seg[1]+30, "["+str(counter)+"]", horizontalalignment='left', verticalalignment='top')
        # plt.text(seg[0]+45, seg[1] + 200, str((seg[2]-seg[0])), horizontalalignment='left', verticalalignment='top')
        counter += 1
    for seg in segments_headers:
        plt.gca().add_patch(Rectangle((seg[0], seg[1]), (seg[2]-seg[0]), (seg[3]-seg[1]), linewidth=0.3, edgecolor='b', facecolor='none'))
        # plt.text(seg[0]+25, seg[1]+30, "["+str(counter)+"]", horizontalalignment='left', verticalalignment='top')
        # plt.text(seg[0]+45, seg[1] + 200, str((seg[2]-seg[0])), horizontalalignment='left', verticalalignment='top')
        counter += 1

    plt.savefig("/Users/idath/Desktop/Test/aalborgstiftstidende-1942-01-02-01-0028B-out.png", dpi=300, bbox_inches='tight')
