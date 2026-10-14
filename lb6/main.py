"""Лабораторная работа 6. Вариант 33."""
import math
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

folder = Path(__file__).resolve().parent
images = [None, None, None, None]
parameters = None


def affine(image, k, scale):
    w, h = image.size
    # Скос: x1=x+k*y. Масштабирование: i=s*x1, j=s*y.
    # Сдвигаем холст для отрицательного скоса, чтобы не обрезать изображение.
    offset = min(0, k * (h - 1))
    width = math.ceil(scale * (w - 1 + abs(k) * (h - 1))) + 1
    height = math.ceil(scale * (h - 1)) + 1
    result = Image.new("RGB", (width, height), "white")
    for j in range(height):
        for i in range(width):
            y = j / scale
            x = i / scale + offset - k * y
            if 0 <= x <= w - 1 and 0 <= y <= h - 1:
                result.putpixel((i, j), image.getpixel((round(x), round(y))))
    return result, offset


def restore(image, original_size, k, scale, offset):
    result = Image.new("RGB", original_size, "white")
    for y in range(result.height):
        for x in range(result.width):
            i = round(scale * (x + k * y - offset))
            j = round(scale * y)
            if 0 <= i < image.width and 0 <= j < image.height:
                result.putpixel((x, y), image.getpixel((i, j)))
    return result


def functional(image):
    w, h = image.size
    if w < 2:
        raise ValueError("Ширина изображения должна быть не меньше 2")
    result = Image.new("RGB", (w, h))
    # x' от 0 до 3; i от 0 до cosh(3)-1. Оба диапазона вписаны в ширину.
    # Обратная функция: x'=acosh(i+1), j=y'.
    for i in range(w):
        coordinate = i * (math.cosh(3) - 1) / (w - 1)
        x = round(math.acosh(coordinate + 1) * (w - 1) / 3)
        for j in range(h):
            result.putpixel((i, j), image.getpixel((x, j)))
    return result


def show_img(number):
    if images[number] is None:
        boxes[number].config(image="", text="Нет изображения")
        return
    temp = images[number].copy()
    temp.thumbnail((400, 260))
    boxes[number].photo = ImageTk.PhotoImage(temp)
    boxes[number].config(image=boxes[number].photo, text="")


def open_img():
    global parameters
    path = filedialog.askopenfilename(initialdir=folder,
        filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp *.ppm"), ("Все файлы", "*.*")])
    if path:
        try:
            with Image.open(path) as image:
                images[0] = image.convert("RGB")
            images[1:] = [None, None, None]
            parameters = None
            for i in range(4):
                show_img(i)
        except OSError:
            messagebox.showerror("Ошибка", "Не удалось открыть изображение")


def process(number):
    global parameters
    if images[0] is None:
        messagebox.showwarning("Ошибка", "Сначала откройте изображение")
        return
    try:
        if number == 1:
            k = float(k_entry.get())
            scale = float(scale_entry.get())
            if not -1 <= k <= 1 or not 0.25 <= scale <= 2:
                raise ValueError("Скос от -1 до 1, масштаб от 0.25 до 2")
            images[1], offset = affine(images[0], k, scale)
            parameters = (k, scale, offset)
            images[2] = None
            show_img(2)
        elif number == 2:
            if images[1] is None:
                raise ValueError("Сначала выполните аффинное преобразование")
            # Используем параметры выполненного преобразования, а не новые поля.
            images[2] = restore(images[1], images[0].size, *parameters)
        else:
            images[3] = functional(images[0])
        show_img(number)
    except ValueError as error:
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
    names = ["", "affine.png", "restored.png", "functional.png"]
    path = filedialog.asksaveasfilename(initialdir=folder, initialfile=names[number],
        defaultextension=".png", filetypes=[("PNG", "*.png"), ("PPM", "*.ppm"), ("PBM", "*.pbm")])
    if path:
        try:
            if Path(path).suffix.lower() == ".pbm":
                write_pbm(image, path)
            else:
                image.save(path)
        except (OSError, ValueError) as error:
            messagebox.showerror("Ошибка", str(error))


def main():
    global boxes, k_entry, scale_entry
    root = tk.Tk()
    root.title("Лабораторная работа 6. Вариант 33.")
    top = tk.Frame(root)
    top.pack(pady=8)
    tk.Button(top, text="Открыть", command=open_img).pack(side=tk.LEFT, padx=4)
    tk.Label(top, text="Скос:").pack(side=tk.LEFT)
    k_entry = tk.Entry(top, width=5)
    k_entry.insert(0, "0.3")
    k_entry.pack(side=tk.LEFT)
    tk.Label(top, text="Масштаб:").pack(side=tk.LEFT)
    scale_entry = tk.Entry(top, width=5)
    scale_entry.insert(0, "0.8")
    scale_entry.pack(side=tk.LEFT)
    for i, text in enumerate(["Аффинное", "Обратное", "Функция"], 1):
        tk.Button(top, text=text, command=lambda n=i: process(n)).pack(side=tk.LEFT, padx=4)
    panels = tk.Frame(root)
    panels.pack(padx=10, pady=10)
    boxes = []
    for i, title in enumerate(["Исходное изображение", "Скос и масштабирование",
                               "Обратное преобразование", "i = cosh(x') - 1"]):
        panel = tk.Frame(panels)
        panel.grid(row=i // 2, column=i % 2, padx=5, pady=5)
        tk.Label(panel, text=title).pack()
        box = tk.Label(panel, text="Нет изображения", bg="white")
        box.pack()
        boxes.append(box)
        if i:
            tk.Button(panel, text="Сохранить", command=lambda n=i: save_img(n)).pack()
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
