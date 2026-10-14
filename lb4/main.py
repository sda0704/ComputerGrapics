# Лабораторная работа 4. Вариант 33.
import math
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk

img = None
source = None
folder = Path(__file__).resolve().parent
try:
    FONT = ImageFont.truetype("arial.ttf", 14)
except OSError:
    FONT = ImageFont.load_default()


def egg_arcs(R, r):
    # R - радиус нижней дуги, r - верхней. Боковые дуги имеют радиус 2R.
    # Расстояние между центрами касающихся окружностей равно 2R-r.
    h = math.sqrt((2 * R - r) ** 2 - R ** 2)
    angle = math.degrees(math.atan2(h, R))
    return [(0, 0, R, 0, 180),
            (-R, 0, 2 * R, 360 - angle, 360),
            (R, 0, 2 * R, 180, 180 + angle),
            (0, -h, r, 180 + angle, 360 - angle)]


def arc_pixels(cx, cy, radius, start, end, method):
    # Сначала растеризуем окружность, затем оставляем нужную дугу.
    result = set()
    radius = round(radius)

    def put(x, y):
        angle = math.degrees(math.atan2(y, x)) % 360
        if start - 1e-9 <= angle <= end + 1e-9 or (angle == 0 and end == 360):
            result.add((round(cx + x), round(cy + y)))

    if method == 0:
        for x in range(-radius, radius + 1):
            y = round(math.sqrt(radius * radius - x * x))
            put(x, y)
            put(x, -y)
            # Перебор обеих координат устраняет пропуски возле боковых точек.
            put(y, x)
            put(-y, x)
    elif method == 1:
        steps = math.ceil(math.radians(end - start) * radius * 2)
        for i in range(steps + 1):
            angle = math.radians(start + (end - start) * i / steps)
            result.add((round(cx + radius * math.cos(angle)),
                        round(cy + radius * math.sin(angle))))
    else:
        x, y, error = 0, radius, 3 - 2 * radius
        while x <= y:
            for px, py in [(x, y), (-x, y), (x, -y), (-x, -y),
                           (y, x), (-y, x), (y, -x), (-y, -x)]:
                put(px, py)
            if error < 0:
                error += 4 * x + 6
            else:
                error += 4 * (x - y) + 10
                y -= 1
            x += 1
    return result


def render_egg(R, r, method, x0=190, y0=200, background=None):
    image = background.copy() if background is not None else Image.new("RGB", (380, 320), "white")
    arcs = egg_arcs(R, r)
    draw = ImageDraw.Draw(image)
    for cx, cy, radius, start, end in arcs:
        cx, cy = cx + x0, cy + y0
        if method == 3:
            draw.arc((cx - radius, cy - radius, cx + radius, cy + radius),
                     start, end, fill="black", width=1)
        else:
            for x, y in arc_pixels(cx, cy, radius, start, end, method):
                image.putpixel((x, y), (0, 0, 0))
    return image


def open_img():
    global source, img
    path = filedialog.askopenfilename(initialdir=folder,
        filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp *.ppm *.pbm"), ("Все файлы", "*.*")])
    if path:
        try:
            with Image.open(path) as image:
                source = image.convert("RGB")
            img = None
            picture.config(image="", text="Задайте центр и радиусы, затем нажмите Построить")
            info.config(text=f"Исходное изображение: {source.width} x {source.height}")
        except OSError:
            messagebox.showerror("Ошибка", "Не удалось открыть изображение")


def build():
    global img
    if source is None:
        messagebox.showwarning("Ошибка", "Сначала откройте исходное изображение")
        return
    try:
        R, r = int(R_entry.get()), int(r_entry.get())
        x0, y0 = int(x_entry.get()), int(y_entry.get())
        if not 5 <= r < R:
            raise ValueError("Нужно 5 <= r < R")
        arcs = egg_arcs(R, r)
        top = y0 + arcs[-1][1] - r
        if x0 - R < 1 or x0 + R > source.width - 2 or top < 1 or y0 + R > source.height - 2:
            raise ValueError("Яйцо выходит за границы изображения. Измените центр или радиусы")
    except ValueError as error:
        messagebox.showerror("Ошибка", str(error))
        return
    panels = [render_egg(R, r, method, x0, y0, source) for method in range(4)]
    w, h = source.size
    img = Image.new("RGB", (w * 2, (h + 30) * 2), "white")
    draw = ImageDraw.Draw(img)
    titles = ["Уравнение окружности", "Параметрическое уравнение",
              "Брезенхем", "Встроенный метод"]
    for i, panel in enumerate(panels):
        x, y = (i % 2) * w, (i // 2) * (h + 30)
        img.paste(panel, (x, y + 30))
        draw.text((x + 15, y + 8), titles[i], fill="black", font=FONT)
    draw.line((w, 0, w, img.height - 1), fill="gray")
    draw.line((0, h + 30, img.width - 1, h + 30), fill="gray")
    # Сравниваем контуры на белом фоне, чтобы темный исходник не скрывал различия.
    white = Image.new("RGB", source.size, "white")
    masks = [render_egg(R, r, method, x0, y0, white).convert("L").tobytes()
             for method in range(4)]
    counts = [sum(a != b for a, b in zip(masks[0], mask)) for mask in masks[1:]]
    info.config(text="Различий с уравнением: " + "/".join(map(str, counts)))
    preview = img.copy()
    preview.thumbnail((900, 650))
    picture.photo = ImageTk.PhotoImage(preview)
    picture.config(image=picture.photo, text="")


def write_pbm(image, path):
    gray = image.convert("L")
    with open(path, "w", encoding="ascii") as file:
        file.write(f"P1\n{image.width} {image.height}\n")
        for y in range(image.height):
            row = ["1" if gray.getpixel((x, y)) < 128 else "0"
                   for x in range(image.width)]
            file.write(" ".join(row) + "\n")


def save_img(pbm=False):
    if img is None:
        messagebox.showwarning("Ошибка", "Сначала постройте рисунок")
        return
    extension = ".pbm" if pbm else ".png"
    path = filedialog.asksaveasfilename(initialdir=folder, initialfile="result" + extension, defaultextension=extension,
                                      filetypes=[("PBM" if pbm else "PNG", "*" + extension)])
    if path:
        try:
            if pbm:
                write_pbm(img, path)
            else:
                img.save(path, format="PNG")
        except OSError:
            messagebox.showerror("Ошибка", "Не удалось сохранить изображение")


def main():
    global source, R_entry, r_entry, x_entry, y_entry, info, picture
    root = tk.Tk()
    root.title("Лабораторная работа 4. Вариант 33.")
    top = tk.Frame(root)
    top.pack(pady=8)
    tk.Button(top, text="Открыть", command=open_img).pack(side=tk.LEFT, padx=5)
    tk.Label(top, text="Центр X:").pack(side=tk.LEFT)
    x_entry = tk.Entry(top, width=5)
    x_entry.insert(0, "190")
    x_entry.pack(side=tk.LEFT)
    tk.Label(top, text="Y:").pack(side=tk.LEFT)
    y_entry = tk.Entry(top, width=5)
    y_entry.insert(0, "200")
    y_entry.pack(side=tk.LEFT)
    tk.Label(top, text="Нижний радиус R:").pack(side=tk.LEFT)
    R_entry = tk.Entry(top, width=5)
    R_entry.insert(0, "90")
    R_entry.pack(side=tk.LEFT, padx=5)
    tk.Label(top, text="Верхний радиус r:").pack(side=tk.LEFT)
    r_entry = tk.Entry(top, width=5)
    r_entry.insert(0, "53")
    r_entry.pack(side=tk.LEFT, padx=5)
    for text, command in [("Построить", build), ("PNG", save_img),
                          ("PBM", lambda: save_img(True))]:
        tk.Button(top, text=text, command=command).pack(side=tk.LEFT, padx=5)
    info = tk.Label(root, text="Откройте изображение и задайте центр и радиусы")
    info.pack()
    picture = tk.Label(root, bg="white")
    picture.pack(padx=10, pady=10)
    path = folder / "source.png"
    if path.exists():
        try:
            with Image.open(path) as image:
                source = image.convert("RGB")
            build()
        except OSError:
            messagebox.showerror("Ошибка", "Не удалось открыть source.png")
    root.mainloop()


if __name__ == "__main__":
    main()
