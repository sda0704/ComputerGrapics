"""Лабораторная работа 2. Вариант 33."""
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw

src = None
dst = None


def show_img(image, box):
    temp = image.copy()
    temp.thumbnail((440, 340))
    box.photo = ImageTk.PhotoImage(temp)
    box.config(image=box.photo, text="")


def create_img():
    global dst
    try:
        w, h = int(width_entry.get()), int(height_entry.get())
        if w < 400 or h < 300:
            raise ValueError()
        dst = Image.new("RGB", (w, h), "white")
        show_img(dst, dst_box)
    except ValueError:
        messagebox.showerror("Ошибка", "Введите размеры не меньше 400 x 300")


def open_img():
    global src
    path = filedialog.askopenfilename(filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp"), ("Все файлы", "*.*")])
    if path:
        try:
            with Image.open(path) as image:
                src = image.convert("RGB")
            show_img(src, src_box)
        except OSError:
            messagebox.showerror("Ошибка", "Не удалось открыть изображение")


def copy_part():
    if src is None or dst is None:
        messagebox.showwarning("Ошибка", "Сначала создайте холст и откройте фотографию")
        return
    sw, sh = src.size
    dw, dh = dst.size
    cx, cy = sw // 2, sh // 2
    depth = min(150, sw - cx - 1, dw // 3)
    half = min(75, cy, sh - cy - 1, (dh - 40) // 2)
    if depth < 1 or half < 1:
        messagebox.showwarning("Ошибка", "Фотография слишком маленькая")
        return
    left = dw - depth - 21
    # Вертикальное основание на центральной линии, вершина справа.
    for x in range(depth + 1):
        part = half * (depth - x) // depth
        for y in range(-part, part + 1):
            color = src.getpixel((cx + x, cy + y))
            dst.putpixel((left + x, 20 + half + y), color)
    show_img(dst, dst_box)


def draw_axes():
    if dst is None:
        messagebox.showwarning("Ошибка", "Сначала создайте холст")
        return
    w, h = dst.size
    d = ImageDraw.Draw(dst)
    x0, y0 = w // 3, h - 50
    right, scale = w * 3 // 5, 40
    d.line((20, y0, right, y0), fill="black")
    d.line((x0, h - 20, x0, 20), fill="black")
    d.line((right - 7, y0 - 4, right, y0, right - 7, y0 + 4), fill="black")
    d.line((x0 - 4, 27, x0, 20, x0 + 4, 27), fill="black")
    for x in range(x0 % scale, right, scale):
        if x >= 20:
            d.line((x, y0 - 3, x, y0 + 3), fill="black")
            d.text((x - 4, y0 + 8), str((x - x0) // scale), fill="black")
    for y in range(y0, 20, -scale):
        d.line((x0 - 3, y, x0 + 3, y), fill="black")
        if y != y0:
            d.text((x0 - 18, y - 5), str((y0 - y) // scale), fill="black")
    d.text((right + 5, y0), "x", fill="black")
    d.text((x0 + 5, 15), "y", fill="black")
    show_img(dst, dst_box)


def draw_graph():
    if dst is None:
        messagebox.showwarning("Ошибка", "Сначала создайте холст")
        return
    w, h = dst.size
    d = ImageDraw.Draw(dst)
    x0, y0, scale = w // 3, h - 50, 40
    old = None
    for px in range(20, w * 3 // 5):
        x = (px - x0) / scale
        if abs(x - 1) < 0.000001:
            old = None
            continue
        y = 1 / (x - 1) ** 2
        py = y0 - round(y * scale)
        if 20 <= py <= y0:
            if old is not None:
                d.line((*old, px, py), fill="blue", width=2)
            old = (px, py)
        else:
            old = None
    d.text((20, 5), "y = 1/(x-1)^2", fill="blue")
    show_img(dst, dst_box)


def write_pbm(image, path):
    gray = image.convert("L")
    with open(path, "w", encoding="ascii") as file:
        file.write(f"P1\n{image.width} {image.height}\n")
        for y in range(image.height):
            row = ["1" if gray.getpixel((x, y)) < 128 else "0"
                   for x in range(image.width)]
            for start in range(0, len(row), 35):
                file.write(" ".join(row[start:start + 35]) + "\n")


def save_img(pbm=False):
    if dst is None:
        messagebox.showwarning("Ошибка", "Сначала создайте холст")
        return
    extension = ".pbm" if pbm else ".png"
    path = filedialog.asksaveasfilename(defaultextension=extension, filetypes=[("PBM" if pbm else "PNG", "*" + extension)])
    if path:
        try:
            if pbm:
                # PBM хранит только чёрный и белый: порог яркости 128.
                write_pbm(dst, path)
            else:
                dst.save(path, format="PNG")
        except OSError:
            messagebox.showerror("Ошибка", "Не удалось сохранить файл")


def main():
    global width_entry, height_entry, src_box, dst_box
    root = tk.Tk()
    root.title("Лабораторная работа 2. Вариант 33.")
    root.geometry("1050x520")
    top = tk.Frame(root)
    top.pack(pady=10)
    tk.Label(top, text="Ширина:").pack(side=tk.LEFT)
    width_entry = tk.Entry(top, width=6)
    width_entry.insert(0, "600")
    width_entry.pack(side=tk.LEFT)
    tk.Label(top, text="Высота:").pack(side=tk.LEFT)
    height_entry = tk.Entry(top, width=6)
    height_entry.insert(0, "400")
    height_entry.pack(side=tk.LEFT)
    for text, command in [("Создать", create_img), ("Открыть", open_img), ("Перенести", copy_part), ("Оси", draw_axes), ("График", draw_graph), ("PNG", save_img), ("PBM", lambda: save_img(True))]:
        tk.Button(top, text=text, command=command).pack(side=tk.LEFT, padx=4)
    panels = tk.Frame(root)
    panels.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    src_box = tk.Label(panels, text="Откройте фотографию", bg="white", relief=tk.SOLID)
    src_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    dst_box = tk.Label(panels, text="Создайте новый холст", bg="white", relief=tk.SOLID)
    dst_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    root.mainloop()


if __name__ == "__main__":
    main()
