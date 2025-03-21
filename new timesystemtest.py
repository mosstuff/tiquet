import datetime
from app.config import reload_settings
from zoneinfo import ZoneInfo
settings = reload_settings()

def get_timezone():
    return ZoneInfo(settings.timezone) if hasattr(settings, "timezone") else ZoneInfo("UTC")

def get_next_time_range(offset=0):
    # Convert settings values to datetime.time objects
    event_begin = datetime.datetime.strptime(settings.event_begin, "%H:%M").time()
    event_end = datetime.datetime.strptime(settings.event_end, "%H:%M").time()
    slot_interval = datetime.datetime.strptime(settings.slot_interval, "%H:%M").time()
    slot_minutes = slot_interval.hour * 60 + slot_interval.minute

    # Get the current datetime and apply offset AFTER determining the slot
    tz = get_timezone()
    current_datetime = datetime.datetime.now(tz)

    current_minute = (current_datetime.minute // slot_minutes) * slot_minutes
    next_slot_start = current_datetime.replace(minute=current_minute, second=0, microsecond=0) + datetime.timedelta(minutes=slot_minutes)
    next_slot_start += datetime.timedelta(minutes=offset)
    next_slot_end = next_slot_start + datetime.timedelta(minutes=slot_minutes)

    # Ensure the time range is within event boundaries
    if next_slot_start.time() < event_begin:
        next_slot_start = current_datetime.replace(hour=event_begin.hour, minute=event_begin.minute, second=0,
                                                   microsecond=0)
        next_slot_start += datetime.timedelta(minutes=offset)
        next_slot_end = next_slot_start + datetime.timedelta(minutes=slot_minutes)
    elif next_slot_end.time() > event_end:
        return None  # No valid slots available

    return next_slot_start.strftime("%H:%M") + " - " + next_slot_end.strftime("%H:%M")


def get_current_time_range(offset=0):
    # Convert settings values to datetime.time objects
    event_begin = datetime.datetime.strptime(settings.event_begin, "%H:%M").time()
    event_end = datetime.datetime.strptime(settings.event_end, "%H:%M").time()
    slot_interval = datetime.datetime.strptime(settings.slot_interval, "%H:%M").time()
    slot_minutes = slot_interval.hour * 60 + slot_interval.minute

    # Get the current datetime and apply offset AFTER determining the slot
    tz = get_timezone()
    current_datetime = datetime.datetime.now(tz)
    current_minute = (current_datetime.minute // slot_minutes) * slot_minutes
    slot_start = current_datetime.replace(minute=current_minute, second=0, microsecond=0)
    slot_start += datetime.timedelta(minutes=offset)
    slot_end = slot_start + datetime.timedelta(minutes=slot_minutes)

    # Ensure the time range is within event boundaries
    if slot_start.time() < event_begin:
        slot_start = current_datetime.replace(hour=event_begin.hour, minute=event_begin.minute, second=0, microsecond=0)
        slot_start += datetime.timedelta(minutes=offset)
        slot_end = slot_start + datetime.timedelta(minutes=slot_minutes)
    elif slot_end.time() > event_end:
        return None  # No valid slots available

    return slot_start.strftime("%H:%M") + " - " + slot_end.strftime("%H:%M")

def getCurrentTime():
    tz = get_timezone()
    current_datetime = datetime.datetime.now(tz)
    return current_datetime

print("Current Slot: " + get_current_time_range(0))
print("Current Slot + 3 minutes: " + get_current_time_range(3))
print("Next Slot: " + get_next_time_range(0))
print("Next Slot + 3 minutes: " + get_next_time_range(3))

print("Current time: " + getCurrentTime().strftime("%H:%M"))