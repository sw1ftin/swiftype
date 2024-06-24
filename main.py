import flet as ft
from flet_timer.flet_timer import Timer
from random import choices
from datetime import datetime

global words_count, page_controls_size, seconds, result
words_count, page_controls_size, seconds, result = 15, 5, 0, 0


def homepage(page: ft.Page):
    def redirect(page_route: str = "/"):
        page.route = page_route
        if page_route == "/stats/":
            view_stats_page(page_route)
        if page_route == "/main/":
            view_main_page(page_route)

    def view_stats_page(e):
        page.controls.clear()
        page.add(
            default_appbar,
            ft.Column(
                [
                    ft.Text(
                        value=f"Your result is: {result} WPM",
                        text_align=ft.TextAlign.CENTER,
                        size=60,
                        width=page.width
                    ),
                    ft.Container(
                        ft.TextButton(
                            "Try again",
                            on_click=view_main_page,
                            icon="replay",
                        ),
                        alignment=ft.Alignment(0, 0),
                        width=page.width,
                        scale=2
                    )
                ]
            )

        )
        page.update()

    def view_main_page(e):
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
            default_appbar,
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
    page.title = "Swiftype"
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
        title=ft.TextButton("Swiftype", on_click=redirect(), icon="keyboard"),
        center_title=False,
        actions=[
            ft.IconButton(
                "replay",
                on_click=view_main_page,
            ),
            dropdown_words,
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


ft.app(target=homepage)
