import flet as ft
import os


def list_dir(path):
    try:
        return os.listdir(path)
    except Exception as e:
        return [f"Error: {e}"]


def main(page: ft.Page):
    page.title = "Mini Total Commander"
    page.window_width = 1000
    page.window_height = 600
    page.bgcolor = "#0b1a3c"
    page.theme_mode = "dark"

    left_path = ft.TextField(
        label="Left path",
        value=os.getcwd(),
        expand=True,
        on_submit=lambda e: refresh_left(),
    )
    right_path = ft.TextField(
        label="Right path",
        value=os.getcwd(),
        expand=True,
        on_submit=lambda e: refresh_right(),
    )

    left_files = ft.ListView(expand=True, spacing=5, padding=10)
    right_files = ft.ListView(expand=True, spacing=5, padding=10)

    output_text = ft.Text(
        "Output will appear here",
        selectable=True,
        color="white",
        size=14,
    )

    def refresh_left():
        left_files.controls.clear()
        for f in list_dir(left_path.value):
            left_files.controls.append(ft.Text(f, color="white"))
        page.update()

    def refresh_right():
        right_files.controls.clear()
        for f in list_dir(right_path.value):
            right_files.controls.append(ft.Text(f, color="white"))
        page.update()

    refresh_left()
    refresh_right()

    def copy_files(e):
        output_text.value = f"[COPY] from {left_path.value} to {right_path.value}"
        page.update()

    def move_files(e):
        output_text.value = f"[MOVE] from {left_path.value} to {right_path.value}"
        page.update()

    def delete_files(e):
        output_text.value = f"[DELETE] in {left_path.value}"
        page.update()

    def count_files(e):
        output_text.value = f"[COUNT] in {left_path.value}"
        page.update()

    def find_files(e):
        output_text.value = f"[FIND] in {left_path.value}"
        page.update()

    def analyse_dir(e):
        output_text.value = f"[ANALYSE] {left_path.value}"
        page.update()

    def add_date(e):
        output_text.value = f"[ADD_DATE] in {left_path.value}"
        page.update()

    def hashsum_files(e):
        output_text.value = f"[HASHSUM] in {left_path.value}"
        page.update()

    def find_duplicates(e):
        output_text.value = f"[DUPLICATES] in {left_path.value}"
        page.update()

    layout = ft.Row(
        expand=True,
        controls=[
            ft.Column([left_path, left_files], expand=True),
            ft.Column([right_path, right_files], expand=True),
        ],
    )

    square_style = ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=0),
        bgcolor="#1e3a8a",  # синий оттенок кнопки
        color="white",
    )

    buttons = ft.Row(
        alignment="center",
        spacing=10,
        controls=[
            ft.ElevatedButton("Copy", on_click=copy_files, width=100, height=40, style=square_style),
            ft.ElevatedButton("Move", on_click=move_files, width=100, height=40, style=square_style),
            ft.ElevatedButton("Delete", on_click=delete_files, width=100, height=40, style=square_style),
            ft.ElevatedButton("Count", on_click=count_files, width=100, height=40, style=square_style),
            ft.ElevatedButton("Find", on_click=find_files, width=100, height=40, style=square_style),
            ft.ElevatedButton("Analyse", on_click=analyse_dir, width=100, height=40, style=square_style),
            ft.ElevatedButton("Add Date", on_click=add_date, width=100, height=40, style=square_style),
            ft.ElevatedButton("Hashsum", on_click=hashsum_files, width=100, height=40, style=square_style),
            ft.ElevatedButton("Duplicates", on_click=find_duplicates, width=100, height=40, style=square_style),
        ],
    )

    page.add(layout, ft.Divider(), buttons, ft.Divider(), output_text)


if __name__ == "__main__":
    ft.app(target=main)
