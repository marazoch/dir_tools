import flet as ft
from flet import Icons
import os


def main(page: ft.Page):
    page.title = "File Manager (Total Commander style)"
    page.bgcolor = "#0b1a4a"
    page.window_width = 1000
    page.window_height = 800

    left_path = ft.TextField(
        label="Left path",
        value=os.getcwd(),
        expand=True,
        border=ft.border.all(1, "white"),
        border_radius=3,
        text_style=ft.TextStyle(color="white"),
    )

    right_path = ft.TextField(
        label="Right path",
        value=os.getcwd(),
        expand=True,
        border=ft.border.all(1, "white"),
        border_radius=3,
        text_style=ft.TextStyle(color="white"),
    )

    left_files = ft.ListView(expand=True, spacing=0, padding=0)
    right_files = ft.ListView(expand=True, spacing=0, padding=0)

    def load_files(path, listview: ft.ListView):
        listview.controls.clear()
        if os.path.isdir(path):
            try:
                for name in os.listdir(path):
                    full_path = os.path.join(path, name)
                    if os.path.isdir(full_path):
                        icon = Icons.FOLDER
                    else:
                        icon = Icons.DESCRIPTION
                    listview.controls.append(
                        ft.Row(
                            [ft.Icon(icon, color="white"), ft.Text(name, color="white")],
                            spacing=10,
                        )
                    )
            except Exception as e:
                listview.controls.append(ft.Text(f"Error: {e}", color="red"))
        listview.update()

    def update_left_path(e):
        load_files(left_path.value, left_files)

    def update_right_path(e):
        load_files(right_path.value, right_files)

    left_path.on_submit = update_left_path
    right_path.on_submit = update_right_path

    file_panels = ft.Row(
        [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(left_path, margin=ft.margin.only(bottom=1)),
                        left_files,
                    ],
                    spacing=0,
                    expand=True,
                ),
                border=ft.border.all(1, "white"),
                expand=True,
                padding=5,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(right_path, margin=ft.margin.only(bottom=1)),
                        right_files,
                    ],
                    spacing=0,
                    expand=True,
                ),
                border=ft.border.all(1, "white"),
                expand=True,
                padding=5,
            ),
        ],
        expand=True,
        spacing=1,
        tight=True,
    )

    commands = [
        "Copy", "Move", "Delete", "Count",
        "Find", "Analyse", "Add Date", "Hashsum", "Duplicates"
    ]

    buttons = ft.Row(
        [
            ft.ElevatedButton(
                text,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=0),
                    padding=20,
                    bgcolor="#1e3d8f",
                    color="white",
                ),
            )
            for text in commands
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=15,
    )

    button_map = {btn.text: btn for btn in buttons.controls}

    hotkeys = {
        "F1": "Copy",
        "F2": "Move",
        "F3": "Delete",
        "F4": "Count",
        "F5": "Find",
        "F6": "Analyse",
        "F7": "Add Date",
        "F8": "Hashsum",
        "F9": "Duplicates",
    }

    def handle_hotkey(e: ft.KeyboardEvent):
        if e.key in hotkeys:
            cmd = hotkeys[e.key]
            btn = button_map.get(cmd)
            if btn and btn.on_click:
                btn.on_click(None)

    page.on_keyboard_event = handle_hotkey

    page.add(file_panels, buttons)

    load_files(left_path.value, left_files)
    load_files(right_path.value, right_files)


if __name__ == "__main__":
    ft.app(target=main)
