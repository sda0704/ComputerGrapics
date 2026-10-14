"""Лабораторная работа 7. Вариант 33."""
import colorsys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

folder = Path(__file__).resolve().parent
images = [None, None, None]

gauss = [[0, 1, 2, 1, 0],
         [1, 6, 10, 6, 1],
         [2, 10, 16, 10, 2],
         [1, 6, 10, 6, 1],
         [0, 1, 2, 1, 0]]

log_mask = [[-1, -2, -3, -2, -1],
            [-2, 0, 4, 0, -2],
            [-3, 4, 16, 4, -3],
            [-2, 0, 4, 0, -2],
            [-1, -2, -3, -2, -1]]


def low_filter(source, threshold):
    result = source.copy()
    norm = sum(sum(row) for row in gauss)
    for y in range(2, source.height - 2):
        for x in range(2, source.width - 2):
            # Яркость V в HSV равна максимальному каналу RGB.
            if max(source.getpixel((x, y))) <= threshold:
                continue
            color = [0, 0, 0]
            for ky in range(5):
                for kx in range(5):
                    pixel = source.getpixel((x + kx - 2, y + ky - 2))
                    for channel in range(3):
                        color[channel] += pixel[channel] * gauss[ky][kx]
            result.putpixel((x, y), tuple(round(c / norm) for c in color))
    return result


def convolution(data, x, y):
    total = 0
    for ky in range(5):
        for kx in range(5):
            total += data[y + ky - 2][x + kx - 2] * log_mask[ky][kx]
    return total


def normalize(data):
    minimum = min(min(row) for row in data)
    maximum = max(max(row) for row in data)
    if maximum - minimum < 1e-12:
        return [[0 for value in row] for row in data]
    return [[(value - minimum) / (maximum - minimum) for value in row]
            for row in data]


def high_filter(source):
    w, h = source.size
    planes = [[[0.0] * w for y in range(h)] for channel in range(3)]
    for y in range(h):
        for x in range(w):
            pixel = source.getpixel((x, y))
            hsv = colorsys.rgb_to_hsv(*(c / 255 for c in pixel))
            for channel in range(3):
                planes[channel][y][x] = hsv[channel]
    result = source.copy()
    # HSV: 0 - тон, 1 - насыщенность, 2 - яркость.
    for left, right, channels in [(2, w // 2, (1, 2)),
                                  (w // 2, w - 2, (0, 1))]:
        filtered = {}
        for channel in channels:
            values = [[convolution(planes[channel], x, y)
                       for x in range(left, right)] for y in range(2, h - 2)]
            filtered[channel] = normalize(values)
        for y in range(2, h - 2):
            for x in range(left, right):
                hsv = [planes[channel][y][x] for channel in range(3)]
                for channel in channels:
                    hsv[channel] = filtered[channel][y - 2][x - left]
                color = colorsys.hsv_to_rgb(*hsv)
                result.putpixel((x, y), tuple(round(c * 255) for c in color))
    return result


def show_img(number):
    if images[number] is None:
        boxes[number].config(image="", text="Нет изображения")
        return
    temp = images[number].copy()
    temp.thumbnail((340, 340))
    boxes[number].photo = ImageTk.PhotoImage(temp)
    boxes[number].config(image=boxes[number].photo, text="")


def open_img():
    path = filedialog.askopenfilename(initialdir=folder,
        filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp *.ppm"), ("Все файлы", "*.*")])
    if path:
        try:
            with Image.open(path) as image:
                source = image.convert("RGB")
            if source.width < 6 or source.height < 5:
                raise ValueError("Размер изображения должен быть не меньше 6 x 5")
            images[:] = [source, None, None]
            for i in range(3):
                show_img(i)
        except (OSError, ValueError) as error:
            messagebox.showerror("Ошибка", str(error))


def process(number):
    if images[0] is None:
        messagebox.showwarning("Ошибка", "Сначала откройте изображение")
        return
    try:
        if number == 1:
            threshold = int(threshold_entry.get())
            if not 0 <= threshold <= 255:
                raise ValueError("Порог T должен быть от 0 до 255")
        status.config(text="Обработка...")
        status.update_idletasks()
        if number == 1:
            images[1] = low_filter(images[0], threshold)
        else:
            images[2] = high_filter(images[0])
        show_img(number)
        status.config(text="Готово")
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
        messagebox.showwarning("Ошибка", "Сначала выполните фильтрацию")
        return
    path = filedialog.asksaveasfilename(initialdir=folder,
        initialfile="low.png" if number == 1 else "high.png", defaultextension=".png",
        filetypes=[("PNG", "*.png"), ("PPM", "*.ppm"), ("PBM", "*.pbm")])
    if path:
        try:
            if Path(path).suffix.lower() == ".pbm":
                write_pbm(image, path)
            else:
                image.save(path)
        except (OSError, ValueError) as error:
            messagebox.showerror("Ошибка", str(error))


def main():
    global boxes, threshold_entry, status
    root = tk.Tk()
    root.title("Лабораторная работа 7. Вариант 33.")
    top = tk.Frame(root)
    top.pack(pady=10)
    tk.Button(top, text="Открыть", command=open_img).pack(side=tk.LEFT, padx=5)
    tk.Label(top, text="Порог T:").pack(side=tk.LEFT)
    threshold_entry = tk.Entry(top, width=5)
    threshold_entry.insert(0, "128")
    threshold_entry.pack(side=tk.LEFT)
    for i, text in [(1, "ФНЧ"), (2, "ФВЧ")]:
        tk.Button(top, text=text, command=lambda n=i: process(n)).pack(side=tk.LEFT, padx=5)
    panels = tk.Frame(root)
    panels.pack(padx=10, pady=10)
    boxes = []
    for i, title in enumerate(["Исходное изображение", "ФНЧ: размытие ярких пикселей",
                               "ФВЧ: лапласиан гауссиана"]):
        panel = tk.Frame(panels)
        panel.pack(side=tk.LEFT, padx=5)
        tk.Label(panel, text=title).pack()
        box = tk.Label(panel, text="Нет изображения", bg="white")
        box.pack()
        boxes.append(box)
        if i:
            tk.Button(panel, text="Сохранить", command=lambda n=i: save_img(n)).pack()
    status = tk.Label(root, text="Порог яркости от 0 до 255")
    status.pack(pady=5)
    path = folder / "image.jpg"
    if path.exists():
        try:
            with Image.open(path) as image:
                source = image.convert("RGB")
            if source.width < 6 or source.height < 5:
                raise ValueError("Размер изображения должен быть не меньше 6 x 5")
            images[0] = source
            show_img(0)
        except (OSError, ValueError) as error:
            messagebox.showerror("Ошибка", str(error))
    root.mainloop()


if __name__ == "__main__":
    main()
