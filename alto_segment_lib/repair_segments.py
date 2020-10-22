from xml.dom import minidom
import operator
import statistics
import numpy


# First fixed column overlap then row overlap

class RepairSegments:

    __segments: list
    __avg_paragraph_width: float
    __threshold: int

    def __init__(self, segments: list, threshold: int = 10):
        self.__segments = segments
        self.__threshold = threshold
        self.__analyze_coordinates()

    def __analyze_coordinates(self):
        sum_width = 0
        all_para = []
        for segment in self.__segments:
            all_para.append(segment[2]-segment[0])
        self.__avg_paragraph_width = statistics.median(all_para)
        print("Avg. paragraph width: "+(str(self.__avg_paragraph_width)))

    def __need_repair(self, segment: list):
        seg_width = (segment[2] - segment[0])
        min_width = self.__avg_paragraph_width-self.__threshold
        max_width = self.__avg_paragraph_width+self.__threshold

        if seg_width > max_width:
            return True
        return False

    def repair_columns(self):
        for segment in self.__segments:
            if self.__need_repair(segment):
                cur_seg_width = (segment[2]-segment[0])
                segment[2] = segment[0]+(cur_seg_width/2)-5
                self.__add_segment(segment[0]+(cur_seg_width/2)+5, segment[1], segment[2]+(cur_seg_width/2), segment[3], segment[4])
        return self.__segments

        # [x, y, x2, y2, lines]


    def repair_rows(self, range_span: int = 50):
        segments_to_remove = []
        for segment in self.__segments:
            x = segment[0]
            for subsegment in self.__segments:
                if segment is not subsegment:
                    if (x-range_span) <= subsegment[0] <= (x+range_span):
                        # hvis begge y koordinater ligger indenfor segment: slet lille alto_segment_lib
                        if segment[1] <= subsegment[1] <= segment[3] and segment[1] <= subsegment[3] <= segment[3]:
                            self.__segments.remove(subsegment)
                        # hvis subsegment ligger Segment med samme x-koordinater: flyt y-koordinat
                        elif segment[1] <= subsegment[1] <= segment[3]:
                            subsegment[1] = segment[3]
                        elif segment[1] <= subsegment[3] <= segment[3]:
                            subsegment[3] = segment[1]
                    # hvis subsegment ligger Segment med forskellige x-koordinater: split op i mindre bokse
                    elif (segment[1] <= subsegment[1] <= segment[3] or segment[1] <= subsegment[3] <= segment[3]) and (segment[0] <= subsegment[0] <= segment[2] or segment[0] <= subsegment[2] <= segment[2]):
                        print("segment 1:" + str(segment[1]) + " Segment 2:" + str(subsegment[1]) + "\n")

                        lines: list = segment[4]
                        grouped_lines = []
                        counter: int = 0

                        print(len(lines))

                        while counter < (len(lines)-1):
                            line = lines[counter]

                            length = (int(line[2]) - int(line[0]))
                            line1_changed = False
                            line2_changed = False

                            if len(lines)-1 >= counter + 1:
                                next_line = lines[counter + 1]
                                next_line_length = next_line[2]-next_line[0]

                                if next_line_length not in range(int(round(length*0.7)), int(round(length*1.3))):
                                    #print("line 1 changed: " + str(next_line_length) + str(length))
                                    line1_changed = True

                                if len(lines)-1 > counter + 2:
                                    next_line2 = lines[counter + 2]
                                    next_line2_length = next_line2[2]-next_line2[0]

                                    if next_line2_length not in range(int(round(next_line_length*0.7)), int(round(next_line_length*1.3))):
                                        #print("line 2 changed:")
                                        line2_changed = True

                            if line1_changed and line2_changed:
                                #print("New box!:" + str(lines) + "\n")
                                grouped_lines.append(line)
                                grouped_lines.append(lines[counter + 1])
                                new_coordinates = self.find_split_coordinates(grouped_lines)
                                new_coordinates.append(grouped_lines.copy())
                                self.__add_segment(new_coordinates[0], new_coordinates[1], new_coordinates[2], new_coordinates[3], new_coordinates[4])
                                grouped_lines.clear()
                                counter += 1
                            else:
                                grouped_lines.append(line)

                            counter += 1
                            print(counter)


        return self.__segments

    def __add_segment(self, x, y, x2, y2, lines):
        self.__segments.append([x, y, x2, y2, lines])

    def get_avg_column_width(self):
        return self.__avg_paragraph_width

    def find_split_coordinates(self, grouped_lines_split: list):
        box_height = 0
        box_width = 0
        coordinates = []
        coordinates.append(grouped_lines_split[0][0])
        coordinates.append(grouped_lines_split[0][1])

        # Finds width and height line and change box height and width accordingly
        for line in grouped_lines_split:
            line_width = line[2] - line[0]
            box_height += line[3] - line[1]
            if (line_width > box_width):
                box_width = line_width

        coordinates.append(coordinates[0]+box_width)
        coordinates.append(coordinates[1]+box_height)

        return coordinates

"""



                            if line1_changed and line2_changed:
                                grouped_lines.append(line)
                                grouped_lines.append(lines[counter + 1])
                                new_coordinates = self.find_split_coordinates(grouped_lines)
                                new_coordinates.append(grouped_lines)
                                self.__add_segment(new_coordinates[0], new_coordinates[1], new_coordinates[2], new_coordinates[3], new_coordinates[4])
                                grouped_lines.clear()
                                counter += 1
                            else:
                                grouped_lines.append(line)

                        ## linje 1 er større og 2 større: færdig blok -> start ny
                        # linje 1 er mindre og 2 større: tale om færdig sætning: tilføj også 1 [Samme blok]
                        ## linje 1 er mindre og 2 mindre: færdig blok -> start ny
                        # linje 1 er større og 2 mindre: ??
                            counter += 1

                        if len(grouped_lines) > 0:
                            new_coordinates = self.find_split_coordinates(grouped_lines)
                            new_coordinates.append(grouped_lines)
                            self.__add_segment(new_coordinates[0], new_coordinates[1], new_coordinates[2], new_coordinates[3], new_coordinates[4])
                            grouped_lines.clear()
                            segments_to_remove.extend(segment)

        for del_segment in segments_to_remove:
            if del_segment in self.__segments:
                self.__segments.remove(del_segment)
        return self.__segments








"""
