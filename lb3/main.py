# Лабораторная работа 3. Вариант 33.
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import xml.etree.ElementTree as ET

img = None
img_tk = None
lines = []


W = 760
H = 580


try:
    FONT = ImageFont.truetype("arial.ttf", 14)
except OSError:
    FONT = ImageFont.load_default()


def put(x, y, color):
    if img is None:
        return

    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), color)


def dda(x1, y1, x2, y2, color):
    dx = x2 - x1
    dy = y2 - y1

    steps = max(abs(dx), abs(dy))

    if steps == 0:
        put(x1, y1, color)
        return

    sx = dx / steps
    sy = dy / steps

    x = x1
    y = y1

    for _ in range(steps + 1):
        put(round(x), round(y), color)
        x += sx
        y += sy


def brez(x1, y1, x2, y2, color):
    dx = x2 - x1
    dy = y2 - y1

    sx = 1 if dx >= 0 else -1
    sy = 1 if dy >= 0 else -1

    dx = abs(dx)
    dy = abs(dy)

    x = x1
    y = y1

    if dx >= dy:
        f = dy / dx - 0.5 if dx != 0 else 0

        for _ in range(dx + 1):
            put(x, y, color)

            if f >= 0:
                y += sy
                f -= 1

            x += sx

            if dx != 0:
                f += dy / dx
    else:
        f = dx / dy - 0.5 if dy != 0 else 0

        for _ in range(dy + 1):
            put(x, y, color)

            if f >= 0:
                x += sx
                f -= 1

            y += sy

            if dy != 0:
                f += dx / dy


def brez_int(x1, y1, x2, y2, color):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    err = dx - dy
    x = x1
    y = y1

    while True:
        put(x, y, color)

        if x == x2 and y == y2:
            break

        e2 = 2 * err

        if e2 > -dy:
            err -= dy
            x += sx

        if e2 < dx:
            err += dx
            y += sy


def built_in(x1, y1, x2, y2, color):
    d = ImageDraw.Draw(img)
    d.line((x1, y1, x2, y2), fill=color, width=1)


def draw_frame():
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, img.width - 1, img.height - 1), outline="gray")
    d.line((380, 0, 380, 579), fill="gray")
    d.line((0, 290, 759, 290), fill="gray")
    d.text((20, 10), "ЦДА", fill="black", font=FONT)
    d.text((400, 10), "Брезенхем", fill="black", font=FONT)
    d.text((20, 300), "Целочисленный Брезенхем", fill="black", font=FONT)
    d.text((400, 300), "Встроенный метод", fill="black", font=FONT)


def read_svg():
    global lines

    path = filedialog.askopenfilename(
        initialdir=Path(__file__).resolve().parent,
        title="Открыть SVG",
        filetypes=[("SVG", "*.svg"), ("Все файлы", "*.*")]
    )

    if path == "":
        return

    try:
        tree = ET.parse(path)
        root = tree.getroot()

        found = []

        for elem in root.iter():
            tag = elem.tag.lower()

            if tag.split("}")[-1] == "line":
                x1 = round(float(elem.get("x1", "0")))
                y1 = round(float(elem.get("y1", "0")))
                x2 = round(float(elem.get("x2", "0")))
                y2 = round(float(elem.get("y2", "0")))
                found.append((x1, y1, x2, y2))

        if len(found) == 0:
            messagebox.showwarning("Ошибка", "В SVG не найдено ни одного отрезка")
            return

        if any(not (20 <= x1 <= 360 and 40 <= y1 <= 270 and
                        20 <= x2 <= 360 and 40 <= y2 <= 270)
               for x1, y1, x2, y2 in found):
            messagebox.showwarning("Ошибка", "Координаты SVG: x от 20 до 360, y от 40 до 270")
            return
        lines = found
        info.config(text=f"Отрезков: {len(lines)}")
        messagebox.showinfo("Готово", "SVG файл считан")
    except (OSError, ValueError, ET.ParseError):
        messagebox.showerror("Ошибка", "Не удалось прочитать SVG файл")


def build():
    global img

    if len(lines) == 0:
        messagebox.showwarning("Ошибка", "Сначала откройте SVG файл")
        return

    img = Image.new("RGB", (W, H), "white")
    draw_frame()

    methods = [(dda, 0, 0), (brez, 380, 0),
               (brez_int, 0, 290), (built_in, 380, 290)]
    for method, ox, oy in methods:
        for x1, y1, x2, y2 in lines:
            method(x1 + ox, y1 + oy, x2 + ox, y2 + oy, (0, 0, 0))

    # Сравниваем только рисунки, без рамок и заголовков.
    base = img.crop((20, 40, 361, 271))
    counts = []
    for ox, oy in [(380, 0), (0, 290), (380, 290)]:
        other = img.crop((20 + ox, 40 + oy, 361 + ox, 271 + oy))
        counts.append(sum(base.getpixel((x, y)) != other.getpixel((x, y))
                          for y in range(base.height) for x in range(base.width)))
    info.config(text="Различий с ЦДА: " + "/".join(map(str, counts)))
    show_img()


def show_img():
    global img_tk

    if img is None:
        return

    temp = img.copy()
    temp.thumbnail((930, 700))

    img_tk = ImageTk.PhotoImage(temp)
    picture.config(image=img_tk, text="")


def write_pbm(image, path):
    with open(path, "w", encoding="ascii") as file:
        file.write(f"P1\n{image.width} {image.height}\n")
        for y in range(image.height):
            row = []
            for x in range(image.width):
                r, g, b = image.getpixel((x, y))
                bright = 0.299 * r + 0.587 * g + 0.114 * b
                row.append("1" if bright < 128 else "0")
            file.write(" ".join(row) + "\n")


def save_img(pbm=False):
    if img is None:
        messagebox.showwarning("Ошибка", "Сначала постройте рисунок")
        return
    extension = ".pbm" if pbm else ".png"
    path = filedialog.asksaveasfilename(initialdir=Path(__file__).resolve().parent,
        initialfile="result" + extension, defaultextension=extension,
        filetypes=[("PBM" if pbm else "PNG", "*" + extension)])
    if path:
        try:
            if pbm:
                write_pbm(img, path)
            else:
                img.save(path, format="PNG")
        except OSError:
            messagebox.showerror("Ошибка", "Не удалось сохранить файл")


def main():
    global root, info, picture
    root = tk.Tk()
    root.title("Лабораторная работа 3. Вариант 33.")
    root.geometry("980x760")

    top = tk.Frame(root)
    top.pack(pady=8)

    tk.Button(top, text="Открыть SVG", width=15, command=read_svg).pack(side=tk.LEFT, padx=4)
    tk.Button(top, text="Построить", width=15, command=build).pack(side=tk.LEFT, padx=4)
    tk.Button(top, text="Сохранить", width=15, command=save_img).pack(side=tk.LEFT, padx=4)
    tk.Button(top, text="PBM", width=10, command=lambda: save_img(True)).pack(side=tk.LEFT, padx=4)

    info = tk.Label(top, text="Отрезков: 0")
    info.pack(side=tk.LEFT, padx=10)

    picture = tk.Label(
        root,
        text="Откройте SVG файл и нажмите Построить",
        bg="white",
        bd=1,
        relief=tk.SOLID
    )
    picture.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
