"""Лабораторная работа 5. Вариант 33."""
import colorsys
import math
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

folder = Path(__file__).resolve().parent
images = [None, None, None, None]


def show_img(number):
    if images[number] is None:
        boxes[number].config(image="", text="Нет изображения")
        return
    temp = images[number].copy()
    temp.thumbnail((390, 280))
    boxes[number].photo = ImageTk.PhotoImage(temp)
    boxes[number].config(image=boxes[number].photo, text="")


def open_img(number):
    path = filedialog.askopenfilename(initialdir=folder,
        filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp *.ppm *.pbm"), ("Все файлы", "*.*")])
    if path:
        try:
            with Image.open(path) as image:
                images[number] = image.convert("RGB")
            images[2] = images[3] = None
            for i in [number, 2, 3]:
                show_img(i)
        except OSError:
            messagebox.showerror("Ошибка", "Не удалось открыть изображение")


def saturation(image):
    result = Image.new("RGB", image.size)
    for y in range(image.height):
        for x in range(image.width):
            r, g, b = image.getpixel((x, y))
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            # Тон переводим в радианы. Отрицательную насыщенность ограничиваем нулем.
            s = max(0, math.sin(2 * math.pi * h))
            color = colorsys.hsv_to_rgb(h, s, v)
            result.putpixel((x, y), tuple(round(c * 255) for c in color))
    return result


def soft_light(bottom, top):
    if bottom.size != top.size:
        raise ValueError("Изображения должны быть одинакового размера")
    result = Image.new("RGB", bottom.size)
    for y in range(bottom.height):
        for x in range(bottom.width):
            lower = bottom.getpixel((x, y))
            upper = top.getpixel((x, y))
            color = []
            for c1, c2 in zip(lower, upper):
                a, b = c1 / 255, c2 / 255
                # Мягкий свет по определению методички.
                if b < 0.5:
                    c = min(a, b)
                else:
                    c = 1 - (1 - a) * (1 - b)
                color.append(round(c * 255))
            result.putpixel((x, y), tuple(color))
    return result


def process():
    if images[0] is None:
        messagebox.showwarning("Ошибка", "Сначала откройте первое изображение")
        return
    images[2] = saturation(images[0])
    show_img(2)


def mix():
    if images[0] is None or images[1] is None:
        messagebox.showwarning("Ошибка", "Сначала откройте два изображения")
        return
    try:
        # Операции независимы: накладываем исходное второе на исходное первое.
        images[3] = soft_light(images[0], images[1])
        show_img(3)
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
        messagebox.showwarning("Ошибка", "Сначала выполните обработку")
        return
    name = "saturation.png" if number == 2 else "soft_light.png"
    path = filedialog.asksaveasfilename(initialdir=folder, initialfile=name,
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
    global boxes
    root = tk.Tk()
    root.title("Лабораторная работа 5. Вариант 33.")
    top = tk.Frame(root)
    top.pack(pady=8)
    buttons = [("Открыть 1", lambda: open_img(0)), ("Открыть 2", lambda: open_img(1)),
               ("Синус тона", process), ("Мягкий свет", mix),
               ("Сохранить 1", lambda: save_img(2)), ("Сохранить 2", lambda: save_img(3))]
    for text, command in buttons:
        tk.Button(top, text=text, command=command).pack(side=tk.LEFT, padx=4)
    panels = tk.Frame(root)
    panels.pack(padx=10, pady=10)
    boxes = []
    for i, title in enumerate(["Первое изображение (нижний слой)", "Второе изображение (верхний слой)",
                               "Насыщенность: синус тона", "Наложение: мягкий свет"]):
        panel = tk.Frame(panels)
        panel.grid(row=i // 2, column=i % 2, padx=5, pady=5)
        tk.Label(panel, text=title).pack()
        box = tk.Label(panel, bg="white", text="Нет изображения")
        box.pack()
        boxes.append(box)
    for i, name in enumerate(["image1.jpg", "image2.jpg"]):
        path = folder / name
        if path.exists():
            try:
                with Image.open(path) as image:
                    images[i] = image.convert("RGB")
                show_img(i)
            except OSError:
                messagebox.showerror("Ошибка", f"Не удалось открыть {name}")
    root.mainloop()


if __name__ == "__main__":
    main()
