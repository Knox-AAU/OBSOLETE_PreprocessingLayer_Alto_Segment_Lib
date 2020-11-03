from alto_segment_lib.repair_segments import *

class TestRepairSegments:

    def test_add_segment_success(self):
        segments = []
        add_segment(segments, [200, 400, 400, 800], [], "Paragraph")

        if len(segments) == 1:
            assert True
        else:
            assert False

    def test_add_segment_failed(self):
        segments = []
        add_segment(segments, [200, 400, 400, 800], [], "Paragraph")

        if len(segments) != 1:
            assert False
        else:
            assert True