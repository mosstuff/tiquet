import datetime
from app.config import reload_settings
from zoneinfo import ZoneInfo
settings=reload_settings()
# tzdata has to be installed but there is no need for it to be imported


def get_timezone():
    return ZoneInfo(settings.timezone)


def get_current_time_range(offset="0"):
    if 0 <= int(offset) <= 9:
        tz = get_timezone()
        now = datetime.datetime.now(tz)
        slot_interval = datetime.datetime.strptime(settings.slot_interval, "%H:%M").time()
        slot_minutes = slot_interval.hour * 60 + slot_interval.minute
        offset = datetime.datetime.strptime(offset, "%M").time()
        # Get the next available slot
        now_with_offset = now - datetime.timedelta(minutes=offset.minute)
        slot_start = now_with_offset - datetime.timedelta(minutes=now_with_offset.minute % 10, seconds=0,
                                                          microseconds=0) + datetime.timedelta(minutes=offset.minute)
        slot_end = slot_start + datetime.timedelta(minutes=slot_minutes)

        return slot_start, slot_end
    else:
        raise Exception("Invalid time offset! Must be between 0 and 9")


def get_current_time_range_str(offset=0):
    offset = str(offset)
    slot_start, slot_end = get_current_time_range(offset)
    return slot_start.strftime("%H:%M") + " - " + slot_end.strftime("%H:%M")


def get_next_time_range_str(offset=0):
    offset = str(offset)
    slot_start, slot_end = get_current_time_range(offset)
    slot_interval = datetime.datetime.strptime(settings.slot_interval, "%H:%M").time()
    slot_minutes = slot_interval.hour * 60 + slot_interval.minute

    slot_start = slot_start + datetime.timedelta(minutes=slot_minutes)
    slot_end = slot_start + datetime.timedelta(minutes=slot_minutes)

    return slot_start.strftime("%H:%M") + " - " + slot_end.strftime("%H:%M")


print(get_current_time_range_str(3))
print(get_next_time_range_str(3))