

This is a stopgap solution. I'm working on a much smaller and more convinient version of this based on a custom PCB coming soon.

I wrote the display code in the second half of 'totp/__init__.py'. If you connect to the Badger using `rshell` or `thonny`, you can run `set_time.py` to save your computer's time to the RTC.

- Notes: This was made before the Badger2040 W was released. I know that's a board with an RTC integrated, but that's not supported.

The main sauce is the TOTP directory, rtc.py, set_time.py, otp.json. Other than that, the clock has minor changes to interact with the RTC if you're setting time manually. The launcher simply exposes the TOTP app.

This project simply packages a bunch of different people's projects together. Huge thanks to:
- Pimoroni for the Badger2040, BadgerOS, and associated e-ink libraries.
- [Edd Mann's Pico 2FA TOTP](https://github.com/eddmann/pico-2fa-totp) library for doing all the actual TOTP computations in MicroPython.
- [Peter Hinch's DS3231 Driver](https://github.com/peterhinch/micropython-samples/blob/master/DS3231/ds3231_port.py)
- My 3D Printed case was inspired by <https://www.thingiverse.com/thing:5997974> and <https://www.thingiverse.com/thing:5271558> and used [this DS3231 model](https://grabcad.com/library/hw-84-ds3231-real-time-clock-1) for sizing.
