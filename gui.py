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

    left_path = ft.TextField(label="Left path", value=os.getcwd(), expand=True)
    right_path = ft.TextField(label="Right path", value=os.getcwd(), expand=True)

    left_files = ft.ListView(expand=True, spacing=5, padding=10)
    right_files = ft.ListView(expand=True, spacing=5, padding=10)

    output_text = ft.Text("Output will appear here", selectable=True)

    def refresh_left(e=None):
        left_files.controls.clear()
        for f in list_dir(left_path.value):
            left_files.controls.append(ft.Text(f))
        page.update()

    def refresh_right(e=None):
        right_files.controls.clear()
        for f in list_dir(right_path.value):
            right_files.controls.append(ft.Text(f))
        page.update()

    refresh_left()
    refresh_right()

    def copy_files(e):
        output_text.value = f"Copy from {left_path.value} to {right_path.value}"
        page.update()

    def move_files(e):
        output_text.value = f"Move from {left_path.value} to {right_path.value}"
        page.update()

    def hashsum_files(e):
        output_text.value = f"Hashsum check in {left_path.value}"
        page.update()

    def find_duplicates(e):
        output_text.value = f"Find duplicates in {left_path.value}"
        page.update()


    layout = ft.Row(
        expand=True,
        controls=[
            ft.Column([left_path, left_files], expand=True),
            ft.Column([right_path, right_files], expand=True),
        ]
    )

    buttons = ft.Row(
        controls=[
            ft.ElevatedButton("Copy", on_click=copy_files),
            ft.ElevatedButton("Move", on_click=move_files),
            ft.ElevatedButton("Hashsum", on_click=hashsum_files),
            ft.ElevatedButton("Duplicates", on_click=find_duplicates),
        ]
    )

    page.add(layout, buttons, ft.Divider(), output_text)


if __name__ == "__main__":
    ft.app(target=main)
