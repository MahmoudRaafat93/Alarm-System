#!/usr/bin/env python3
"""Alarm-System: trigger a siren from a Raspberry Pi when motion is logged.

The script polls a text file (default: /home/pi/Desktop/scanLog.txt) for a
line of the form ``Amplitude=<number>``. While the value is 0 nothing happens.
As soon as it becomes greater than 0, the siren pin is driven HIGH for a fixed
time, then the file is reset to ``Amplitude=0`` and monitoring resumes.

The GPIO pin drives a solid-state relay (SSR), which switches the 12 V siren,
because the Pi's 3.3 V GPIO cannot supply 12 V or the siren's current.
"""

import argparse
import logging
import os
import re
import signal
import sys
import tempfile
import time
from pathlib import Path

import RPi.GPIO as GPIO

DEFAULT_LOG_FILE = "/home/pi/Desktop/scanLog.txt"
DEFAULT_PIN = 3          # physical (BOARD) pin number, same as the original wiring
DEFAULT_DURATION = 10    # seconds the siren stays on
DEFAULT_POLL = 0.5       # seconds between file checks

AMPLITUDE_RE = re.compile(r"Amplitude=\s*(-?\d+(?:\.\d+)?)")
RESET_CONTENT = "Amplitude=0\n"

log = logging.getLogger("alarm")


def motion_detected(path: Path) -> bool:
    """Return True if any 'Amplitude=<value>' in the file has value > 0."""
    try:
        text = path.read_text()
    except FileNotFoundError:
        return False
    return any(float(value) > 0 for value in AMPLITUDE_RE.findall(text))


def reset_log(path: Path) -> None:
    """Atomically rewrite the log file as 'Amplitude=0'.

    Writing to a temp file and renaming avoids the window in which the file
    doesn't exist (the original remove + create approach could race with
    whatever process writes the log).
    """
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=".scanLog-")
    try:
        with os.fdopen(fd, "w") as tmp:
            tmp.write(RESET_CONTENT)
        os.replace(tmp_name, path)
    except Exception:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def sound_alarm(pin: int, duration: int) -> None:
    log.warning("Motion detected - siren ON for %ds", duration)
    GPIO.output(pin, GPIO.HIGH)
    try:
        for second in range(duration):
            log.info("siren %d/%d", second + 1, duration)
            time.sleep(1)
    finally:
        GPIO.output(pin, GPIO.LOW)  # always switch the siren off
        log.info("Siren OFF")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--log-file", type=Path, default=Path(DEFAULT_LOG_FILE))
    parser.add_argument("--pin", type=int, default=DEFAULT_PIN,
                        help="physical (BOARD) pin driving the relay")
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION,
                        help="seconds the siren stays on")
    parser.add_argument("--poll", type=float, default=DEFAULT_POLL,
                        help="seconds between checks of the log file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")

    # Let systemd / `kill` stop the script cleanly (runs the finally block).
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

    if not args.log_file.exists():
        reset_log(args.log_file)

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(args.pin, GPIO.OUT, initial=GPIO.LOW)
    log.info("Watching %s (siren on pin %d)", args.log_file, args.pin)

    try:
        while True:
            if motion_detected(args.log_file):
                sound_alarm(args.pin, args.duration)
                reset_log(args.log_file)
                log.info("Reset - monitoring again")
            time.sleep(args.poll)
    except KeyboardInterrupt:
        log.info("Stopped by user")
    finally:
        GPIO.output(args.pin, GPIO.LOW)
        GPIO.cleanup()
    return 0


if __name__ == "__main__":
    sys.exit(main())
