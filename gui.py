import os
import re
import sys
from types import SimpleNamespace

import flet as ft

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from features import copy as feat_copy
from features import move as feat_move
from features import delete as feat_delete
from features import count as feat_count
from features import find as feat_find
from features import analyse as feat_analyse
from features import add_date as feat_add_date
from features import hashsum as feat_hashsum
from features import duplicates as feat_duplicates
from features import rename as feat_rename
from features import mkfile as feat_mkfile
from features import mkdir as feat_mkdir


class ModalManager:
    def __init__(self, page: ft.Page):
        self.page = page

        self.title = ft.Text("", weight=ft.FontWeight.BOLD, size=18, color="white")
        close_btn = ft.IconButton(
            icon=ft.Icons.CLOSE, icon_color="white",
            tooltip="Close",
            on_click=lambda e: self.hide()
        )
        header = ft.Row(
            [self.title, ft.Container(expand=True), close_btn],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        self.body = ft.Column([], tight=True, spacing=8, scroll=ft.ScrollMode.AUTO)
        body_box = ft.Container(
            self.body,
            height=420,
            padding=ft.padding.only(top=5, bottom=5),
        )

        self.actions = ft.Row([], alignment=ft.MainAxisAlignment.END, spacing=10)

        self.card = ft.Container(
            content=ft.Column([header, ft.Divider(opacity=0.15), body_box, self.actions],
                              tight=True, spacing=10),
            bgcolor="#1e3d8f",
            border_radius=12,
            padding=20,
            width=720,
            shadow=ft.BoxShadow(blur_radius=20, color="black"),
        )
        self.card_gd = ft.GestureDetector(
            content=self.card,
            on_tap=lambda e: None,  # глушим всплытие клика внутри карточки
        )

        self.overlay = ft.GestureDetector(
            content=ft.Container(
                expand=True,
                bgcolor="rgba(0,0,0,0.55)",
                alignment=ft.alignment.center,
                content=self.card_gd,
            ),
            on_tap=lambda e: self.hide(),
        )
        self.overlay.visible = False

    def mount_into(self, stack: ft.Stack):
        stack.controls.append(self.overlay)

    def show(self, title: str, body_controls: list[ft.Control], actions: list[ft.Control]):
        self.title.value = title
        self.body.controls = body_controls
        self.actions.controls = actions
        self.overlay.visible = True
        self.page.update()

    def hide(self, _e=None):
        self.overlay.visible = False
        self.page.update()

    def show_text(self, title: str, text: str):
        # текст кладём в прокручиваемое тело
        txt = ft.Text(text, color="white", selectable=True)
        self.show(
            title,
            [txt],
            [
                ft.TextButton("Copy", on_click=lambda _e: self.page.set_clipboard(text)),
                ft.FilledButton("Close", on_click=self.hide),
            ],
        )

    def prompt(self, title: str, fields: list[ft.Control], on_ok, ok_label="OK", ok_primary=True):
        ok_btn = ft.FilledButton(ok_label, on_click=lambda e: (self.hide(), on_ok(e))) if ok_primary \
            else ft.TextButton(ok_label, on_click=lambda e: (self.hide(), on_ok(e)))
        self.show(title, fields, [ft.TextButton("Cancel", on_click=self.hide), ok_btn])

    def confirm(self, title: str, text: str, on_yes, yes_label="Delete"):
        self.show(
            title,
            [ft.Text(text, color="white")],
            [ft.TextButton("Cancel", on_click=self.hide),
             ft.FilledButton(yes_label, on_click=lambda e: (self.hide(), on_yes(e)))],
        )


def main(page: ft.Page):
    page.title = "TotalCommander with some illness"
    page.bgcolor = "#0b1a4a"
    page.window_width = 1140
    page.window_height = 800

    root_stack = ft.Stack(expand=True)
    page.add(root_stack)

    modal = ModalManager(page)
    modal.mount_into(root_stack)

    def snack(msg: str, error: bool = False):
        page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(msg, color="white"),
                bgcolor="#b00020" if error else None,
                show_close_icon=True,
                duration=3000,
            )
        )

    def human_size(n: int) -> str:
        try:
            n = int(n)
        except Exception:
            return str(n)
        for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
            if abs(n) < 1024 or unit == "PB":
                return f"{n:.0f} {unit}" if unit == "B" else f"{n:.2f} {unit}"
            n /= 1024

    def is_dir(p: str) -> bool:
        try:
            return os.path.isdir(p)
        except Exception:
            return False

    def sorted_entries(path: str):
        try:
            names = os.listdir(path)
        except Exception as e:
            return None, str(e)
        names.sort(key=lambda n: (not is_dir(os.path.join(path, n)), n.lower()))
        return names, None

    DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}_")
    DATE_SUFFIX = re.compile(r"_\d{4}-\d{2}-\d{2}(\.[^.]+)?$", re.IGNORECASE)  # intentionally not used; see below

    DATE_SUFFIX = re.compile(r"_\d{4}-\d{2}-\d{2}(\.[^.]+)?$", re.IGNORECASE)

    def looks_dated(original_name: str, candidate: str) -> bool:
        name, ext = os.path.splitext(original_name)
        return (
                (candidate.endswith(original_name) and DATE_PREFIX.match(candidate))
                or (candidate.startswith(name + "_") and candidate.endswith(ext) and DATE_SUFFIX.search(candidate))
        )

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

    left_list = ft.ListView(expand=True, spacing=0, padding=0, auto_scroll=False)
    right_list = ft.ListView(expand=True, spacing=0, padding=0, auto_scroll=False)

    state = {"active": "left", "left_selected": None, "right_selected": None}

    def run_feature_safe(func, ns: SimpleNamespace):
        try:
            result = func.run(ns)
        except Exception as ex:
            return False, None, str(ex)
        if result:
            return True, result, ""
        return False, result, ""

    def make_row(name: str, folder: bool, selected: bool, on_tap, on_double_tap):
        return ft.GestureDetector(
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.FOLDER if folder else ft.Icons.DESCRIPTION, color="white"),
                        ft.Text(name, color="white"),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor="#123078" if selected else None,
                padding=8,
            ),
            data=name,
            on_tap=on_tap,
            on_double_tap=on_double_tap,
        )

    def load_panel(path_field: ft.TextField, listview: ft.ListView, key: str):
        listview.controls.clear()
        current_path = path_field.value
        selected_name = state["left_selected"] if key == "left" else state["right_selected"]

        def tap(e: ft.ControlEvent):
            name = e.control.data
            state["active"] = key
            if key == "left":
                state["left_selected"] = name
            else:
                state["right_selected"] = name
            load_panel(path_field, listview, key)

        def dbl(e: ft.ControlEvent):
            open_item(path_field, listview, e.control.data, key)

        # '..'
        if os.path.isdir(current_path) and os.path.dirname(current_path) and os.path.dirname(
                current_path) != current_path:
            listview.controls.append(make_row("..", True, False, tap, dbl))

        names, err = sorted_entries(current_path)
        if err:
            listview.controls.append(ft.Text(f"Error: {err}", color="red"))
            listview.update()
            return

        for nm in names:
            full = os.path.join(current_path, nm)
            listview.controls.append(make_row(nm, is_dir(full), nm == selected_name, tap, dbl))
        listview.update()

    def open_item(path_field: ft.TextField, listview: ft.ListView, name: str, key: str):
        base = path_field.value
        if name == "..":
            parent = os.path.dirname(base)
            if parent and os.path.exists(parent):
                path_field.value = parent
                if key == "left":
                    state["left_selected"] = None
                else:
                    state["right_selected"] = None
                path_field.update()
                load_panel(path_field, listview, key)
            return
        full = os.path.join(base, name)
        if is_dir(full):
            path_field.value = full
            if key == "left":
                state["left_selected"] = None
            else:
                state["right_selected"] = None
            path_field.update()
            load_panel(path_field, listview, key)
        else:
            if key == "left":
                state["left_selected"] = name
            else:
                state["right_selected"] = name
            load_panel(path_field, listview, key)

    def refresh_both():
        load_panel(left_path, left_list, "left")
        load_panel(right_path, right_list, "right")

    left_path.on_submit = lambda _e: load_panel(left_path, left_list, "left")
    right_path.on_submit = lambda _e: load_panel(right_path, right_list, "right")

    def current_panel():
        return ("left", left_path, left_list, "left_selected") if state["active"] == "left" \
            else ("right", right_path, right_list, "right_selected")

    def other_panel():
        return ("right", right_path, right_list, "right_selected") if state["active"] == "left" \
            else ("left", left_path, left_list, "left_selected")

    def handle_copy():
        _, src_field, _, sel_key = current_panel()
        _, dst_field, dst_list, _ = other_panel()
        sel = state[sel_key]
        if not sel:
            snack("Select an item on the active panel", True);
            return
        ok, payload, msg = run_feature_safe(feat_copy, SimpleNamespace(src=os.path.join(src_field.value, sel),
                                                                       dst=dst_field.value))
        if ok:
            load_panel(dst_field, dst_list, "right" if dst_field is right_path else "left")
            snack("Copied")
        else:
            snack(f"Copy failed{': ' + msg if msg else ''}", True)

    def handle_move():
        _, src_field, src_list, sel_key = current_panel()
        _, dst_field, dst_list, _ = other_panel()
        sel = state[sel_key]
        if not sel:
            snack("Select an item on the active panel", True);
            return
        ok, payload, msg = run_feature_safe(feat_move, SimpleNamespace(src=os.path.join(src_field.value, sel),
                                                                       dst=dst_field.value))
        if ok:
            load_panel(src_field, src_list, "left" if src_field is left_path else "right")
            load_panel(dst_field, dst_list, "right" if dst_field is right_path else "left")
            snack("Moved")
        else:
            snack(f"Move failed{': ' + msg if msg else ''}", True)

    def handle_delete():
        _, path_field, listview, sel_key = current_panel()
        sel = state[sel_key]
        if not sel:
            snack("Select an item on the active panel", True);
            return
        target = os.path.join(path_field.value, sel)

        def confirmed(_e):
            ok, payload, msg = run_feature_safe(feat_delete, SimpleNamespace(src=target))
            if ok and not os.path.exists(target):
                state[sel_key] = None
                load_panel(path_field, listview, "left" if path_field is left_path else "right")
                snack("Deleted")
            else:
                snack(f"Delete failed{': ' + msg if msg else ''}", True)

        modal.confirm("Confirm deletion", target, confirmed)

    def handle_count():
        _, path_field, _, _ = current_panel()
        ok, payload, msg = run_feature_safe(feat_count, SimpleNamespace(path=path_field.value))
        if ok and isinstance(payload, int):
            modal.show_text("Count", f"Total files in {path_field.value}:\n{payload}")
        else:
            modal.show_text("Count", f"Count failed{': ' + msg if msg else ''}")

    def handle_find():
        _, path_field, _, _ = current_panel()
        rx = ft.TextField(label="Regex", autofocus=True, width=420)
        out = ft.Text(color="white", selectable=True)

        def run_find(_e=None):
            pat = rx.value or ""
            if not pat:
                out.value = "Enter a regex";
                modal.page.update();
                return
            ok, payload, msg = run_feature_safe(feat_find, SimpleNamespace(path=path_field.value, regex=pat))
            if ok and isinstance(payload, list):
                out.value = "\n".join(payload) if payload else "No matches found"
            else:
                out.value = f"Find failed{': ' + msg if msg else ''}"
            modal.page.update()

        rx.on_submit = run_find
        modal.show(
            "Find (regex on filenames)",
            [rx, out],
            [
                ft.TextButton("Run", on_click=run_find),
                ft.FilledButton("Close", on_click=modal.hide),
            ],
        )

    def handle_analyse():
        _, path_field, _, _ = current_panel()
        ok, payload, msg = run_feature_safe(feat_analyse, SimpleNamespace(path=path_field.value))
        if ok and isinstance(payload, dict):
            lines = [f"Total: {human_size(payload.get('total_bytes', 0))}", ""]
            for n, s in sorted(payload.get("entries", []), key=lambda x: x[1], reverse=True):
                lines.append(f"{n:<40}  {human_size(s):>12}")
            modal.show_text("Analyse", "\n".join(lines))
        else:
            modal.show_text("Analyse", f"Analyse failed{': ' + msg if msg else ''}")

    def handle_add_date():
        _, path_field, listview, sel_key = current_panel()
        sel = state[sel_key]
        target = os.path.join(path_field.value, sel) if sel else path_field.value

        recursive = ft.Checkbox(label="Recursive", value=False)
        info = ft.Text(color="white")

        def run_add(_e):
            base_dir = target if os.path.isdir(target) else os.path.dirname(target)
            try:
                before = set(os.listdir(base_dir))
            except Exception:
                before = set()

            ok, payload, msg = run_feature_safe(feat_add_date, SimpleNamespace(path=target, recursive=recursive.value))
            load_panel(path_field, listview, "left" if path_field is left_path else "right")

            try:
                after = set(os.listdir(base_dir))
            except Exception:
                after = set()
            added = list(after - before)
            removed = list(before - after)

            count = 0
            if os.path.isfile(target):
                original = os.path.basename(target)
                if original in removed:
                    for cand in added:
                        if looks_dated(original, cand):
                            count = 1
                            break
            else:
                for cand in added:
                    if (re.match(r"^\d{4}-\d{2}-\d{2}_", cand) or
                            re.search(r"_\d{4}-\d{2}-\d{2}(\.[^.]+)?$", cand)):
                        count += 1
            if isinstance(payload, list):
                count = max(count, len(payload))

            if ok:
                info.value = f"Renamed: {count} file(s)"
                snack("Add Date done" if count > 0 else "Nothing to rename")
            else:
                info.value = f"Add Date failed{': ' + msg if msg else ''}"
            modal.page.update()

        modal.prompt(
            "Add creation date to filenames",
            [ft.Text(target, color="white"), recursive, info],
            on_ok=run_add,
            ok_label="Run",
        )

    def handle_hashsum():
        _, path_field, _, sel_key = current_panel()
        sel = state[sel_key]
        target = os.path.join(path_field.value, sel) if sel else path_field.value
        method = ft.Dropdown(
            label="Method",
            value="sha256",
            width=220,
            options=[ft.dropdown.Option("sha256"), ft.dropdown.Option("md5")],
        )

        def run_hash(_e):
            ok, payload, msg = run_feature_safe(feat_hashsum, SimpleNamespace(path=target, method=method.value))
            if ok and isinstance(payload, dict):
                if payload.get("total"):
                    lines = [f"TOTAL {payload['method']}: {payload['total']}", f"Files: {len(payload['items'])}", ""]
                    for it in payload["items"]:
                        lines.append(f"{payload['method']}  {it['hash']}  {it['path']}")
                    modal.show_text("Hashsum (dir)", "\n".join(lines))
                else:
                    modal.show_text("Hashsum (file)", f"{payload['method']}: {payload['items'][0]['hash']}")
            else:
                modal.show_text("Hashsum", f"Hashsum failed{': ' + msg if msg else ''}")

        modal.prompt(
            "Hashsum",
            [ft.Text(target, color="white"), method],
            on_ok=run_hash,
            ok_label="Run",
        )

    def handle_duplicates():
        _, path_field, _, _ = current_panel()
        ok, payload, msg = run_feature_safe(feat_duplicates, SimpleNamespace(path=path_field.value))
        if ok and isinstance(payload, list):
            if not payload:
                modal.show_text("Duplicates", "No duplicates found.")
            else:
                lines = []
                for i, g in enumerate(payload, 1):
                    size_str = human_size(g.get('size', 0))
                    lines.append(f"Group #{i}  size={size_str}  sha256={g.get('hash', '')}")
                    for p in g.get("files", []):
                        lines.append(f"  {p}")
                    lines.append("")
                modal.show_text("Duplicates", "\n".join(lines))
        else:
            modal.show_text("Duplicates", f"Duplicates failed{': ' + msg if msg else ''}")

    def handle_rename():
        _, path_field, listview, sel_key = current_panel()
        sel = state[sel_key]
        if not sel:
            snack("Select a file or folder to rename", True);
            return
        src = os.path.join(path_field.value, sel)
        name_field = ft.TextField(label="New name", value=sel, autofocus=True, width=420)

        def do_rename(_e=None):
            new_name = (name_field.value or "").strip()
            if not new_name:
                snack("Name cannot be empty", True);
                return
            ok, payload, msg = run_feature_safe(feat_rename, SimpleNamespace(src=src, name=new_name))
            if ok and payload:
                state[sel_key] = os.path.basename(payload)
                load_panel(path_field, listview, "left" if path_field is left_path else "right")
                snack("Renamed")
            else:
                snack(f"Rename failed{': ' + msg if msg else ''}", True)

        name_field.on_submit = do_rename
        modal.prompt("Rename", [ft.Text(src, color="white"), name_field], on_ok=do_rename,
                     ok_label="Rename")

    def _target_dir_for_create():
        _, path_field, _, sel_key = current_panel()
        sel = state[sel_key]
        base = path_field.value
        if sel and is_dir(os.path.join(base, sel)):
            return os.path.join(base, sel), path_field, sel_key
        return base, path_field, sel_key

    def handle_new_file():
        base_dir, path_field, sel_key = _target_dir_for_create()
        name_field = ft.TextField(label="Filename", autofocus=True, width=420)

        def do_create(_e=None):
            fname = (name_field.value or "").strip()
            if not fname:
                snack("Filename cannot be empty", True);
                return
            ok, payload, msg = run_feature_safe(feat_mkfile, SimpleNamespace(path=base_dir, name=fname))
            if ok and payload:
                state[sel_key] = None
                load_panel(path_field, left_list if path_field is left_path else right_list,
                           "left" if path_field is left_path else "right")
                snack("File created")
            else:
                snack(f"Create file failed{': ' + msg if msg else ''}", True)

        name_field.on_submit = do_create
        modal.prompt("New File", [ft.Text(base_dir, color="white"), name_field], on_ok=do_create,
                     ok_label="Create")

    def handle_new_folder():
        base_dir, path_field, sel_key = _target_dir_for_create()
        name_field = ft.TextField(label="Folder name", autofocus=True, width=420)

        def do_create(_e=None):
            dname = (name_field.value or "").strip()
            if not dname:
                snack("Folder name cannot be empty", True);
                return
            ok, payload, msg = run_feature_safe(feat_mkdir, SimpleNamespace(path=base_dir, name=dname))
            if ok and payload:
                state[sel_key] = None
                load_panel(path_field, left_list if path_field is left_path else right_list,
                           "left" if path_field is left_path else "right")
                snack("Folder created")
            else:
                snack(f"Create folder failed{': ' + msg if msg else ''}", True)

        name_field.on_submit = do_create
        modal.prompt("New Folder", [ft.Text(base_dir, color="white"), name_field], on_ok=do_create,
                     ok_label="Create")

    COMMANDS = {
        "copy": handle_copy,
        "move": handle_move,
        "delete": handle_delete,
        "count": handle_count,
        "find": handle_find,
        "analyse": handle_analyse,
        "add_date": handle_add_date,
        "hashsum": handle_hashsum,
        "duplicates": handle_duplicates,
        "rename": handle_rename,
        "new_file": handle_new_file,
        "new_folder": handle_new_folder,
    }

    def dispatch(cmd_id: str):
        handler = COMMANDS.get(cmd_id)
        if not handler:
            snack(f"Unknown command: {cmd_id}", True)
            return
        handler()

    def make_panel(path_field: ft.TextField, listview: ft.ListView):
        return ft.Container(
            content=ft.Column(
                [ft.Container(path_field, margin=ft.margin.only(bottom=1)), listview],
                spacing=0, expand=True,
            ),
            border=ft.border.all(1, "white"),
            expand=True, padding=5,
        )

    BUTTONS = [
        ("Copy", "copy"),
        ("Move", "move"),
        ("Delete", "delete"),
        ("Count", "count"),
        ("Find", "find"),
        ("Analyse", "analyse"),
        ("Add Date", "add_date"),
        ("Hashsum", "hashsum"),
        ("Duplicates", "duplicates"),
        ("Rename", "rename"),
        ("New File", "new_file"),
        ("New Folder", "new_folder"),
    ]

    controls_layout = ft.Column(
        [
            ft.Row([make_panel(left_path, left_list), make_panel(right_path, right_list)],
                   expand=True, spacing=1, tight=True),
            ft.Row(
                [
                    ft.ElevatedButton(
                        label,
                        on_click=(lambda _cmd=cmd: (lambda _e: dispatch(_cmd)))(),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=0),
                            padding=20,
                            bgcolor="#1e3d8f",
                            color="white",
                        ),
                    )
                    for (label, cmd) in BUTTONS
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=12,
                wrap=True,
            ),
        ],
        expand=True,
    )

    root_stack.controls.insert(0, controls_layout)
    page.update()

    load_panel(left_path, left_list, "left")
    load_panel(right_path, right_list, "right")


if __name__ == "__main__":
    # uncomment when want to use browser instead of app
    # ft.app(target=main, view=ft.AppView.WEB_BROWSER)
    ft.app(target=main)
