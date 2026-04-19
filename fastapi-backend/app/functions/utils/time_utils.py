"""Time utility functions for route calculations."""

from datetime import datetime, timedelta


def time_difference_seconds(time1, time2):
    """Calculate the difference in seconds between two time strings (HH:MM:SS)."""
    def to_seconds(t):
        h, m, s = map(int, t.split(":"))
        return h * 3600 + m * 60 + s

    return to_seconds(time1) - to_seconds(time2)


def add_minutes_to_time_str(time_str, minutes):
    """Add minutes to a time string in HH:MM:SS format."""
    time_format = "%H:%M:%S"
    time_obj = datetime.strptime(time_str, time_format)
    new_time = time_obj + timedelta(minutes=minutes)
    return new_time.strftime(time_format)


def add_seconds_to_time_str(time_str, seconds):
    """Add seconds to a time string in HH:MM:SS format."""
    time_format = "%H:%M:%S"
    time_obj = datetime.strptime(time_str, time_format)
    new_time = time_obj + timedelta(seconds=seconds)
    return new_time.strftime(time_format)
