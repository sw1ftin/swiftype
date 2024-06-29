import logging
import os.path

import flet as ft
from flet_timer.flet_timer import Timer
from random import choices
from datetime import datetime
import json

global words_count, page_controls_size, history_limit, seconds, errors, result, nickname, data
words_count, page_controls_size, history_limit, seconds, errors, result, nickname = 15, 5, 6, 0, 0, 0, ft.TextField()
data = {}


class ChartState:
    toggle = True


def homepage(page: ft.Page):
    def redirect(page_route: str = "/"):
        page.route = page_route
        e = ft.ControlEvent(target=page_route, name="redirect", data="", control="", page=page)
        if page_route == "/stats/":
            view_stats_page(e)
        elif page_route == "/main/":
            view_main_page(e)
        elif page_route == "/login/":
            view_login_page(e)

    def load_user_stats():
        global data, nickname
        with open("data/data.json", "r") as f:
            try:
                data = json.load(f)
            except Exception as e:
                logging.error(type(e))
                data = {}
        if data.get("nickname"):
            nickname.value = data["nickname"]

    def save_user_stats():
        global data
        with open("data/data.json", "w") as f:
            json.dump(data, f)

    def view_login_page(e=None):
        def submit_nickname(e):
            if input_nickname.value:
                global nickname
                nickname = input_nickname
                data["nickname"] = nickname.value
                save_user_stats()
                redirect("/main/")

        load_user_stats()
        global data
        if data.get("nickname"):
            redirect("/main/")
            return
        page.controls.clear()
        default_avatar = ft.CircleAvatar(
            content=ft.Icon(ft.icons.PERSON, size=50),
            radius=50
        )
        input_nickname = ft.TextField(
            autofocus=True,
            text_align=ft.TextAlign.CENTER,
            label="Nickname",
            hint_text="Enter your nickname",
            hint_style=ft.TextStyle(color=ft.colors.GREY_700),
            on_submit=submit_nickname,
            width=page.width / 2,
            text_size=30,
            border_color=ft.colors.INDIGO,
            border_radius=25
        )
        btn = ft.TextButton(
            text="Submit",
            on_click=submit_nickname,
            width=page.width / 2,
            height=50,
        )
        page.add(
            default_appbar,
            ft.Column(
                [
                    ft.Container(
                        create_row([default_avatar]),
                        margin=ft.margin.only(top=50),
                    ),
                    ft.Container(
                        create_row([ft.Text(
                            "Welcome!",
                            style=ft.TextStyle(
                                size=40
                            )
                        )]),
                        margin=ft.margin.only(top=30),
                    ),
                    ft.Container(
                        create_row([input_nickname]),
                        margin=ft.margin.only(top=50),
                    ),
                    ft.Container(
                        create_row([ft.Container(
                            btn,
                            border=ft.border.all(2, color=ft.colors.INDIGO),
                            border_radius=25
                        )]),
                        margin=ft.margin.only(top=50),
                    ),
                ],
                width=page.width,
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )

    def create_row(controls=None, width=page.width):
        if controls is None:
            controls = []
        return ft.Row(
            controls,
            width=page.width,
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def get_datatable():
        data_text_style = ft.TextStyle(
            size=20,
            color=ft.colors.WHITE,
            font_family="Mono"
        )
        rows = []
        global data
        if data.get("history"):
            for i in range(1, min(len(data["history"]) + 1, history_limit + 1)):
                value = data["history"][-i]
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(value["date"], style=data_text_style)),
                            ft.DataCell(ft.Text(str(value["result"]) + " WPM", style=data_text_style)),
                            ft.DataCell(ft.Text(str(value["errors"]), style=ft.TextStyle(
                                size=20,
                                color=ft.colors.RED if value["errors"] != 0 else ft.colors.GREEN,
                                font_family="Mono"
                            )))
                        ]
                    )
                )
            if len(rows) < history_limit:
                for i in range(history_limit - len(rows)):
                    rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text("-", style=data_text_style)),
                                ft.DataCell(ft.Text("-", style=data_text_style)),
                                ft.DataCell(ft.Text("-", style=data_text_style)),
                            ]
                        )
                    )
        else:
            for i in range(history_limit):
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text("-", style=data_text_style)),
                            ft.DataCell(ft.Text("-", style=data_text_style)),
                            ft.DataCell(ft.Text("-", style=data_text_style)),
                        ]
                    )
                )
        datatable = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Date", style=data_text_style)),
                ft.DataColumn(ft.Text("Result", style=data_text_style)),
                ft.DataColumn(ft.Text("Errors", style=data_text_style)),
            ],
            rows=rows,
            width=page.width * 0.4
        )
        return datatable

    def get_linechart():
        global data
        history = data["history"]
        dates = [entry["date"].replace(' ', '\n') for entry in history]
        results = [entry["result"] for entry in history]
        # anytime you can change date format
        short_dates = [date for date in dates]
        x_labels = [
            ft.ChartAxisLabel(
                value=index,
                label=ft.Container(
                    ft.Text(
                        short_date,
                        size=10,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE),
                    ),
                    margin=ft.margin.only(top=5),
                ),
            )
            for index, short_date in enumerate(short_dates)
        ]
        series = [
            ft.LineChartData(
                data_points=[
                    ft.LineChartDataPoint(index, result) for index, result in enumerate(results)
                ],
                stroke_width=5,
                color=ft.colors.CYAN,
                curved=True,
                stroke_cap_round=True,
            )
        ]

        chart = ft.LineChart(
            data_series=series,
            border=ft.border.all(3, ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=(max(results) - min(results)) / 4,
                color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE),
                width=1,
            ),
            vertical_grid_lines=ft.ChartGridLines(
                interval=1, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1
            ),
            left_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=min(results),
                        label=ft.Text(str(min(results)), size=14, weight=ft.FontWeight.BOLD),
                    ),
                    ft.ChartAxisLabel(
                        value=(min(results) + max(results)) // 2,
                        label=ft.Text(
                            str((min(results) + max(results)) // 2), size=14, weight=ft.FontWeight.BOLD
                        ),
                    ),
                    ft.ChartAxisLabel(
                        value=max(results),
                        label=ft.Text(str(max(results)), size=14, weight=ft.FontWeight.BOLD),
                    ),
                ],
                labels_size=40,
            ),
            bottom_axis=ft.ChartAxis(
                labels=x_labels,
                labels_size=32,
            ),
            tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY),
            min_y=min(results) - 10,
            max_y=max(results) + 10,
            min_x=0,
            max_x=len(dates) - 1,
            expand=False,
            width=page.width * 0.4,
            height=300,
        )

        return chart

    def view_stats_page(e):
        global data
        page.controls.clear()
        stats_text_style = ft.TextStyle(
            size=50,
            color=ft.colors.WHITE,
            font_family="Mono"
        )

        page.add(stats_appbar)

        avatar = ft.CircleAvatar(
            content=
            ft.Image("data/icon.png", height=100, width=100) if os.path.isfile("data/icon.png")
            else ft.Icon(ft.icons.PERSON, size=50),
            radius=50
        )
        match e.name:
            case "redirect":
                global errors
                data_result = {"date": str(datetime.now().strftime("%H:%M %d.%m.%y")), "result": result,
                               "errors": errors}
                if data.get("history"):
                    data["history"].append(data_result)
                else:
                    data["history"] = [data_result]
                errors = 0
                page.add(
                    ft.Column(
                        [
                            ft.Text(
                                value=f"Result: {result} WPM",
                                text_align=ft.TextAlign.CENTER,
                                size=60,
                                width=page.width
                            ),
                            ft.Text(
                                value=f"Errors: {errors}",
                                text_align=ft.TextAlign.CENTER,
                                size=60,
                                width=page.width
                            ),
                            ft.Container(
                                ft.TextButton(
                                    "Go to Stats",
                                    on_click=view_stats_page,
                                    icon=ft.icons.QUERY_STATS,
                                ),
                                alignment=ft.Alignment(0, 0),
                                width=page.width,
                                scale=2,
                                margin=20,
                            ),
                            ft.Container(
                                ft.TextButton(
                                    "Try again",
                                    on_click=view_main_page,
                                    icon=ft.icons.REPLAY,
                                ),
                                alignment=ft.Alignment(0, 0),
                                width=page.width,
                                scale=2,
                                margin=20,
                            )
                        ]
                    )
                )
            case "click":
                stats = [
                    get_datatable(),
                ]
                if data.get("history"):
                    stats.append(get_linechart())
                page.add(
                    ft.Column(
                        [
                            create_row([avatar]),
                            create_row([
                                ft.Text(
                                    nickname.value,
                                    style=stats_text_style
                                )]),
                            create_row(stats)
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        height=page.height / 2,
                    )
                )
        save_user_stats()
        page.update()

    def view_main_page(e):
        page.route = "/main/"
        global start_time
        start_time = ft.Text(value="None")
        global txt_time
        txt_time = ft.Text(
            value="None",
            text_align=ft.TextAlign.CENTER,
            size=50,
            width=page.width
        )
        load_text()
        page.controls.clear()
        page.add(
            main_appbar,
            Timer(name="timer", interval_s=0.2, callback=refresh),
            Timer(name="pointer", interval_s=0.5, callback=pointer_blink),
            txt_time,
            default_text_obj,
        )

    def refresh():
        global seconds
        if start_time.value != "None":
            seconds = (datetime.now() - start_time.value).total_seconds()
            txt_time.value = f"{int(seconds // 60)}:{int(seconds % 60):02}"
        else:
            txt_time.value = "0:00"
        page.update()

    def pointer_blink():
        text = page.controls.pop()
        symbol = text.spans[1].text
        if symbol == "|":
            symbol = ft.TextSpan(" ", style=ft.TextStyle(color="green"))
        else:
            symbol = ft.TextSpan("|", style=ft.TextStyle(color="green"))

        page.add(
            ft.Text(
                text.value,
                size=30,
                style=ft.TextStyle(color="white"),
                spans=[
                    text.spans[0],
                    symbol,
                    text.spans[2],
                ],
            )
        )

    def update_page(correct_part, incorrect_part, left_part):
        page.add(
            ft.Text(
                correct_part,
                size=30,
                style=ft.TextStyle(color="white"),
                spans=[
                    ft.TextSpan(
                        incorrect_part, style=ft.TextStyle(color="red")
                    ),
                    ft.TextSpan("|", style=ft.TextStyle(color="green")),
                    ft.TextSpan(
                        left_part, style=ft.TextStyle(color=ft.colors.GREY)
                    ),
                ],
            )
        )

    def on_keyboard(e: ft.KeyboardEvent):
        match page.route:
            case "/login/":
                pass
            case "/stats/":
                pass
            case _:
                if len(e.key) == 1:
                    if 64 < ord(e.key) < 91:
                        if start_time.value == "None":
                            start_time.value = datetime.now()

                        if len(page.controls) >= page_controls_size:
                            text = page.controls.pop()
                            correct_part = text.value
                            incorrect_part = text.spans[0].text
                            left_part = text.spans[-1].text
                            if left_part:
                                if not incorrect_part:
                                    if e.key.lower() == left_part[0]:
                                        correct_part += left_part[0]
                                        left_part = left_part[1:]
                                        if left_part:
                                            if left_part[0] == ' ':
                                                correct_part += left_part[0]
                                                left_part = left_part[1:]
                                    else:
                                        incorrect_part += left_part[0]
                                        global errors
                                        errors += 1
                                        left_part = left_part[1:]
                            else:
                                pass

                            update_page(correct_part, incorrect_part, left_part)

                            try:
                                if incorrect_part + left_part == "":
                                    global result
                                    result = int(words_count * 60 / seconds)
                                    redirect("/stats/")

                            except IndexError:
                                pass
                    if ord(e.key) == 32:
                        pass

                elif e.key == "Backspace":
                    if len(page.controls) >= page_controls_size:
                        text = page.controls.pop()
                        correct_part = text.value
                        incorrect_part = text.spans[0].text
                        left_part = text.spans[-1].text
                        if incorrect_part:
                            left_part = incorrect_part[-1] + left_part
                            incorrect_part = incorrect_part[:-1]

                        update_page(correct_part, incorrect_part, left_part)

    page.on_keyboard_event = on_keyboard
    page.fonts = {
        "Mono": "https://github.com/google/fonts/raw/main/apache/robotomono/RobotoMono%5Bwght%5D.ttf"
    }
    page.title = "SWIFTYPE"
    page.scroll = "adaptive"
    page.window.min_width = 800
    page.window.min_height = 600

    with open("words.txt", "r", encoding="utf-8") as f:
        global raw_loaded_words
        raw_loaded_words = f.readlines()

    def change_words_count(e):
        global words_count
        words_count = int(dropdown_words.value)
        dropdown_words.disabled = True  # disable dropdown to unfocus
        view_main_page(e)
        page.update()
        dropdown_words.disabled = False

    def load_text():
        loaded_words = " ".join(choices(raw_loaded_words, k=words_count)).replace("\n", "")

        global default_text_obj
        default_text_obj = ft.Text(
            "",
            size=30,
            style=ft.TextStyle(color="white"),
            spans=[
                ft.TextSpan("", style=ft.TextStyle(color="red")),
                ft.TextSpan("|", style=ft.TextStyle(color="green")),
                ft.TextSpan(loaded_words, style=ft.TextStyle(color=ft.colors.GREY)),
            ],
        )

    dropdown_words = ft.Dropdown(
        label="Words",
        on_change=change_words_count,
        options=[
            ft.dropdown.Option('5'),
            ft.dropdown.Option('10'),
            ft.dropdown.Option('15'),
            ft.dropdown.Option('20'),
            ft.dropdown.Option('30'),
            ft.dropdown.Option('50'),
            ft.dropdown.Option('100'),
        ],
        autofocus=False,
        width=100
    )

    default_appbar = ft.AppBar(
        title=ft.TextButton("SWIFTYPE", on_click=view_main_page, icon="keyboard"),
        center_title=False,
        actions=[],
        adaptive=True,
    )

    stats_appbar = ft.AppBar(
        title=ft.TextButton("SWIFTYPE", on_click=view_main_page, icon="keyboard"),
        center_title=False,
        actions=[
            ft.IconButton(
                "home",
                on_click=view_main_page
            )
        ],
        adaptive=True,
    )

    main_appbar = ft.AppBar(
        title=ft.TextButton("SWIFTYPE", on_click=view_main_page, icon="keyboard"),
        center_title=False,
        actions=[
            dropdown_words,
            ft.IconButton(
                "replay",
                on_click=view_main_page,
            ),
            ft.IconButton(
                "person",
                on_click=view_stats_page,
            )
        ],
        adaptive=True,
    )

    global start_time
    start_time = ft.Text(value="None")
    global txt_time
    txt_time = ft.Text(
        value="None",
        text_align=ft.TextAlign.CENTER,
        size=50,
        width=page.width

    )

    load_text()
    global default_text_obj
    page.add(
        default_appbar,
        Timer(name="timer", interval_s=0.2, callback=refresh),
        Timer(name="pointer", interval_s=0.5, callback=pointer_blink),
        txt_time,
        default_text_obj,
    )

    global nickname
    if not nickname.value:
        redirect("/login/")


ft.app(target=homepage)
