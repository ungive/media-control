#!/usr/bin/python3

import subprocess
import sys
import time
import json


def format(duration):
    minutes = duration // 60000000
    seconds = (duration // 1000000) % 60
    return f"{minutes:01d}:{seconds:02d}"


def limit(text, max_length):
    if len(text) > max_length:
        return text[:max_length].rstrip() + "\u2026"
    return text


try:
    output = subprocess.check_output(
        ["/opt/homebrew/bin/media-control", "get", "--micros", "--no-artwork"], text=True
    )
except (subprocess.CalledProcessError, OSError) as e:
    print(str(e))
    sys.exit(1)
data = json.loads(output)
if data is None:
    print("\u25fc No media")
else:
    icon = "\u25b6" if data["playing"] else "\u23f8"
    elapsed_time = data.get("elapsedTimeMicros")
    timestamp = data.get("timestampEpochMicros")
    duration = data.get("durationMicros")
    if data["playing"] and all(
        value is not None for value in (elapsed_time, timestamp, duration)
    ):
        current_epoch = int(time.time() * 1000000)
        total_time = elapsed_time + current_epoch - timestamp
        icon += "  " + format(total_time) + "\ufe58" + format(duration)
    print(
        icon
        + "  "
        + limit(data["title"], 64).strip()
        + " \u2013 "
        + limit(data["artist"], 64).strip()
    )
