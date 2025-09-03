import flet as ft
import os

from flet.core.form_field_control import InputBorder


def main(page: ft.Page):
    page.title = "File Manager (Total Commander style)"
    page.bgcolor = "#0b1a4a"
    page.window_width = 1000
    page.window_height = 800

    page.keyboard_type = "physical"

    left_path = ft.TextField(
        label="Left path",
        value=os.getcwd(),
        expand=True,
        border_color="white",
        border_radius=3,
        text_style=ft.TextStyle(color="white"),
    )

    right_path = ft.TextField(
        label="Right path",
        value=os.getcwd(),
        expand=True,
        border_color="white",
        border_radius=3,
        text_style=ft.TextStyle(color="white"),
    )

    left_files = ft.ListView(expand=True, spacing=0, padding=0)
    right_files = ft.ListView(expand=True, spacing=0, padding=0)

    def open_item(path_field, listview: ft.ListView, item_name: str):
        current_path = path_field.value
        if item_name == "..":
            parent = os.path.dirname(current_path)
            if parent and os.path.exists(parent):
                path_field.value = parent
                path_field.update()
                load_files(parent, listview, path_field)
        else:
            full_path = os.path.join(current_path, item_name)
            if os.path.isdir(full_path):
                path_field.value = full_path
                path_field.update()
                load_files(full_path, listview, path_field)
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"Selected file: {item_name}", color="white"))
                page.snack_bar.open = True
                page.update()

    def load_files(path, listview: ft.ListView, path_field):
        listview.controls.clear()
        if os.path.isdir(path):
            try:
                if os.path.dirname(path) != path:
                    listview.controls.append(
                        ft.GestureDetector(
                            content=ft.Row(
                                [ft.Icon(ft.Icons.ARROW_UPWARD, color="white"), ft.Text("..", color="white")],
                                spacing=10,
                            ),
                            on_tap=lambda e: open_item(path_field, listview, ".."),
                        )
                    )

                for name in os.listdir(path):
                    full_path = os.path.join(path, name)
                    if os.path.isdir(full_path):
                        icon = ft.Icons.FOLDER
                    else:
                        icon = ft.Icons.DESCRIPTION
                    listview.controls.append(
                        ft.GestureDetector(
                            content=ft.Row(
                                [ft.Icon(icon, color="white"), ft.Text(name, color="white")],
                                spacing=10,
                            ),
                            on_tap=lambda e, n=name: open_item(path_field, listview, n),
                        )
                    )
            except Exception as e:
                listview.controls.append(ft.Text(f"Error: {e}", color="red"))
        listview.update()

    def update_left_path(e):
        load_files(left_path.value, left_files, left_path)

    def update_right_path(e):
        load_files(right_path.value, right_files, right_path)

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

    def make_button_action(name):
        def action(e):
            page.snack_bar = ft.SnackBar(ft.Text(f"{name} pressed", color="white"))
            page.snack_bar.open = True
            page.update()

        return action

    buttons = ft.Row(
        [
            ft.ElevatedButton(
                text,
                on_click=make_button_action(text),
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
        "F9": "Duplicates"
    }

    def handle_hotkey(e: ft.KeyboardEvent):
        key = e.key.upper()
        if key in hotkeys:
            cmd = hotkeys[key]
            btn = button_map.get(cmd)
            if btn and btn.on_click:
                btn.on_click(e)

    page.on_keyboard_event = handle_hotkey

    page.add(file_panels, buttons)

    load_files(left_path.value, left_files, left_path)
    load_files(right_path.value, right_files, right_path)


if __name__ == "__main__":
    ft.app(target=main)
