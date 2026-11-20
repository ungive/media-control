import contextlib
import io
import json
from pathlib import Path
import runpy
import subprocess
import unittest
from unittest.mock import patch


PLUGIN = Path(__file__).resolve().parents[1] / "xbar-now-playing.1s.py"


class NowPlayingTests(unittest.TestCase):
    def render(self, data):
        output = io.StringIO()
        with patch("subprocess.check_output", return_value=json.dumps(data)):
            with patch("time.time", return_value=100):
                with contextlib.redirect_stdout(output):
                    runpy.run_path(str(PLUGIN), run_name="__main__")
        return output.getvalue().strip()

    def test_playing_without_elapsed_time_shows_track_without_timer(self):
        self.assertEqual(
            self.render({
                "playing": True,
                "timestampEpochMicros": 99000000,
                "durationMicros": 234506667,
                "title": "Near Dark",
                "artist": "Burial",
            }),
            "▶  Near Dark – Burial",
        )

    def test_playing_with_timing_shows_updated_position(self):
        self.assertEqual(
            self.render({
                "playing": True,
                "elapsedTimeMicros": 61000000,
                "timestampEpochMicros": 99000000,
                "durationMicros": 234506667,
                "title": "Near Dark",
                "artist": "Burial",
            }),
            "▶  1:02﹘3:54  Near Dark – Burial",
        )

    def test_missing_or_null_timing_shows_track_without_timer(self):
        timing = {
            "elapsedTimeMicros": 0,
            "timestampEpochMicros": 100000000,
            "durationMicros": 234506667,
        }
        for key in timing:
            for null_value in (False, True):
                with self.subTest(key=key, null_value=null_value):
                    data = dict(timing, playing=True, title="Near Dark", artist="Burial")
                    if null_value:
                        data[key] = None
                    else:
                        del data[key]
                    self.assertEqual(self.render(data), "▶  Near Dark – Burial")

    def test_zero_elapsed_time_is_valid(self):
        self.assertEqual(
            self.render({
                "playing": True,
                "elapsedTimeMicros": 0,
                "timestampEpochMicros": 100000000,
                "durationMicros": 234506667,
                "title": "Near Dark",
                "artist": "Burial",
            }),
            "▶  0:00﹘3:54  Near Dark – Burial",
        )

    def test_paused_without_timing_shows_track(self):
        self.assertEqual(
            self.render({"playing": False, "title": "Near Dark", "artist": "Burial"}),
            "⏸  Near Dark – Burial",
        )

    def test_no_media(self):
        self.assertEqual(self.render(None), "◼ No media")

    def test_requests_metadata_without_artwork(self):
        with patch("subprocess.check_output", return_value="null") as get_metadata:
            with contextlib.redirect_stdout(io.StringIO()):
                runpy.run_path(str(PLUGIN), run_name="__main__")
        get_metadata.assert_called_once_with(
            ["/opt/homebrew/bin/media-control", "get", "--micros", "--no-artwork"],
            text=True,
        )

    def test_command_failures_print_error_and_exit(self):
        errors = (
            subprocess.CalledProcessError(1, "media-control"),
            FileNotFoundError("media-control not found"),
            PermissionError("media-control is not executable"),
        )
        for error in errors:
            with self.subTest(error=type(error).__name__):
                output = io.StringIO()
                with patch("subprocess.check_output", side_effect=error):
                    with contextlib.redirect_stdout(output):
                        with self.assertRaises(SystemExit) as raised:
                            runpy.run_path(str(PLUGIN), run_name="__main__")
                self.assertEqual(raised.exception.code, 1)
                self.assertEqual(output.getvalue().strip(), str(error))


if __name__ == "__main__":
    unittest.main()
