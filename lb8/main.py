"""Лабораторная работа 8. Вариант 33."""
import math
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

folder = Path(__file__).resolve().parent
images = [None, None, None, None]
names = ["Исходное изображение", "Ближайший сосед", "Билинейная", "Бикубическая"]


def pixel(image, x, y):
    x = max(0, min(image.width - 1, x))
    y = max(0, min(image.height - 1, y))
    return image.getpixel((x, y))


def cubic_weights(t):
    # Кубический полином Лагранжа на узлах -1, 0, 1, 2.
    return [-t * (t - 1) * (t - 2) / 6,
            (t + 1) * (t - 1) * (t - 2) / 2,
            -(t + 1) * t * (t - 2) / 2,
            (t + 1) * t * (t - 1) / 6]


def interpolate(image, x, y, method):
    if method == 0:
        return pixel(image, math.floor(x + 0.5), math.floor(y + 0.5))
    left, top = math.floor(x), math.floor(y)
    a, b = x - left, y - top
    if method == 1:
        wx, wy = [1 - a, a], [1 - b, b]
        start = 0
    else:
        wx, wy = cubic_weights(a), cubic_weights(b)
        start = -1
    color = [0.0, 0.0, 0.0]
    for j in range(len(wy)):
        for i in range(len(wx)):
            value = pixel(image, left + start + i, top + start + j)
            weight = wx[i] * wy[j]
            for channel in range(3):
                color[channel] += value[channel] * weight
    return tuple(max(0, min(255, round(c))) for c in color)


def transform(image, matrix, method):
    a, b, c, d = matrix
    determinant = a * d - b * c
    if abs(determinant) < 1e-12:
        raise ValueError("Преобразование должно иметь обратную матрицу")
    w, h = image.size
    corners = [(a * x + b * y, c * x + d * y)
               for x in (-w / 2, w / 2) for y in (-h / 2, h / 2)]
    left = min(x for x, y in corners)
    top = min(y for x, y in corners)
    width = math.ceil(max(x for x, y in corners) - left - 1e-9)
    height = math.ceil(max(y for x, y in corners) - top - 1e-9)
    result = Image.new("RGB", (width, height), "white")
    for j in range(height):
        for i in range(width):
            u, v = left + i + 0.5, top + j + 0.5
            # Обратное отображение центров пикселей без пропусков.
            x = (d * u - b * v) / determinant + w / 2 - 0.5
            y = (-c * u + a * v) / determinant + h / 2 - 0.5
            if -0.5 <= x < w - 0.5 and -0.5 <= y < h - 0.5:
                result.putpixel((i, j), interpolate(image, x, y, method))
    return result


def show_img(number):
    if images[number] is None:
        boxes[number].config(image="", text="Нет изображения")
        return
    temp = images[number].copy()
    temp.thumbnail((390, 260))
    boxes[number].photo = ImageTk.PhotoImage(temp)
    boxes[number].config(image=boxes[number].photo, text="")


def open_img():
    path = filedialog.askopenfilename(initialdir=folder,
        filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp *.ppm *.pbm"),
                   ("Все файлы", "*.*")])
    if path:
        try:
            with Image.open(path) as image:
                source = image.convert("RGB")
            images[:] = [source, None, None, None]
            for i in range(4):
                show_img(i)
            status.config(text=f"Исходное изображение: {source.width} x {source.height}")
        except OSError:
            messagebox.showerror("Ошибка", "Не удалось открыть изображение")


def process(kind):
    if images[0] is None:
        messagebox.showwarning("Ошибка", "Сначала откройте изображение")
        return
    try:
        if kind == "scale":
            value = float(scale_entry.get())
            if not 0.25 <= value <= 2:
                raise ValueError("Масштаб должен быть от 0.25 до 2")
            matrix = (value, 0, 0, value)
            description = f"Масштаб {value}"
        elif kind == "rotate":
            value = float(angle_entry.get())
            if not math.isfinite(value):
                raise ValueError("Введите конечный угол")
            angle = math.radians(value % 360)
            matrix = (math.cos(angle), -math.sin(angle), math.sin(angle), math.cos(angle))
            description = f"Поворот {value} градусов по часовой стрелке"
        else:
            value = float(shear_entry.get())
            if not -1 <= value <= 1:
                raise ValueError("Скос должен быть от -1 до 1")
            matrix = (1, value, 0, 1)
            description = f"Скос {value}"
        status.config(text="Обработка...")
        status.update_idletasks()
        results = [transform(images[0], matrix, method) for method in range(3)]
        images[1:] = results
        for i in range(1, 4):
            show_img(i)
        status.config(text=f"{description}. Размер: {results[0].width} x {results[0].height}")
    except ValueError as error:
        status.config(text="Проверьте параметры")
        messagebox.showerror("Ошибка", str(error))


def write_pbm(image, path):
    gray = image.convert("L")
    with open(path, "w", encoding="ascii") as file:
        file.write(f"P1\n{image.width} {image.height}\n")
        for y in range(image.height):
            row = ["1" if gray.getpixel((x, y)) < 128 else "0"
                   for x in range(image.width)]
            for start in range(0, len(row), 35):
                file.write(" ".join(row[start:start + 35]) + "\n")


def save_img(number):
    image = images[number]
    if image is None:
        messagebox.showwarning("Ошибка", "Сначала выполните преобразование")
        return
    filename = ["", "nearest.png", "bilinear.png", "bicubic.png"][number]
    path = filedialog.asksaveasfilename(initialdir=folder, initialfile=filename,
        defaultextension=".png", filetypes=[("PNG", "*.png"), ("PBM P1", "*.pbm")])
    if path:
        try:
            if Path(path).suffix.lower() == ".pbm":
                write_pbm(image, path)
            else:
                image.save(path, format="PNG")
        except OSError:
            messagebox.showerror("Ошибка", "Не удалось сохранить изображение")


def main():
    global boxes, scale_entry, angle_entry, shear_entry, status
    root = tk.Tk()
    root.title("Лабораторная работа 8. Вариант 33.")
    top = tk.Frame(root)
    top.pack(pady=8)
    tk.Button(top, text="Открыть", command=open_img).pack(side=tk.LEFT, padx=5)
    entries = []
    for label, value, kind in [("Масштаб", "1.6", "scale"),
                                ("Угол", "20", "rotate"), ("Скос", "0.25", "shear")]:
        tk.Label(top, text=label).pack(side=tk.LEFT)
        entry = tk.Entry(top, width=5)
        entry.insert(0, value)
        entry.pack(side=tk.LEFT, padx=3)
        entries.append(entry)
        tk.Button(top, text="Применить", command=lambda k=kind: process(k)).pack(side=tk.LEFT)
    scale_entry, angle_entry, shear_entry = entries
    panels = tk.Frame(root)
    panels.pack(padx=10, pady=10)
    boxes = []
    for i, title in enumerate(names):
        panel = tk.Frame(panels)
        panel.grid(row=i // 2, column=i % 2, padx=5, pady=5)
        tk.Label(panel, text=title).pack()
        box = tk.Label(panel, text="Нет изображения", bg="white")
        box.pack()
        boxes.append(box)
        if i:
            tk.Button(panel, text="Сохранить", command=lambda n=i: save_img(n)).pack()
    status = tk.Label(root, text="Каждое преобразование выполняется над исходником")
    status.pack(pady=5)
    path = folder / "image.jpg"
    if path.exists():
        try:
            with Image.open(path) as image:
                images[0] = image.convert("RGB")
            show_img(0)
        except OSError:
            messagebox.showerror("Ошибка", "Не удалось открыть image.jpg")
    root.mainloop()


if __name__ == "__main__":
    main()
