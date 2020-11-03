from alto_segment_lib.alto_segment_extractor import AltoSegmentExtractor
from alto_segment_lib.alto_segment_extractor import *

class TestAltoSegmentExtractor:

    def test_inch1200_to_px_conversion_success(self):
        extractor = AltoSegmentExtractor()
        extractor.set_dpi(300)

        inch1200 = 14500

        if extractor.inch1200_to_px(inch1200) == 3625:
            assert True
        else:
            assert False

    def test_inch1200_to_px_conversion_failed(self):
        extractor = AltoSegmentExtractor()
        extractor.set_dpi(300)

        inch1200 = 14000

        if extractor.inch1200_to_px(inch1200) == 3625:
            assert False
        else:
            assert True

    def test_determine_most_frequent_list_element_success(self):
        list_of_names = ['hans', 'hanne', 'flemming', 'hans', 'ole', 'hans']

        most_frequent_element = determine_most_frequent_list_element(list_of_names)

        if most_frequent_element == "hans":
            assert True
        else:
            assert False

    def test_determine_most_frequent_list_element_failed(self):
        list_of_names = ['hans', 'hanne', 'flemming', 'hans', 'ole', 'hans']

        most_frequent_element = determine_most_frequent_list_element(list_of_names)

        if most_frequent_element == "ole":
            assert False
        else:
            assert True



