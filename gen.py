# Ширина инструмента для корректировки
import math

TOOL_WIDTHS = {
    "RECT_5X30": 5.0,
    "RECT_5X80": 5.0,
    "RECT_5X50": 5.0,
    "RECT_3X10": 3.0
}
TOOL_LENGTHS = {
    "RECT_5X30": 30.0,
    "RECT_5X80": 80.0,
    "RECT_5X50": 50.0,
    "RECT_3X10": 10.0
}

class KOTCassette:
    def __init__(self, tape, length, width, stamp, thickness, quantity, drainage=True, mounting=True):
        self.tape = tape
        self.length = length
        self.width = width
        self.stamp = stamp
        self.thickness = thickness
        self.quantity = quantity
        self.drainage = drainage
        self.mounting = mounting
        self.tool_map = []
        self.result = []
        self.stert_x = None
        self.stert_y = None
        self.end_x = None
        self.end_y = None
        self.otv_x = None
        self.otv_y = None
        self.lengths = []


    def _coord(self, x, y, flag, punching=False):
        if punching:
            self.result.append(f"{x:16.8f}{y:16.8f}    {flag}   0")
            return
        if flag == 8:
            self.result.append(f"{x:16.8f}{y:16.8f}    {flag}   0")
            self.start_x = None
            self.start_y = None
            return
        else:
            if self.start_x is not None and self.start_y is not None:
                if flag == -1:
                    self.otv_x = x
                    self.otv_y = y
                    self.result.append(f"{x:16.8f}{y:16.8f}    {flag}   0")
                    return
                self.end_x = self.start_x
                self.end_y = self.start_y
                self.start_x = x
                self.start_y = y
                self.result.append(f"{x:16.8f}{y:16.8f}    {flag}   0")
            else:
                self.start_x = x
                self.start_y = y
                self.result.append(f"{x:16.8f}{y:16.8f}    {flag}   0")
            if self.end_x is not None and self.end_y is not None:
                # Определяем направление линии
                dx = self.start_x - self.end_x
                dy = self.start_y - self.end_y

                if abs(dx) > abs(dy):
                    if dx > 0:
                        direction = "left"
                    else:
                        direction = "right"
                else:
                    if dy > 0:
                        direction = "down"
                    else:
                        direction = "up"
            else:
                direction = None

            self.add_tool_map(
                self.start_x,
                self.start_y,
                self.end_x,
                self.end_y,
                self.otv_x,
                self.otv_y,
                direction
                )
            self.otv_x = None
            self.otv_y = None


    def add_tool_map(self, start_x, start_y, end_x, end_y, otv_x, otv_y, direction):
        if start_x is None or start_y is None:
            return  # если нет начальной точки — ничего не делаем

        if otv_x is not None and otv_y is not None:
            # Это пробивка отверстия
            tool = "RND_2_MT"
            punch = "STRIKE"
            step = None
            orientation = None
            start_x = otv_x
            start_y = otv_y
            end_x = None
            end_y = None
        elif end_x is not None and end_y is not None:
            # Это линия или контур
            dx = end_x - start_x
            dy = end_y - start_y
            length = (dx ** 2 + dy ** 2) ** 0.5
            self.lengths.append(length)
            orientation = 0 if abs(dy) < 0.001 else 90 if abs(dx) < 0.001 else None

            if 12 < length < 18:
                tool = "RECT_3X10"
                punch = "STRIKE"
                step = None
                if direction == "right":
                    if start_x < 50:
                        start_x += 9
                    else:
                        start_x += 8
                elif direction == "left":
                    if start_x < 50:
                        start_x -= 8
                    else:
                        start_x -= 9

            elif length == 18.5:
                tool = "RECT_5X30"
                punch = "STRIKE"
                step = None
                if direction == "right":
                    if start_x < 50:
                        start_x += 14
                    else:
                        start_x += 5
                elif direction == "left":
                    if start_x < 50:
                        start_x -= 5
                    else:
                        start_x -= 14

            elif 10.7 < length < 10.9:
                tool = "RECT_5X30"
                punch = "STRIKE"
                step = None
                if direction == "up":
                    if start_y < 50:
                        start_y -= 4.2 # левый низ
                    else:
                        start_y += 15 # левый верх
                elif direction == "down":
                    if start_y < 50:
                        start_y -= 15 # правый низ
                    else:
                        start_y += 4.2 # правый верх



            elif 32 < length < 80:
                tool = "RECT_5X30"
                punch = "NIBBLE"
                step = 29
                if direction == "up":
                    if start_y < 50:
                        start_y += 1
                        end_y += 1
                    else:
                        start_y -= 1
                        end_y -= 1
                elif direction == "down":
                    if start_y < 50:
                        start_y += 1
                        end_y += 1
                    else:
                        start_y -= 1
                        end_y -= 1
            else:
                tool = "RECT_5X50" if self.thickness == 0.7 else "RECT_5X80"
                punch = "NIBBLE"
                step = 49 if tool == "RECT_5X50" else 79
                if direction == "right":
                    start_x += 1
                    end_x -= 1
                elif direction == "left":
                    start_x -= 1
                    end_x += 1
                elif direction == "up":
                    start_y -= 1
                    end_y += 1
                elif direction == "down":
                    start_y += 1
                    end_y -= 1

            # Коррекция для NIBBLE — чтобы не вылазить за края
            if punch == "NIBBLE":
                tool_length = TOOL_LENGTHS.get(tool, 0)
                if direction == "right":
                    start_x += tool_length / 2
                    end_x -= tool_length / 2
                elif direction == "left":
                    start_x -= tool_length / 2
                    end_x += tool_length / 2
                elif direction == "up":
                    start_y += tool_length / 2
                    end_y -= tool_length / 2
                elif direction == "down":
                    start_y -= tool_length / 2
                    end_y += tool_length / 2
        else:
            return  # ничего не делаем, неполные данные

        self.tool_map.append(self.adjust_punch({
            "contour_punching": True,
            "type_punching": punch,
            "step": step,
            "tool": tool,
            "rotation": orientation,
            "x_start": start_x,
            "y_start": start_y,
            "x_end": end_x,
            "y_end": end_y,
            "direction": direction
        }))
    


    def adjust_punch(self, punch):
        tool_name = punch["tool"]
        tool_width = TOOL_WIDTHS.get(tool_name, 0.0)  # ширина инструмента
        offset_width = tool_width / 2.0

        if punch["type_punching"] not in ("STRIKE", "NIBBLE"):
            return punch  # пропускаем если не наш тип

        if "direction" not in punch:
            return punch  # Без направления не трогаем

        direction = punch["direction"]

        # Если пробивка одиночная (нет конца), пока не двигаем
        if punch["x_end"] is None or punch["y_end"] is None:
            return punch

        # Смещаем координаты в зависимости от направления
        if direction == "right":
            punch["y_start"] -= offset_width
            punch["y_end"] -= offset_width
        elif direction == "left":
            punch["y_start"] += offset_width
            punch["y_end"] += offset_width
        elif direction == "up":
            punch["x_start"] += offset_width
            punch["x_end"] += offset_width
        elif direction == "down":
            punch["x_start"] -= offset_width
            punch["x_end"] -= offset_width

        return punch

    def _add(self, line):
        self.result.append(line)

    def _draw_hole(self, center_x, center_y, vertical=False, paint_hole=False):
        if paint_hole:
            self._coord(center_x - 2, center_y, 9, True)
            self._coord(center_x - 2, center_y, 0, True)
            self._coord(center_x, center_y, -1, True)
            self._coord(center_x - 2, center_y, 0, True)
            self.tool_map.append({
                "contour_punching": False,
                "type_punching": "STRIKE",
                "step": None,
                "tool": "RND_4",  # круглая пробивка Ø4
                "rotation": 0.0,
                "x_start": center_x,
                "y_start": center_y,
                "x_end": None,
                "y_end": None
            })
            return
        # Размеры половинок (относительно центра)
        half_length = 2.5
        x1 = center_x - half_length
        x2 = center_x + half_length
        y1 = center_y - half_length
        y2 = center_y + half_length
        if vertical:
            # Вытянут по Y
            self._coord(x1, y2, 9, True)
            self._coord(x1, y2, 0, True)
            self._coord(x1, y1, 0, True)
            self._coord(center_x, y1, -1, True)
            self._coord(x2, y1, 0, True)
            self._coord(x2, y2, 0, True)
            self._coord(center_x, y2, -1, True)
            self._coord(x1, y2, 0, True)

        else:
            # Вытянут по X (как изначально)
            self._coord(x1, y1, 9, True)
            self._coord(x1, y1, 0, True)
            self._coord(x2, y1, 0, True)
            self._coord(x2, center_y, -1, True)
            self._coord(x2, y2, 0, True)
            self._coord(x1, y2, 0, True)
            self._coord(x1, center_y, -1, True)
            self._coord(x1, y1, 0, True)
        if vertical:
            rotation = 90.0
        else:
            rotation = 0.0

        self.tool_map.append({
        "contour_punching": False,
        "type_punching": "STRIKE",
        "step": None,
        "tool": "OBR_5X10",
        "rotation": rotation,
        "x_start": center_x,
        "y_start": center_y,
        "x_end": None,
        "y_end": None
    })

    def _bottom_block(self):
        x1 = 0.0
        x2 = 18.5
        x3 = 35.25
        x4 = 36.25
        x5 = round(self.length + 36.25, 8)
        x6 = round(self.length + 37.25, 8)
        x7 = round(self.length + 54.0, 8)
        x8 = round(self.length + 72.5, 8)

        y1 = 26.15
        y2 = round(self.width + 46.35, 8)
        y3 = round(self.width + 35.55, 8)
        y4 = round(self.width + 36.55, 8)
        y5 = round(self.width + 72.5, 8)

        self._coord(x1, y1, 8)
        self._coord(x1, y1, 0)
        self._coord(x1, y2, 0)
        self._coord(x2, y2, 0)
        self._coord(x2, y3, 0)
        self._coord(x3, y3, 0)
        self._coord(x4, y3, -1)
        self._coord(x4, y4, 0)
        self._coord(x4, y5, 0)
        self._coord(x5, y5, 0)
        self._coord(x5, y4, 0)
        self._coord(x5, y3, -1)
        self._coord(x6, y3, 0)
        self._coord(x7, y3, 0)
        self._coord(x7, y2, 0)
        self._coord(x8, y2, 0)
        self._coord(x8, y1, 0)
        self._coord(x7, y1, 0)
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
        self._coord(x2, y1, 0)
        self._coord(x1, y1, 0)

    def _tool_block(self):
        """
        Создание блока инструментов на основе карты пробивки self.tool_map.
        Внутренние пробивки нумеруются от 0, контур — последним.
        """
        # Разделим пробивки на внутренние и контурные
        internal_punchings = [p for p in self.tool_map if not p["contour_punching"]]
        contour_punchings = [p for p in self.tool_map if p["contour_punching"]]

        # Сначала обрабатываем внутренние пробивки
        for index, punch in enumerate(internal_punchings):
            self._add("PARTNO 0")
            self._add("TOOL")
            self._add(f"{punch['tool']} {index} 32128")
            self._add("ROTATION")
            rotation = punch['rotation'] if punch['rotation'] is not None else 0.0
            self._add(f"{rotation:10.4f}")

            if punch['type_punching'] == "STRIKE":
                self._add("STRIKE")
                self._add(f"{punch['x_start']:.8f}    {punch['y_start']:.8f}    99      0       0")
            elif punch['type_punching'] == "NIBBLE":
                self._add("NIBBLE")
                self._add(f"{punch['step']:.4f}")
                self._add(f"{punch['x_start']:.8f}    {punch['y_start']:.8f}    0       0")
                self._add(f"{punch['x_end']:.8f}    {punch['y_end']:.8f}    0       0")
                self._add("0.00000000      0.00000000      99      0")

        # Теперь контурные пробивки идут с продолжением индексации
        contour_index = len(internal_punchings)
        for punch in contour_punchings:
            self._add("PARTNO 0")
            self._add("TOOL")
            self._add(f"{punch['tool']} {contour_index} 32128")
            self._add("ROTATION")
            rotation = punch['rotation'] if punch['rotation'] is not None else 0.0
            self._add(f"{rotation:10.4f}")

            if punch['type_punching'] == "STRIKE":
                self._add("STRIKE")
                self._add(f"{punch['x_start']:.8f}    {punch['y_start']:.8f}    99      0       0")
            elif punch['type_punching'] == "NIBBLE":
                self._add("NIBBLE")
                self._add(f"{punch['step']:.4f}")
                self._add(f"{punch['x_start']:.8f}    {punch['y_start']:.8f}    0       0")
                self._add(f"{punch['x_end']:.8f}    {punch['y_end']:.8f}    0       0")
                self._add("0.00000000      0.00000000      99      0")

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
            self._draw_hole(46.25, 9, paint_hole=not self.mounting)
            self._draw_hole(self.length + 26.25, 9, paint_hole=not self.mounting)
            self._draw_hole(46.25, self.width + 63.5, paint_hole=not self.mounting)
            self._draw_hole(self.length + 26.25, self.width + 63.5, paint_hole=not self.mounting)
            if self.drainage:
                #дренажные отверстия
                self._draw_hole(106.25, 26)
                self._draw_hole(self.length - 33.75, 26)
            if self.length > 1499 and self.mounting:
                #монтажные отверстия
                self._draw_hole(self.length/3 + 36.25, 9)
                self._draw_hole(self.length/1.5 + 36.25, 9)
                self._draw_hole(self.length/3 + 36.25, self.width + 63.5)
                self._draw_hole(self.length/1.5 + 36.25, self.width + 63.5)
                if self.drainage:
                    #дренажные отверстия
                    self._draw_hole(self.length/2 + 36.25, 26)
            elif self.length > 699 and self.mounting:
                #монтажные отверстия
                self._draw_hole(self.length/2 + 36.25, 9)
                self._draw_hole(self.length/2 + 36.25, self.width + 63.5)
        else:
            #монтажные отверстия
            self._draw_hole(9, 51.95, vertical=True, paint_hole=not self.mounting)
            self._draw_hole(self.length + 63.5, 51.95, vertical=True, paint_hole=not self.mounting)
            self._draw_hole(9, self.width + 20.55, vertical=True, paint_hole=not self.mounting)
            self._draw_hole(self.length + 63.5, self.width + 20.55, vertical=True, paint_hole=not self.mounting)
            if self.drainage:
                #дренажные отверстия
                self._draw_hole(106.25, 26)
                self._draw_hole(self.length - 33.75, 26)
                if self.length > 1499:
                    #дренажные отверстия
                    self._draw_hole(self.length/2 + 36.25, 26)
            if self.width > 1499 and self.mounting:
                #монтажные отверстия
                self._draw_hole(9, 9, vertical=True)
                self._draw_hole(self.length + 63.5, 9, vertical=True)
                self._draw_hole(9, self.width + 63.5 + 36.25, vertical=True)
                self._draw_hole(self.length + 63.5, self.width + 63.5 + 36.25, vertical=True)
            elif self.width > 699 and self.mounting:
                #монтажные отверстия
                self._draw_hole(9, self.width/2, vertical=True)
                self._draw_hole(self.length + 63.5, self.width/2 + 36.25, vertical=True)

        self._bottom_block()
        self._postprocessing_block()
        self._tool_block()
        #print(self.tool_map)
        print(self.lengths)

        return "\n".join(self.result)


if __name__ == "__main__":
    example = KOTCassette("kotvo", 1300, 750, "Zink", "0.7", 10)
    print(example.generate())
