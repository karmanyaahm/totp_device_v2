import rtc

TIME_ZONE = -5 * 60 * 60 # I'm in CDT, UTC -0500, this makes sure the clock is UTC not local time

ext_rtc.save_time(TIME_ZONE)
print(ext_rtc.get_time())

