#!/usr/bin/python3

import subprocess
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
        ["/opt/homebrew/bin/media-control", "get"], text=True
    )
except Exception as e:
    print(str(e))
    exit(1)
data = json.loads(output)
if data is None:
    print("\u25fc No media")
else:
    current_epoch = int(time.time() * 1000000)
    time_diff = current_epoch - data["timestampEpochMicros"]
    total_time = data["elapsedTimeMicros"] + data["playing"] * time_diff
    icon = "\u25b6" if data["playing"] else "\u23f8"
    print(
        (
            "\u25b6  " + format(total_time) + "\ufe58" + format(data["durationMicros"])
            if data["playing"]
            else "\u23f8"
        )
        + "  "
        + limit(data["title"], 64).strip()
        + " \u2013 "
        + limit(data["artist"], 64).strip()
    )
