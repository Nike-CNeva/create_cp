# Новый main.py с интеграцией генератора кассет

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
from gen import Cassette

# Старые функции create_cp_kzt_701 и им подобные НЕ трогаем, оставляем!

class CreateCPFile:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Создание файлов заготовок кассет v2.0")
        window_width = 400
        window_height = 250
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        title_label = tk.Label(self.window, text="Создать файлы заготовок кассет", font=("Arial", 16))
        title_label.pack(pady=10)

        self.manual_button = tk.Button(self.window, text="Создать вручную", width=40, height=2, command=self.create_manual)
        self.manual_button.pack(pady=5)

        self.excel_button = tk.Button(self.window, text="Создать из Excel", width=40, height=2, command=self.select_parameters)
        self.excel_button.pack(pady=5)

        self.exit_button = tk.Button(self.window, text="Выход", width=40, height=2, command=self.exit_program)
        self.exit_button.pack(pady=5)

        ps = tk.Label(self.window, text="Необходимые поля в таблице Exel: высота, ширина, ширина2, количество")
        ps.pack(pady=20)

        self.window.mainloop()

    def select_parameters(self):
        # Окно для выбора параметров
        param_window = tk.Toplevel(self.window)
        param_window.title("Выберите параметры кассет")
        param_window.geometry("300x400")

        tk.Label(param_window, text="Тип кассеты:").pack()
        self.type_var = tk.StringVar(value="kot")
        type_menu = ttk.Combobox(param_window, textvariable=self.type_var, values=["kot", "kotvo", "kzt"])
        type_menu.pack(pady=5)

        tk.Label(param_window, text="Толщина металла (мм):").pack()
        self.thickness_var = tk.StringVar(value="0.7")
        thickness_menu = ttk.Combobox(param_window, textvariable=self.thickness_var, values=["0.7", "1.0", "1.2"])
        thickness_menu.pack(pady=5)

        tk.Label(param_window, text="Руст (мм):").pack()
        self.rust_var = tk.StringVar(value="20")
        rust_entry = tk.Entry(param_window, textvariable=self.rust_var)
        rust_entry.pack(pady=5)

        tk.Label(param_window, text="Глубина (мм):").pack()
        self.depth_var = tk.StringVar(value="20")
        depth_entry = tk.Entry(param_window, textvariable=self.depth_var)
        depth_entry.pack(pady=5)

        self.drainage_var = tk.BooleanVar(value=True)
        drainage_check = tk.Checkbutton(param_window, text="Дренажные отверстия", variable=self.drainage_var)
        drainage_check.pack(pady=5)

        self.mounting_var = tk.BooleanVar(value=True)
        mounting_check = tk.Checkbutton(param_window, text="Монтажные отверстия", variable=self.mounting_var)
        mounting_check.pack(pady=5)

        start_button = tk.Button(param_window, text="Выбрать Excel файл", command=lambda: [self.create_from_excel(), param_window.destroy()])
        start_button.pack(pady=10)

    def create_from_excel(self):
        file_path = filedialog.askopenfilename(title="Выберите Excel файл", filetypes=[("Excel files", "*.xlsx *.xls")])
        if not file_path:
            return

        save_folder = filedialog.askdirectory(title="Выберите папку для сохранения файлов")
        if not save_folder:
            return

        success = []
        errors = []

        try:
            df = pd.read_excel(file_path, engine='openpyxl')

            for index, row in df.iterrows():
                try:
                    width = int(row["высота"])
                    length_left = int(row["ширина"])
                    quantity = int(row["количество"])

                    length_right = row.get("ширина2")

                    if not (pd.isna(length_right) or str(length_right).strip() == ""):
                        # Угловая кассета
                        length_right = int(length_right)
                        length = length_left + length_right - 2

                        if not (100 <= width <= 3000) or not (50 <= length_left) or not (50 <= length_right) or not (98 <= length <= 3000):
                            errors.append(f"ukot_{width}x{length_left}x{length_right}_{quantity}")
                            continue

                        # Меняем "kot" → "ukot", "kotvo" → "ukotvo"
                        tape_type = self.type_var.get().replace("kotvo", "ukotvo").replace("kot", "ukot")

                        cassette = Cassette(
                            tape=tape_type,
                            length=length,
                            width=width,
                            stamp="Zink",
                            thickness=float(self.thickness_var.get()),
                            quantity=quantity,
                            drainage=False,
                            mounting=self.mounting_var.get(),
                            depth=int(self.depth_var.get()),
                            rust=int(self.rust_var.get()),
                            length_left=length_left,
                            length_right=length_right
                        )

                        filename = f"{cassette.tape}_{width}x{length_left}x{length_right}_{quantity}.cp"

                    else:
                        # Прямая кассета
                        length = length_left

                        if not (100 <= width <= 3000) or not (100 <= length <= 3000):
                            errors.append(f"{self.type_var.get()}_{width}x{length}_{quantity}")
                            continue

                        cassette = Cassette(
                            tape=self.type_var.get(),
                            length=length,
                            width=width,
                            stamp="Zink",
                            thickness=float(self.thickness_var.get()),
                            quantity=quantity,
                            drainage=self.drainage_var.get(),
                            mounting=self.mounting_var.get(),
                            depth=int(self.depth_var.get()),
                            rust=int(self.rust_var.get())
                        )

                        filename = f"{cassette.tape}_{width}x{length}_{quantity}.cp"

                    # Сохраняем CP-файл
                    filepath = os.path.join(save_folder, filename)
                    cp_text = cassette_generate_cp(cassette)

                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(cp_text)

                    success.append(filename)

                except Exception as e:
                    errors.append(f"Ошибка в строке {index+2}: {e}")  # +2 потому что Excel считает с 1 и есть заголовок

            self.show_results(success, errors)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обработке файла: {e}")

    def show_results(self, success, errors):
        result_window = tk.Toplevel(self.window)
        result_window.title("Результаты создания кассет")
        result_window.geometry("600x400")

        text_area = tk.Text(result_window, wrap="word")
        scrollbar = tk.Scrollbar(result_window, command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)

        text_area.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        text_area.insert(tk.END, "✅ Успешно созданы файлы:\n")
        for name in success:
            text_area.insert(tk.END, f"- {name}\n")

        text_area.insert(tk.END, "\n❌ Ошибки при создании файлов:\n")
        for name in errors:
            text_area.insert(tk.END, f"- {name}\n")

        text_area.config(state=tk.DISABLED)

    def create_manual(self):
        messagebox.showinfo("Информация", "Ручное создание временно недоступно. Отдыхай, ты заслужил!")

    def exit_program(self):
        self.window.destroy()


def cassette_generate_cp(cassette):
    cassette.generate()
    return "\n".join(cassette.result)


if __name__ == "__main__":
    CreateCPFile()
