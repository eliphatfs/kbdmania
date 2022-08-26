import os
import string
import icue
import keys
from keys import *
import vkey
from play import Note


src_r = [
    'm', 5,
    'k', 5.5,
    'n', 9.75,
    'n', 13.0,
    'k', 13.75,
    'n', 17.0,
    'm', 18.75,
    'j', 19.0,
    'n', 18.75 + 2,
    'h', 19.0 + 2,
    'o', 18.0 + 4,
    '0', 18.25 + 4,
    'p', 18.5 + 4,
    'o', 18.0 + 6,
    '0', 18.25 + 6,
    'p', 18.5 + 6,
    'm', 18.75 + 8,
    'j', 19.0 + 8,
    'n', 18.75 + 10,
    'h', 19.0 + 10,
    'o', 18.0 + 12,
    '0', 18.25 + 12,
    'p', 18.5 + 12,
    'o', 18.0 + 14,
    '0', 18.25 + 14,
    'p', 18.5 + 14,
]
for i in range(8):
    src_r.append('n3')
    src_r.append(34 + 0.5 * i)
for i in range(8, 16):
    src_r.append('n6')
    src_r.append(34 + 0.5 * i)
for i in range(16, 24):
    src_r.append('n3')
    src_r.append(34 + 0.5 * i)
for i in range(24, 29):
    src_r.append('n9')
    src_r.append(34 + 0.5 * i)
src_b = [
    '1', 2.0,
    'a', 2.0,
    'z', 6,
    'w', 9.5,
    '1', 10.0,
    'q', 14.0,
    'a', 14.0,
    '1', 18.0,
    'q', 18.25,
    '2', 18.5,
    '1', 18.0 + 2,
    'q', 18.25 + 2,
    '2', 18.5 + 2,
    'b', 18.75 + 4,
    'd', 19.0 + 4,
    'v', 18.75 + 6,
    's', 19.0 + 6,
    '1', 18.0 + 8,
    'q', 18.25 + 8,
    '2', 18.5 + 8,
    '1', 18.0 + 10,
    'q', 18.25 + 10,
    '2', 18.5 + 10,
    'b', 18.75 + 12,
    'd', 19.0 + 12,
    'v', 18.75 + 14,
    's', 19.0 + 14,
]


def conv_k(k):
    if k[0] == 'n' and len(k) == 2:
        if k[1] == '/':
            return CLK_KeypadSlash
        else:
            return getattr(keys, 'CLK_Keypad' + k[1])
    return icue.led_id_of_key(k)


notes = []
for k, t in zip(src_r[::2], src_r[1::2]):
    notes.append(Note(conv_k(k), t, [255, 80, 32]))
for k, t in zip(src_b[::2], src_b[1::2]):
    notes.append(Note(conv_k(k), t, [32, 255, 80]))
keymapping = {
    vkey.VK_NUMPAD0: CLK_Keypad0,
    vkey.VK_NUMPAD1: CLK_Keypad1,
    vkey.VK_NUMPAD2: CLK_Keypad2,
    vkey.VK_NUMPAD3: CLK_Keypad3,
    vkey.VK_NUMPAD4: CLK_Keypad4,
    vkey.VK_NUMPAD5: CLK_Keypad5,
    vkey.VK_NUMPAD6: CLK_Keypad6,
    vkey.VK_NUMPAD7: CLK_Keypad7,
    vkey.VK_NUMPAD8: CLK_Keypad8,
    vkey.VK_NUMPAD9: CLK_Keypad9,
    vkey.VK_MULTIPLY: CLK_KeypadAsterisk,
    vkey.VK_DIVIDE: CLK_KeypadSlash
}
for ch in string.digits + string.ascii_uppercase:
    keymapping[ord(ch)] = icue.led_id_of_key(ch)
track = os.path.join(
    os.path.dirname(__file__),
    'welcome_padded.ogg'
)
