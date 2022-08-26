import os
import ctypes
import copy
from typing import List

import keys


class ICueException(RuntimeError):
    pass


class led_color_t(ctypes.Structure):
    led_id: ctypes.c_int
    r: ctypes.c_int
    g: ctypes.c_int
    b: ctypes.c_int
    _fields_ = [
        ('led_id', ctypes.c_int),
        ('r', ctypes.c_int),
        ('g', ctypes.c_int),
        ('b', ctypes.c_int)
    ]

    @property
    def name(self):
        return keys.lookup[self.led_id]


class led_position_t(ctypes.Structure):
    led_id: ctypes.c_int
    top: ctypes.c_double
    left: ctypes.c_double
    height: ctypes.c_double
    width: ctypes.c_double
    _fields_ = [
        ('led_id', ctypes.c_int),
        ('top', ctypes.c_double),
        ('left', ctypes.c_double),
        ('height', ctypes.c_double),
        ('width', ctypes.c_double)
    ]

    @property
    def name(self):
        return keys.lookup[self.led_id]

    @property
    def center(self) -> complex:
        return 1j *(self.top + self.height / 2) + self.left + self.width / 2


class led_positions_t(ctypes.Structure):
    count: ctypes.c_int
    positions: List[led_position_t]
    _fields_ = [
        ('count', ctypes.c_int),
        ('positions', ctypes.POINTER(led_position_t))
    ]


class protocol_t(ctypes.Structure):
    _fields_ = [
        ('sdk_version', ctypes.c_char_p),
        ('server_version', ctypes.c_char_p),
        ('sdk_protocol_version', ctypes.c_int),
        ('server_protocol_version', ctypes.c_int),
        ('breaking_changes', ctypes.c_bool),
    ]


dll = os.path.abspath(os.path.join(os.path.dirname(__file__), "CUESDK.x64_2017.dll"))
cuesdk = ctypes.cdll.LoadLibrary(dll)


def err_check(result, func, args):
    last_error = get_last_error()
    if last_error != 0:
        raise ICueException(last_error)
    return result


def get_device_count() -> ctypes.c_int:
    func = cuesdk.CorsairGetDeviceCount
    func.restype = ctypes.c_int
    func.errcheck = err_check
    return func()

get_last_error = cuesdk.CorsairGetLastError
get_last_error.restype = ctypes.c_int

handshake = cuesdk.CorsairPerformProtocolHandshake
handshake.restype = protocol_t
handshake.errcheck = err_check


def get_led_positions_by_device_index(idx: int) -> List[led_position_t]:
    func = cuesdk.CorsairGetLedPositionsByDeviceIndex
    func.argtypes = (ctypes.c_int,)
    func.restype = ctypes.POINTER(led_positions_t)
    func.errcheck = err_check
    res: led_positions_t = func(idx).contents
    return [res.positions[i] for i in range(res.count)]


def get_led_positions() -> List[led_position_t]:
    res = []
    for i in range(get_device_count()):
        res.extend(get_led_positions_by_device_index(i))
    return res


def gamma_correction(colors: List[led_color_t], gamma=2.6) -> List[led_color_t]:
    colors = copy.deepcopy(colors)
    for col in colors:
        col.r = int((col.r / 255) ** gamma * 255)
        col.g = int((col.g / 255) ** gamma * 255)
        col.b = int((col.b / 255) ** gamma * 255)
    return colors


def set_led_colors(colors: List[led_color_t]) -> ctypes.c_bool:
    func = cuesdk.CorsairSetLedsColors
    func.argtypes = (ctypes.c_int, ctypes.POINTER(led_color_t))
    func.restype = ctypes.c_bool
    func.errcheck = err_check
    return func(len(colors), (led_color_t * len(colors))(*colors))


def export_led_list_to_csv(filename, device_index=None):
    if device_index is None:
        leds = get_led_positions()
    else:
        leds = get_led_positions_by_device_index(device_index)
    with open(filename, 'w') as fo:
        fo.write("name,id,top,left,width,height\n")
        for led in leds:
            fo.write(
                "%s,%d,%.2f,%.2f,%.2f,%.2f\n"
                % (led.name, led.led_id, led.top, led.left, led.width, led.height)
            )


def led_id_of_key(key: str):
    extend_dict = {i: getattr(keys, 'CLK_' + i) for i in '0123456789'}
    if key in extend_dict:
        return extend_dict[key]
    key = key.upper()
    func = cuesdk.CorsairGetLedIdForKeyName
    func.argtypes = (ctypes.c_char,)
    func.restype = ctypes.c_int
    func.errcheck = err_check
    return func(key.encode('ascii'))


handshake()
