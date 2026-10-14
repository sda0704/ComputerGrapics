"""Лабораторная работа 1. Вариант 33."""
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

folder = Path(__file__).resolve().parent
src = None
img = None


def process_image(source):
    result = source.convert("RGB").copy()
    w, h = result.size
    result.putpixel((0, 0), (64, 127, 127))
    result.putpixel((0, h // 2), (127, 64, 255))
    result.putpixel((w // 2, h // 2), (127, 255, 64))
    return result


def show_img():
    temp = img.copy()
    temp.thumbnail((900, 550))
    picture.photo = ImageTk.PhotoImage(temp)
    picture.config(image=picture.photo, text="")


def open_img():
    global src, img
    path = filedialog.askopenfilename(initialdir=folder,
        filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp"), ("Все файлы", "*.*")])
    if path:
        try:
            with Image.open(path) as image:
                src = image.convert("RGB")
            img = src.copy()
            show_img()
        except OSError:
            messagebox.showerror("Ошибка", "Не удалось открыть изображение")


def process():
    global img
    if src is None:
        messagebox.showwarning("Ошибка", "Сначала откройте изображение")
        return
    img = process_image(src)
    show_img()


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
    if img is None:
        messagebox.showwarning("Ошибка", "Нет изображения для сохранения")
        return
    extension = ".pbm" if pbm else ".png"
    path = filedialog.asksaveasfilename(initialdir=folder, initialfile="result" + extension,
        defaultextension=extension, filetypes=[("PBM" if pbm else "PNG", "*" + extension)])
    if path:
        try:
            if pbm:
                write_pbm(img, path)
            else:
                img.save(path, format="PNG")
        except OSError:
            messagebox.showerror("Ошибка", "Не удалось сохранить изображение")


def main():
    global picture, src, img
    root = tk.Tk()
    root.title("Лабораторная работа 1. Вариант 33.")
    root.geometry("950x650")
    top = tk.Frame(root)
    top.pack(pady=10)
    for text, command in [("Открыть", open_img), ("Обработать", process),
                          ("PNG", save_img), ("PBM", lambda: save_img(True))]:
        tk.Button(top, text=text, command=command).pack(side=tk.LEFT, padx=5)
    picture = tk.Label(root, text="Откройте изображение", bg="white")
    picture.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    path = folder / "image.jpg"
    if path.exists():
        try:
            with Image.open(path) as image:
                src = image.convert("RGB")
            img = src.copy()
            show_img()
        except OSError:
            messagebox.showerror("Ошибка", "Не удалось открыть image.jpg")
    root.mainloop()


if __name__ == "__main__":
    main()
