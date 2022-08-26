import asyncio
from typing import List
import icue
import operator
import time
import random
import colorsys
import numpy


specs = icue.get_led_positions()
id_set = set(spec.led_id for spec in specs)


def pure(*col):
    return [icue.led_color_t(spec.led_id, *map(int, col)) for spec in specs]


def color_specs(vspecs, *col):
    return [icue.led_color_t(spec.led_id, *map(int, col)) for spec in vspecs]


def color_ids(lids, *col):
    return [icue.led_color_t(spec, *map(int, col)) for spec in lids]


def render(colors: List[icue.led_color_t], bg=None, gamma=True):
    act_set = set() if bg is None else set(x.led_id for x in colors)
    send = colors + ([] if bg is None else color_ids(id_set - act_set, *bg))
    if gamma:
        send = icue.gamma_correction(send)
    return icue.set_led_colors(send)


def fclip(v):
    return max(min(v, 255), 0)


def cufunc(fn):
    fnw = lambda x: int(fn(x))
    return lambda c: icue.led_color_t(c.led_id, fnw(c.r), fnw(c.g), fnw(c.b))


cclip = cufunc(fclip)


def alpha_blend(alpha):
    return lambda a, b: int(a * (1 - alpha) + b * alpha)


def randchs(hue, sat, v=1.0):
    h = random.random() * hue
    s = random.random() * sat
    return [
        int(255 * comp) for comp in
        colorsys.hsv_to_rgb(h, s, v)
    ]


def randcolor():
    return [random.randint(0, 255) for _ in range(3)]


def randcv(v=1.0):
    return [
        int(255 * comp) for comp in
        colorsys.hsv_to_rgb(random.random(), random.random() * 0.65 + 0.3, v)
    ]


def chsv(h, s, v):
    return numpy.array([*colorsys.hsv_to_rgb(h, s, v)]) * 255


def invhue(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return [*colorsys.hsv_to_rgb((h + 0.5) % 1.0, s, v)]


def cmula(c: icue.led_color_t, a):
    return cufunc(lambda x: int(x * a))(c)


def blend(c1: List[icue.led_color_t], c2: List[icue.led_color_t], op=operator.add):
    d = {}
    for c in c1:
        d[c.led_id] = cclip(c)
    for c in c2:
        if c.led_id in d:
            o = d[c.led_id]
            d[c.led_id] = cclip(icue.led_color_t(
                c.led_id, op(o.r, c.r), op(o.g, c.g), op(o.b, c.b)
            ))
        else:
            d[c.led_id] = cclip(c)
    return list(d.values())


class Frame:
    def __init__(self, t: float) -> None:
        self.t = t

    async def __aenter__(self):
        self.exit = time.perf_counter() + self.t
        await asyncio.sleep(0)

    async def __aexit__(self, *_):
        while time.perf_counter() < self.exit:
            await asyncio.sleep(0)
