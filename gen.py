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

class Cassette:
    def __init__(self, tape, length, width, stamp, thickness, quantity, drainage=True, mounting=True, depth=20.0, rust=20.0, length_left=None, length_right=None, length_center = None):
        self.tape = tape
        self.length = length
        self.length_left = length_left
        self.length_right = length_right
        self.length_center = length_center
        self.width = width
        self.depth = depth  # глубина кассеты
        self.rust = rust    # ширина руста
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
            length = round((dx ** 2 + dy ** 2) ** 0.5, 8)
            self.lengths.append(length)
            orientation = 0 if abs(dy) < 0.001 else 90 if abs(dx) < 0.001 else None
            
            if length == 2.0:
                return
            
            if length == 16.75 or length == 18.75:
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
            
            elif length == 9 or length == 8:
                tool = "RECT_3X10"
                punch = "STRIKE"
                step = None
                if start_y > 10:
                    if direction == "up":
                        start_y += 5

                    elif direction == "down":
                        start_y -= 4
                else:
                    if direction == "up":
                        start_y += 3

                    elif direction == "down":
                        start_y -= 5

            elif length == 10:
                tool = "RECT_3X10"
                punch = "STRIKE"
                step = None
                if direction == "up":
                    start_y += 6

                elif direction == "down":
                    start_y -= 4
            
            elif length == 18.0:
                tool = "RECT_3X10"
                punch = "NIBBLE"
                step = 8
                if start_y > 25:
                    if direction == "up":
                        end_y -= 1
                    elif direction == "down":
                        start_y -= 1
                else:
                    if direction == "up":
                        start_y += 1
                    elif direction == "down":
                        end_y += 1
            
            elif 26.64 < length < 26.65:
                tool = "RECT_3X10"
                punch = "NIBBLE"
                step = 8
                if direction == "left":
                    if start_x < self.length_left + self.depth + self.rust - 4.75:
                        start_x += 3.16462835
                        end_x -= 0.36131344
                        start_y += 2.35764318
                        end_y -= 3.89428215
                        orientation = 136
                    else:
                        start_x += 0.36131344
                        end_x -= 3.16462835
                        start_y -= 3.89428215
                        end_y += 2.35764318
                        orientation = 44
                elif direction == "right":
                    if start_x < self.length_left + self.depth + self.rust - 4.75:
                        start_x -= 0.36131344
                        end_x += 3.16462835
                        start_y += 3.89428215
                        end_y -= 2.35764318
                        orientation = 44
                    else:
                        start_x -= 3.16462835
                        end_x += 0.36131344
                        start_y -= 2.35764318
                        end_y += 3.89428215
                        orientation = 136
                
            elif length == 13.0:
                tool = "RECT_3X10"
                punch = "NIBBLE"
                step = 8
                start_x += 1
                end_x -= 1
            
            elif length == 14.18:
                tool = "RECT_3X10"
                punch = "NIBBLE"
                step = 8
                if start_x < 20:
                    start_x -= 1
                else:
                    end_x += 1
            
            elif 18.9 < length < 19.0:
                tool = "RECT_3X10"
                punch = "NIBBLE"
                step = 8
                if start_x < 50:
                    start_x += 7.2312
                    end_x -= 8.7316746
                    start_y -= 7.294
                    end_y += 7.696
                    orientation = 330
                else:
                    start_x -= 0.7772254
                    end_x += 2.2777
                    start_y += 2.2057
                    end_y -= 1.8043
                    orientation = 30
            
            elif length == 20.0:
                tool = "RECT_3X10"
                punch = "NIBBLE"
                step = 8
                if start_x < 60:
                    end_x += 1
                else:
                    start_x -= 1

                
            elif length == 21.0:
                tool = "TRIANGLE4"
                punch = "STRIKE"
                step = None
                if start_x < 50:
                    orientation = 30
                    start_x -= 4.1112
                    start_y -= 7.7452
                else:
                    orientation = 0
                    start_x += 4
                    start_y += 13.2846
            
            elif 20 < length < 30:
                tool = "RECT_3X10"
                punch = "NIBBLE"
                step = 8
                if self.tape == "kzt":
                    start_x -= 4
                    end_x += 4
                else:    
                    if direction == "right":
                        if start_x < 50:
                            start_x
                            end_x += 1
                        else:
                            start_x += 1
                            end_x 
                    elif direction == "left":
                        if start_x < 50:
                            start_x += 1
                            end_x 
                        else:
                            start_x 
                            end_x += 1
                        
            elif length == 31.5:
                tool = "RECT_3X10"
                punch = "NIBBLE"
                step = 8
                if start_x < 50:
                    start_y -= 1
                else:
                    end_y -= 1
            
                
            elif 18.6 < length < 18.7:
                tool = "TRIANGLE4"
                punch = "STRIKE"
                step = None
                if start_x < 50:
                    start_x -= 9.5047746
                    start_y += 10.1064
                    orientation = 60
                else:
                    start_x -= 6.7106
                    start_y += 0.87284242
                    orientation = 330
                
            elif length == 18.5:
                tool = "RECT_5X30"
                punch = "STRIKE"
                step = None
                if direction == "right":
                    if start_x < 50:
                        start_x += 14
                    else:
                        start_x += 4.5
                elif direction == "left":
                    if start_x < 50:
                        start_x -= 4.5
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

            elif length == 46:
                tool = "RECT_5X50"
                punch = "STRIKE"
                step = None
                if direction == "up":
                    start_y += 21
                elif direction == "down":
                    start_y -= 25
            
            elif 32 < length < 50:
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
            elif length == 55:
                tool = "RECT_5X50"
                punch = "NIBBLE"
                step = 49
                if start_x < 50:
                    start_x += 1
                    end_x
                else:
                    start_x
                    end_x -= 1
                
            elif 55 < length:
                tool = "RECT_5X50" if self.thickness == 0.7 else "RECT_5X80"
                punch = "NIBBLE"
                step = 49 if tool == "RECT_5X50" else 79
                if self.tape != "kzt":
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
                else:
                    if direction == "right":
                        start_x -= 1
                        end_x += 1
                    elif direction == "left":
                        start_x += 1
                        end_x -= 1
                    elif direction == "up":
                        start_y -= 1
                        end_y += 1
                    elif direction == "down":
                        start_y += 1
                        end_y -= 1
            else:
                tool = "RECT_3X10"
                punch = "NIBBLE"
                step = 8
                
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

    def _bottom_block_kot(self):
        x1 = round(0.0, 8)
        x2 = round(self.rust - 1.5, 8)
        x3 = round(self.depth + self.rust - 4.75, 8)
        x4 = round(self.depth + self.rust - 3.75, 8)
        x5 = round(self.length + self.depth + self.rust - 3.75, 8)
        x6 = round(self.length + self.depth + self.rust - 4.75, 8)
        x7 = round(self.length + (self.depth * 2) + self.rust - 6, 8)
        x8 = round(self.length + ((self.depth + self.rust) * 2) - 7.5, 8)
        xu1 = round(self.length_left + self.depth + self.rust - 24.58980704, 8)
        xu2 = round(self.length_left + self.depth + self.rust - 5.42236681, 8)
        xu3 = round(self.length_left + self.depth + self.rust - 4.75, 8)
        xu4 = round(self.length_left + self.depth + self.rust - 4.07763319, 8)
        xu5 = round(self.length_left + self.depth + self.rust + 15.08980704, 8)
        
        y1 = round(self.depth - (self.rust / 2) + 16.15, 8)
        y2 = round(self.width + self.depth + (self.rust / 2) + 16.35, 8)
        y3 = round(self.width + self.depth + self.rust - 4.45, 8)
        y4 = round(self.width + self.depth + self.rust - 3.45, 8)
        y5 = round(self.width + ((self.depth + self.rust) * 2) - 7.5, 8)
        y6 = round(self.depth + self.rust - 3.05, 8)
        y7 = round(self.depth + self.rust - 4.05, 8)
        y8 = round(0.0, 8)
        yu1 = round(self.rust -2, 8)
        yu2 = round(self.depth + self.rust - 3.49021813, 8)
        yu3 = round(self.depth + self.rust - 2.75, 8)
        yu4 = round(self.width + self.depth + self.rust - 4.75, 8)
        yu5 = round(self.width + self.depth + self.rust - 4.00978187, 8)
        yu6 = round(self.width + (self.depth * 2) + self.rust - 5.5, 8)
        
        self._coord(x1, y1, 8)
        self._coord(x1, y1, 0)
        self._coord(x1, y2, 0)
        self._coord(x2, y2, 0)
        self._coord(x2, y3, 0)
        self._coord(x3, y3, 0)
        self._coord(x4, y3, -1)
        self._coord(x4, y4, 0)
        self._coord(x4, y5, 0)
        if self.tape == "ukot" or self.tape == "ukotvo":
            self._coord(xu1, y5, 0)
            self._coord(xu1, yu6, 0)
            self._coord(xu2, yu5, 0)
            self._coord(xu3, yu4, -1)
            self._coord(xu4, yu5, 0)
            self._coord(xu5, yu6, 0)
            self._coord(xu5, y5, 0)
        self._coord(x5, y5, 0)
        self._coord(x5, y4, 0)
        self._coord(x5, y3, -1)
        self._coord(x6, y3, 0)
        self._coord(x7, y3, 0)
        self._coord(x7, y2, 0)
        self._coord(x8, y2, 0)
        self._coord(x8, y1, 0)
        self._coord(x7, y1, 0)
        self._coord(x7, y6, 0)
        self._coord(x6, y6, 0)
        self._coord(x5, y6, -1)
        self._coord(x5, y7, 0)
        self._coord(x5, y8, 0)
        if self.tape == "ukot" or self.tape == "ukotvo":
            self._coord(xu5, y8, 0)
            self._coord(xu5, yu1, 0)
            self._coord(xu4, yu2, 0)
            self._coord(xu3, yu3, -1)
            self._coord(xu2, yu2, 0)
            self._coord(xu1, yu1, 0)
            self._coord(xu1, y8, 0)
        self._coord(x4, y8, 0)
        self._coord(x4, y7, 0)
        self._coord(x4, y6, -1)
        self._coord(x3, y6, 0)
        self._coord(x2, y6, 0)
        self._coord(x2, y1, 0)
        self._coord(x1, y1, 0)

    def _bottom_block_kzt(self):
        x1 = round(0.0, 8)
        x2 = round(13.0, 8)
        x3 = round(14.18, 8)
        x4 = round(self.depth + 9.1339746, 8)
        x5 = round(self.depth + 10, 8)
        x6 = round(self.depth + 10.6339746, 8)
        x7 = round(self.depth + 11.5, 8)
        x8 = round(self.depth + 12, 8)
        x9 = round(self.depth + 32, 8)
        x10 = round(self.depth + 66.5, 8)
        x11 = round(self.length / 2 + self.depth - 2.5, 8)
        x12 = round(self.length / 2 + self.depth + 22.5, 8)
        x13 = round(self.length + self.depth - 46.5, 8)
        x14 = round(self.length + self.depth - 12, 8)
        x15 = round(self.length + self.depth + 8, 8)
        x16 = round(self.length + self.depth + 8.5, 8)
        x17 = round(self.length + self.depth + 9.3660254, 8)
        x18 = round(self.length + self.depth + 10, 8)
        x19 = round(self.length + self.depth + 10.8660254, 8)
        x20 = round(self.length + (self.depth * 2) + 5.82, 8)
        x21 = round(self.length + (self.depth * 2) + 7, 8)
        x22 = round(self.length + (self.depth * 2) + 20, 8)
        x23 = round(self.length / 3 + self.depth - 2.5, 8)
        x24 = round(self.length / 3 + self.depth + 22.5, 8)
        x25 = round(self.length / 1.5 + self.depth - 2.5, 8)
        x26 = round(self.length / 1.5 + self.depth + 22.5, 8)
        

        y1 = round(0.0, 8)
        y2 = round(8.0, 8)
        y3 = round(self.depth - 2, 8) # нужно выстчитать при изменении на глубину отличную от 20
        y4 = round(self.depth - 1, 8)
        y5 = round(self.depth - 0.5, 8)
        y6 = round(self.depth + 9, 8)
        y7 = round(self.depth + 55, 8)
        y8 = round(self.width + self.depth + 0.5, 8)
        y9 = round(self.width + self.depth + 1, 8)
        y10 = round(self.width + self.depth + 1.5, 8)
        y11 = round(self.width + self.depth + 10.31495458, 8)
        y12 = round(self.width + (self.depth * 2) + 2.5, 8)
        y13 = round(self.width + (self.depth * 2) + self.rust + 14, 8)
        y14 = round(self.width + (self.depth * 2) + self.rust + 23, 8)
        
        self._coord(x1, y7, 8)
        self._coord(x1, y7, 0)
        self._coord(x1, y11, 0)
        self._coord(x2, y11, 0)
        self._coord(x4, y9, 0)
        self._coord(x5, y8, -1)
        self._coord(x5, y10, 0)
        self._coord(x5, y12, 0)
        self._coord(x8, y12, 0)
        self._coord(x8, y13, 0)
        self._coord(x9, y13, 0)
        self._coord(x9, y14, 0)
        if self.length > 1499:
            self._coord(x23, y14, 0)
            self._coord(x23, y13, 0)
            self._coord(x24, y13, 0)
            self._coord(x24, y14, 0)
            self._coord(x25, y14, 0)
            self._coord(x25, y13, 0)
            self._coord(x26, y13, 0)
            self._coord(x26, y14, 0)
        elif self.length > 699:
            self._coord(x11, y14, 0)
            self._coord(x11, y13, 0)
            self._coord(x12, y13, 0)
            self._coord(x12, y14, 0)
        self._coord(x14, y14, 0)
        self._coord(x14, y13, 0)
        self._coord(x15, y13, 0)
        self._coord(x15, y12, 0)
        self._coord(x18, y12, 0)
        self._coord(x18, y10, 0)
        self._coord(x18, y8, -1)
        self._coord(x19, y9, 0)
        self._coord(x21, y11, 0)
        self._coord(x22, y11, 0)
        self._coord(x22, y7, 0)
        self._coord(x20, y7, 0)
        self._coord(x20, y6, 0)
        self._coord(x17, y5, 0)
        self._coord(x16, y4, -1)
        self._coord(x16, y3, 0)
        self._coord(x16, y2, 0)
        self._coord(x13, y2, 0)
        self._coord(x13, y1, 0)
        self._coord(x10, y1, 0)
        self._coord(x10, y2, 0)
        self._coord(x7, y2, 0)
        self._coord(x7, y3, 0)
        self._coord(x7, y4, -1)
        self._coord(x6, y5, 0)
        self._coord(x3, y6, 0)
        self._coord(x3, y7, 0)
        self._coord(x1, y7, 0)

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

    def _hole_block_kot(self):
        x1 = round(9, 8)
        x2 = round(self.depth + self.rust + 6.25, 8)  
        x3 = round(self.depth + self.rust + 66.25, 8)
        x4 = round(self.length / 3 + self.depth + self.rust - 3.75, 8)
        x5 = round(self.length / 2 + self.depth + self.rust - 3.75, 8)
        x6 = round(self.length / 1.5 + self.depth + self.rust - 3.75, 8)
        x7 = round(self.length - (self.depth + self.rust - 6.25), 8)
        x8 = round(self.length + (self.depth + self.rust - 13.75), 8)
        x9 = round(self.length + ((self.depth + self.rust) * 2) - 16.5, 8)

        y1 = round(9, 8)
        y2 = round(self.depth + self.rust - 14, 8)
        y3 = round(self.depth + self.rust + 9.45, 8)
        y4 = round(self.width / 3 + self.depth + self.rust - 3.75, 8)
        y5 = round(self.width / 2 + self.depth + self.rust - 3.75, 8)
        y6 = round(self.width / 1.5 + self.depth + self.rust - 3.75, 8)
        y7 = round(self.width + (self.depth + self.rust - 16.95), 8)
        y8 = round(self.width + ((self.depth + self.rust) * 2) - 16.5, 8)

        if self.mounting == False:
            x1 += 1
            x2 += 5
            x8 -= 5
            x9 -= 1
            y1 += 1
            y3 += 5
            y7 -= 5
            y8 -= 1
            
        if self.tape != "kotvo":
            #монтажные отверстия
            self._draw_hole(x2, y1, paint_hole=not self.mounting)
            self._draw_hole(x8, y1, paint_hole=not self.mounting)
            self._draw_hole(x2, y8, paint_hole=not self.mounting)
            self._draw_hole(x8, y8, paint_hole=not self.mounting)
            if self.drainage:
                #дренажные отверстия
                self._draw_hole(x3, y2)
                self._draw_hole(x7, y2)
            if self.length > 1499 and self.mounting:
                #монтажные отверстия
                self._draw_hole(x4, y1)
                self._draw_hole(x6, y1)
                self._draw_hole(x4, y8)
                self._draw_hole(x6, y8)
                if self.drainage:
                    #дренажные отверстия
                    self._draw_hole(x5, y2)
            elif self.length > 699 and self.mounting:
                #монтажные отверстия
                self._draw_hole(x5, y1)
                self._draw_hole(x5, y8)
        else:
            #монтажные отверстия
            self._draw_hole(x1, y3, vertical=True, paint_hole=not self.mounting)
            self._draw_hole(x9, y3, vertical=True, paint_hole=not self.mounting)
            self._draw_hole(x1, y7, vertical=True, paint_hole=not self.mounting)
            self._draw_hole(x9, y7, vertical=True, paint_hole=not self.mounting)
            if self.drainage:
                #дренажные отверстия
                self._draw_hole(x3, y2)
                self._draw_hole(x7, y2)
                if self.length > 1499:
                    #дренажные отверстия
                    self._draw_hole(x5, y2)
            if self.width > 1499 and self.mounting:
                #монтажные отверстия
                self._draw_hole(x1, y4, vertical=True)
                self._draw_hole(x9, y4, vertical=True)
                self._draw_hole(x1, y6, vertical=True)
                self._draw_hole(x9, y6, vertical=True)
            elif self.width > 699 and self.mounting:
                #монтажные отверстия
                self._draw_hole(x1, y5, vertical=True)
                self._draw_hole(x9, y5, vertical=True)

    def _hole_block_kzt(self):
        x1 = round(self.depth + 19.5, 8)
        x2 = round(self.depth + 81.5, 8)  
        x3 = round(self.length / 2 + self.depth + 10, 8)
        x4 = round(self.length + self.depth - 61.5, 8)
        x5 = round(self.length + self.depth + 0.5, 8)
        x6 = round(self.depth + (self.length / 3) + 10, 8)
        x7 = round(self.depth + (self.length / 1.5) + 10, 8)

        y1 = round(self.depth / 2 + 3, 8)
        y2 = round(self.width + (self.depth * 2) + self.rust - 5.5, 8)

        #монтажные отверстия
        self._draw_hole(x1, y2)
        self._draw_hole(x5, y2)

        #дренажные отверстия
        self._draw_hole(x2, y1)
        self._draw_hole(x4, y1)
        
        if self.length > 1499:
            #монтажные отверстия
            self._draw_hole(x6, y2)
            self._draw_hole(x7, y2)

            #дренажные отверстия
            self._draw_hole(x3, y1)
            
        elif self.length > 699:
            #монтажные отверстия
            self._draw_hole(x3, y2)


    def generate(self):
        self._add("DRAWING")
        self._add(f"{self.tape}_{self.length}x{self.width}_{self.quantity}")
        if self.tape == "kzt":
            self._hole_block_kzt()
            self._bottom_block_kzt()
        else:
            self._hole_block_kot()
            self._bottom_block_kot()
        self._postprocessing_block()
        self._tool_block()
        #print(self.tool_map)
        print(self.lengths)

        return "\n".join(self.result)


if __name__ == "__main__":
    example = Cassette("ukot", 698, 580, "Zink", "1.0", 10, False, True, 20, 20, 300, 400)
    print(example.generate())
