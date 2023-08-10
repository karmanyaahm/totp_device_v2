
from time import time, sleep

import rtc
from machine import RTC

import json

import struct
from totp.sha1 import hmac_sha1
from totp.base32 import base32_decode

import badger2040
import badger_os

badger2040.system_speed(badger2040.SYSTEM_FAST) # lots of compute


state = {
    'last_t': 0,
    'scroll': 0,
}

badger_os.state_load("totp", state)

def totp(time, key, step_secs=30, digits=6):
    """
    Time-based One-Time Password (TOTP) implementation based on https://tools.ietf.org/id/draft-mraihi-totp-timebased-06.html
    >>> totp(1602659430, "DWRGVKRPQJLNU4GY", step_secs=30, digits=6)
    ('846307', 30)
    >>> totp(1602659435, "DWRGVKRPQJLNU4GY", step_secs=30, digits=6)
    ('846307', 25)
    >>> totp(1602659430, "DWRGVKRPQJLNU4GY", step_secs=30, digits=4)
    ('6307', 30)
    >>> totp(1602659430, "DWRGVKRPQJLNU4GY", step_secs=15, digits=6)
    ('524508', 15)
    """

    hmac = hmac_sha1(base32_decode(key), struct.pack(">Q", time // step_secs))
    offset = hmac[-1] & 0xF
    code = ((hmac[offset] & 0x7F) << 24 |
            (hmac[offset + 1] & 0xFF) << 16 |
            (hmac[offset + 2] & 0xFF) << 8 |
            (hmac[offset + 3] & 0xFF))
    code = str(code % 10 ** digits)
    return (
        "0" * (digits - len(code)) + code,
        step_secs - time % step_secs
    )


display = badger2040.Badger2040()


while True:
    last_scroll = state['scroll']
    if display.pressed(badger2040.BUTTON_DOWN):
        state['scroll'] += 6
    if display.pressed(badger2040.BUTTON_UP):
        state['scroll'] -= 6
    reached_end = 0

    data = json.load(open('otp.json', 'r'))
    assert type(data) is list
    if state['scroll'] <= 0:
        reached_end = -1
        state['scroll'] = 0
    if state['scroll'] + 6 >= len(data):
        reached_end = 1
        state['scroll'] = len(data) - len(data) % 6


    data = data[state['scroll'] : state['scroll'] + 6]
    print(state['scroll'], len(data))
    
    currtime = time()
    this_t = currtime // 30
    print(currtime)

    for n, val in enumerate(data):
        #print(val)
        assert val.get('algorithm', 'SHA1') == 'SHA1', 'Only sha1 is supported here'
        token = totp(currtime, val['secret'].upper(),  digits = val.get('digits', 6), step_secs=val.get('period', 30))
        print(token)
        data[n]['token'] = token[0]
        


    ## show the stuff

    display.led(128)
    display.font("sans")
    display.pen(15)
    display.clear()
    display.pen(0)



    time_left = 30 - (currtime % 30)
    display.thickness(7)
    
    line_offset = 20
    if reached_end == -1:
        display.pen(0)
        display.line(0,0,(badger2040.WIDTH * time_left) // 30, 0)
    elif reached_end == 0:
        display.pen(7)
        display.line(0,0,(badger2040.WIDTH * time_left) // 30, 0)
    elif reached_end == 1:
        display.pen(0)
        line_offset = 10
        display.line(0,badger2040.HEIGHT,(badger2040.WIDTH * time_left) // 30, badger2040.HEIGHT)

    display.pen(0)
    display.thickness(2)
    SCALE = .6
    for n, val in enumerate(data):
        
        num_size = display.measure_text(val['token'], SCALE)
        display.text(val['token'], badger2040.WIDTH - num_size, 20 * n + line_offset, scale = SCALE, rotation = 0)
        print(num_size)
        
        size = display.measure_text(val['label'], SCALE)
        while size + num_size > badger2040.WIDTH:
            val['label'] = val['label'][:-1]
            size = display.measure_text(val['label'], SCALE)
        
        display.text(val['label'], 0,20 * n + line_offset, scale = SCALE, rotation = 0)

        
        
    if (state['last_t'] == this_t and badger2040.woken_by_button() and last_scroll != state['scroll']): # only happens on battery really
        display.update_speed(badger2040.UPDATE_TURBO)
    else: display.update_speed(badger2040.UPDATE_FAST)
    display.update()
    
    state['last_t'] = this_t
    badger_os.state_save("totp", state)
    display.halt()
