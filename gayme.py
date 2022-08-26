import asyncio
import random
import math
import numpy
import string
from pynput import keyboard

import keys
import sounds
import play
from common import *


async def welcome():
    active_set = set()
    for i in range(-140, 255):
        async with Frame(0.004):
            active_set.add(random.choice(specs).led_id)
            act = random.sample(list(active_set), len(active_set) // 2)
            act = color_ids(act, 255, 160, 224)
            render(blend(pure(i, 0.627 * i, 0.878 * i), act, max), [0, 0, 0])


async def oem_beat(count, beat_t):
    begin = time.perf_counter()
    oem = [spec for spec in specs if spec.led_id not in keys.onboard]
    while (t := time.perf_counter()) < begin + count * beat_t:
        brightness = fclip(200 - 200 * ((t - begin) % beat_t) / beat_t)
        render(color_specs(oem, *[brightness] * 3))
        await asyncio.sleep(0.003)


async def beat():
    async with Frame(2.55):
        beat_t = 60 / 184
        bases = [[70, 100, 70], [70, 70, 100], [130, 78, 52], [0, 0, 0], [160, 224, 160], [0, 0, 0]]
        makes = [[255, 0, 255], [255, 200, 80], [0, 255, 255], [255, 255, 255], [160, 224, 160], [0, 0, 0]]
        board = list(keys.onboard)
        deltas = [beat_t] * 16 + [beat_t / 2] * 16 + [beat_t / 4] * 16 + [beat_t * 4]
        changes = [0, 8, 16, 32, 48, 49]
    for i, delta in enumerate(deltas):
        async with Frame(delta):
            if i in changes:
                random.shuffle(board)
                colors = pure(*bases[changes.index(i)])
                make = makes[changes.index(i)]
                start = i
            led = [board[i - start]]
            colors = blend(colors, color_ids(led, *make), alpha_blend(1.0))
            render(colors)
    for i in range(60 * 2 - 1):
        async with Frame(beat_t / 2):
            if i == 0:
                oem = asyncio.create_task(oem_beat(60, beat_t))
            if i % 16 == 0:
                base = color_ids(keys.onboard, *randcv(0.4))
            if i % 2 == 0:
                circ = icue.led_id_of_key(random.choice(string.ascii_letters + string.digits))
                spec = [k for k in specs if k.led_id == circ][0]
                basecolor = numpy.array(randcv())
            else:
                basecolor = numpy.array(invhue(*basecolor))
            matches = [k for k in specs if abs(k.center - spec.center) <= 80]
            additive = []
            for match in matches:
                d = abs(spec.center - match.center)
                a = math.exp(-0.5 * (d / 26) ** 2)
                additive += color_specs([match], *(basecolor * a))
            render(blend(base, additive))
    async with Frame(beat_t * 4):
        render([], [0, 0, 0])
        await oem
    render([], [127, 127, 127])
    await oem_beat(999, beat_t)


async def handler(beat_t):
    stop = False
    
    def on_press(key):
        nonlocal stop
        stop = True
        return False

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    while not stop:
        await asyncio.sleep(0.02)
    sounds.select.play()
    beat_t.cancel()
    sounds.circles.fadeout(1500)
    sounds.pausing.play(fade_ms=500)
    for i in range(256):
        async with Frame(1.0 / 256):
            i = 255 - i
            render(pure(i, i, i))
    import charts.welcome_chart as cht
    await play.play(cht.track, cht.notes, cht.keymapping)


async def main():
    sounds.welcome.play()
    sounds.circles.play()
    welcome_t = asyncio.create_task(welcome())
    beat_t = asyncio.create_task(beat())
    await welcome_t
    handler_t = asyncio.create_task(handler(beat_t))
    try:
        await beat_t
    except asyncio.CancelledError:
        print("Beat off!")
    await handler_t


if __name__ == "__main__":
    asyncio.run(main())
