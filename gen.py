class KOTCassette:
    def __init__(self, tape, length, width, stamp, thickness, quantity, drainage=True):
        self.tape = tape
        self.length = length
        self.width = width
        self.stamp = stamp
        self.thickness = thickness
        self.quantity = quantity
        self.drainage = drainage
        self.result = []

    def _coord(self, x, y, flag):
        self.result.append(f"{x:16.8f}{y:16.8f}    {flag}   0")

    def _add(self, line):
        self.result.append(line)

    def _draw_hole(self, center_x, center_y, vertical=False):
        # Размеры половинок (относительно центра)
        half_length = 2.5
        x1 = center_x - half_length
        x2 = center_x + half_length
        y1 = center_y - half_length
        y2 = center_y + half_length
        if vertical:
            # Вытянут по Y
            self._coord(x1, y1, 9)
            self._coord(x1, y1, 0)
            self._coord(x1, y2, 0)
            self._coord(center_x, y2, 1)
            self._coord(x2, y2, 0)
            self._coord(x2, y1, 0)
            self._coord(center_x, y1, 1)
            self._coord(x1, y1, 0)
        else:
            # Вытянут по X (как изначально)
            self._coord(x1, y1, 9)
            self._coord(x1, y1, 0)
            self._coord(x2, y1, 0)
            self._coord(x2, center_y, -1)
            self._coord(x2, y2, 0)
            self._coord(x1, y2, 0)
            self._coord(x1, center_y, -1)
            self._coord(x1, y1, 0)
            

    def _bottom_block(self):
        x1 = 0.0
        x2 = 18.5
        x3 = 35.25
        x4 = 36.25
        x5 = round(self.length + 36.25, 8)

        y_start = 26.15
        y_end = round(self.width + 46.35, 8)
        y_mid = round(self.width + 35.55, 8)
        y_top = round(self.width + 36.55, 8)
        y_max = round(self.width + 72.5, 8)

        self._coord(x1, y_start, 8)
        self._coord(x1, y_start, 0)
        self._coord(x1, y_end, 0)
        self._coord(x2, y_end, 0)
        self._coord(x2, y_mid, 0)
        self._coord(x3, y_mid, 0)
        self._coord(x4, y_mid, -1)
        self._coord(x4, y_top, 0)
        self._coord(x4, y_max, 0)
        self._coord(x5, y_max, 0)
        self._coord(x5, y_top, 0)
        self._coord(x5, y_mid, -1)
        x6 = round(self.length + 37.25, 8)
        x7 = round(self.length + 54.0, 8)
        x8 = round(self.length + 72.5, 8)
        self._coord(x6, y_mid, 0)
        self._coord(x7, y_mid, 0)
        self._coord(x7, y_end, 0)
        self._coord(x8, y_end, 0)
        self._coord(x8, y_start, 0)
        self._coord(x7, y_start, 0)
        self._coord(x7, 36.95, 0)
        self._coord(x6, 36.95, 0)
        self._coord(x5, 36.95, -1)
        self._coord(x5, 35.95, 0)
        self._coord(x5, 0.0, 0)
        self._coord(x4, 0.0, 0)
        self._coord(x4, 35.95, 0)
        self._coord(x4, 36.95, -1)
        self._coord(x3, 36.95, 0)
        self._coord(x2, 36.95, 0)
        self._coord(x2, y_start, 0)
        self._coord(x1, y_start, 0)

    def _tool_block(self):
        x = round(self.length + 36.25, 8)
        y = round(self.width + 35.55, 8)
        self._add("PARTNO 0")
        self._add("TOOL")
        self._add("RND_2_MT 8 32128")
        self._add("ROTATION")
        self._add("   0.0000")
        self._add("STRIKE")
        self._add(f"{x:.8f}    {y:.8f}    99      0       0")

    def _postprocessing_block(self):
        self._add("0.0 0.0 99 0")
        self._add("UNITS 1")
        self._add(f"PART_SIZE {self.length + 72.5:.8f} {self.width + 72.5:.8f}")
        self._add("VERSION_NUMBER 7")
        self._add("STATE_FLAGS 0")
        self._add("MIRRORED_PART_NAME")
        self._add("SING_PART_DESTR_PLATE_SIZES 0.00000000 0.00000000")
        self._add("ASSEMBLY")
        self._add("CUSTOMER_NAME")
        self._add("BENDING_MODE 0")
        self._add("PART_AREAS 0.00000000 0.00000000 0.00000000 0.00000000")
        self._add("(")
        self._add("H(")
        self._add("3015389267")
        self._add("68")
        self._add("0")
        self._add("H)")
        self._add(")")
        self._add("(")
        self._add("H(")
        self._add("1997006329")
        self._add("28")
        self._add("0")
        self._add("H)")
        self._add(")")
        self._add(f"MATERIAL {self.stamp} {self.thickness}")
        self._add("9_INCH_LENS 0")
        self._add("MICROJOINT 0.5")
        self._add("NEST_PAR 0 0  0 0 1 0")
        self._add("SECTION_PAR 0 0")
        self._add("BOUNDARY_TYPE 0")
        self._add("PARTING_TOOL_WIDTH 5 5")
        self._add("EXTRA_HEIGHT 0")
        self._add("MACHINING-MODE_SETTINGS 1 0 0 0 0")
        self._add("MODE 3")
        self._add("REVISION")
        self._add("ALIAS")
        self._add(f"QUANTITY {self.quantity}")
        self._add("CONTROLLER_INDEX 20")

    def generate(self):
        self._add("DRAWING")
        self._add(f"{self.tape}_{self.length}x{self.width}_{self.quantity}")

        if self.tape != "kotvo":
            #монтажные отверстия
            self._draw_hole(46.25, 9)
            self._draw_hole(self.length + 26.25, 9)
            self._draw_hole(46.25, self.width + 63.5)
            self._draw_hole(self.length + 26.25, self.width + 63.5)
            #дренажные отверстия
            self._draw_hole(106.25, 26)
            self._draw_hole(self.length - 33.75, 26)
            if self.length > 1499:
                #монтажные отверстия
                self._draw_hole(self.length/3 + 36.25, 9)
                self._draw_hole(self.length/1.5 + 36.25, 9)
                self._draw_hole(self.length/3 + 36.25, self.width + 63.5)
                self._draw_hole(self.length/1.5 + 36.25, self.width + 63.5)
                #дренажные отверстия
                self._draw_hole(self.length/2 + 36.25, 26)
            elif self.length > 699:
                #монтажные отверстия
                self._draw_hole(self.length/2 + 36.25, 9)
                self._draw_hole(self.length/2 + 36.25, self.width + 63.5)
        else:
            #монтажные отверстия
            self._draw_hole(9, 51.95, vertical=True)
            self._draw_hole(self.length + 63.5, 51.95, vertical=True)
            self._draw_hole(9, self.width + 20.55, vertical=True)
            self._draw_hole(self.length + 63.5, self.width + 20.55, vertical=True)
            #дренажные отверстия
            self._draw_hole(106.25, 26)
            self._draw_hole(self.length - 33.75, 26)
            if self.length > 1499:
                #дренажные отверстия
                self._draw_hole(self.length/2 + 36.25, 26)
            if self.width > 1499:
                #монтажные отверстия
                self._draw_hole(9, 9, vertical=True)
                self._draw_hole(self.length + 63.5, 9, vertical=True)
                self._draw_hole(9, self.width + 63.5 + 36.25, vertical=True)
                self._draw_hole(self.length + 63.5, self.width + 63.5 + 36.25, vertical=True)
            elif self.width > 699:
                #монтажные отверстия
                self._draw_hole(9, self.width/2, vertical=True)
                self._draw_hole(self.length + 63.5, self.width/2 + 36.25, vertical=True)

        self._bottom_block()
        self._postprocessing_block()
        #self._tool_block()


        return "\n".join(self.result)


if __name__ == "__main__":
    example = KOTCassette("kot", 1700, 800, "Zink", "0.7", 10)
    print(example.generate())
