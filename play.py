from typing import Any, Dict, List
from types import SimpleNamespace
import numpy
from pynput import keyboard

from common import *
from keys import *
import sounds
# import matplotlib.pyplot as plotlib


# a key is represented by the corresponding led id.
key_to_pos = {k.led_id: k.center for k in specs}
render_keys = [
    CLK_GraveAccentAndTilde, CLK_1, CLK_2, CLK_3, CLK_4, CLK_5, CLK_6, CLK_7, CLK_8, CLK_9, CLK_0, CLK_MinusAndUnderscore,CLK_EqualsAndPlus, CLK_Backspace, CLK_NumLock, CLK_KeypadSlash, CLK_KeypadAsterisk,
    CLK_Tab, CLK_Q, CLK_W, CLK_E, CLK_R, CLK_T, CLK_Y, CLK_U, CLK_I, CLK_O, CLK_P, CLK_BracketLeft, CLK_BracketRight, CLK_Keypad7, CLK_Keypad8, CLK_Keypad9, CLK_Backslash,
    CLK_CapsLock, CLK_A, CLK_S, CLK_D, CLK_F, CLK_G, CLK_H, CLK_J, CLK_K, CLK_L, CLK_SemicolonAndColon, CLK_ApostropheAndDoubleQuote, CLK_Enter, CLK_Keypad4, CLK_Keypad5, CLK_Keypad6,
    CLK_LeftShift, CLK_Z, CLK_X, CLK_C, CLK_V, CLK_B, CLK_N, CLK_M, CLK_CommaAndLessThan, CLK_PeriodAndBiggerThan, CLK_SlashAndQuestionMark, CLK_RightShift, CLK_Keypad1, CLK_Keypad2, CLK_Keypad3
]
non_render_keys = [k for k in onboard if k not in render_keys]


def binary_lit(num, keys):
    lit = []
    for k in keys:
        if num % 2 != 0:
            lit.append(k)
        num //= 2
    return lit


class Note:
    def __init__(self, key: int, t: float, color):
        self.j = 0
        self.key = key
        self.t = t
        self.color = numpy.array(color)


def judge(t: float, down_key: int, notes: List[Note]):
    # notes should be sorted according to t.
    judges = SimpleNamespace(perfect=0.06, good=0.11)
    for note in notes:
        if note.j:
            continue
        if note.key == down_key and abs(note.t - t) < 1:
            print(t - note.t)
            if abs(note.t - t) < judges.perfect:
                return note, 2
            elif abs(note.t - t) < judges.good:
                return note, 1
    return None, 0


def play_render(t: float, notes: List[Note]):
    # working_area = (0, 0, 300, 200)
    lookahead = 1.0
    note_box_size = 26.0
    note_velocity = 240.0
    
    colors = color_ids(onboard, 0, 0, 0)
    jcolor = burst_color if burst_color is not rainbow_color else perfect_result
    colors = blend(colors, color_ids(non_render_keys, *jcolor), alpha_blend(1.0))
    for note in notes:
        if abs(note.t - t) > lookahead:
            continue
        if note.j:
            continue
        note_pos_1 = key_to_pos[note.key] + note_velocity * (note.t - t)
        note_pos_2 = key_to_pos[note.key] - note_velocity * (note.t - t)
        for note_pos in [note_pos_1, note_pos_2]:
            for key in render_keys:
                if abs(key_to_pos[key].imag - note_pos.imag) > 6:
                    continue
                dist = abs(note_pos - key_to_pos[key])
                if dist < note_box_size:
                    a = 1 - dist / note_box_size
                    rgb = note.color * a
                    colors = blend(colors, color_ids([key], *rgb))
        colors = blend(colors, color_ids([note.key], *perfect_result))
    render(colors)


burst_time = -1
miss_color = numpy.array([255, 64, 0])
good_color = numpy.array([32, 255, 64])
rainbow_color = "rainbow"
perfect_color = rainbow_color
perfect_result = numpy.array([255, 255, 255])
burst_color = perfect_color


async def oem_burst():
    try:
        oem = [spec for spec in specs if spec.led_id not in onboard]
        while burst_time > -100:
            t = time.perf_counter()
            dur = 0.6
            a = max(0, dur - (t - burst_time)) / dur
            if burst_color is not rainbow_color:
                render(color_specs(oem, *(burst_color * a)))
            else:
                phases = numpy.angle([k.center - (165 + 120j) for k in oem]) + t
                colors = []
                for k, phase in zip(oem, phases):
                    colors += color_specs([k], *chsv(phase, 0.8, a))
                render(colors)
            await asyncio.sleep(0.008)
    except Exception:
        import traceback; traceback.print_exc()


async def results(chart: List[Note], duration: float):
    c = [2] * len(onboard)
    up = lambda i, v: c.__setitem__(i, min(c[i], v))
    for note in chart:
        up(min(len(c) - 1, int(note.t / duration * len(c))), note.j)
    c = [[miss_color, good_color, perfect_result, miss_color][v] for v in c]
    base = pure(255, 160, 224)
    sounds.applause.play()
    for i in range(len(c) + 1):
        async with Frame(0.008):
            colors = c[:i] + [[0, 0, 0]] * (len(c) - i)
            colors = [color_ids([k], *v)[0] for k, v in zip(onboard, colors)]
            render(blend(base, colors, alpha_blend(1.0)))


async def fade_pause_loop(delta):
    await asyncio.sleep(delta)
    sounds.pausing.fadeout(500)


async def play(music: str, chart: List[Note], keymap: Dict[Any, int]):
    global burst_color, burst_time

    def on_press(key):
        nonlocal seeya
        if seeya == False and key == keyboard.Key.esc:
            seeya = True
            return False
        try:
            if key.vk in keymap:
                press_queue.append((keymap[key.vk], time.perf_counter() - 0.02))
        except AttributeError:
            if key in keymap:
                press_queue.append((keymap[key], time.perf_counter() - 0.02))

    seeya = None
    press_queue = []
    sounds.mixer.music.load(music)
    await asyncio.sleep(0.5)
    fade_t = asyncio.create_task(fade_pause_loop(1.8))
    sounds.mixer.music.play()
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    burst_t = asyncio.create_task(oem_burst())
    reset_time = 0.0
    start_time = time.perf_counter()
    while sounds.mixer.music.get_busy():
        await asyncio.sleep(0)
        t = sounds.mixer.music.get_pos() / 1000.0
        if press_queue:
            for k, pt in press_queue:
                note, j = judge(t - time.perf_counter() + pt, k, chart)
                if j:
                    note.j = j
                    burst_time = time.perf_counter()
                    if j == 2:
                        if time.perf_counter() >= reset_time:
                            burst_color = perfect_color
                    if j == 1:
                        reset_time = time.perf_counter() + 0.4
                        burst_color = good_color
            press_queue.clear()
        for note in chart:
            if t > note.t + 0.09 and not note.j:
                note.j = -1
                burst_time = time.perf_counter()
                reset_time = time.perf_counter() + 0.5
                burst_color = miss_color
        play_render(t, chart)
    duration = time.perf_counter() - start_time
    for i in range(0, 255, 2):
        async with Frame(0.005):
            render(pure(255 - i, 255 - i, 255 - i))
    await asyncio.sleep(1.0)
    burst_time = -128
    await fade_t
    await burst_t
    seeya = False
    await results(chart, duration)
    while not seeya:
        await asyncio.sleep(0.02)
    sounds.seeya.play()
    await asyncio.sleep(3.5)
