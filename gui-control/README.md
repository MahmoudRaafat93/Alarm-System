# GUI Control Panel

A Tkinter-based fullscreen control panel for the Alarm System, intended
to run directly on the Raspberry Pi's connected display.

This is an **optional front-end** to the main alarm system — it does
not replace or change the core alarm logic, it just gives a touch-friendly
way to trigger and monitor it manually.

## Attribution

This GUI was **not originally written from scratch as part of this
project**. It started as a ready-made Tkinter control-panel script
found elsewhere, which was downloaded to adapt and integrate with
this alarm system later. It's included here as a work-in-progress
starting point, not as original authorship — the code has been
cleaned up (ported to Python 3, bugs fixed) but the core structure
and design are not original.

## Features

- **Start Page** — navigation hub with buttons to the Manual and
  Countdown screens.
- **Manual** — Run / Stop buttons to switch the system ON/OFF directly,
  with a live status indicator.
- **Countdown** — set a duration in minutes and run a countdown timer
  that turns the system ON, then automatically OFF when it reaches
  zero. Includes an on-screen numeric keypad as an alternative to
  typing on a keyboard.

## Requirements

- Python 3
- Tkinter (usually included with Python; on Raspberry Pi OS install
  with `sudo apt install python3-tk` if missing)
- `RPi.GPIO` — only required on the actual Raspberry Pi hardware

## Current status

The GPIO calls that actually switch the hardware pin are **commented
out** in `control_panel.py`. As it stands, the app is a working UI
prototype: the buttons and timer all function, but nothing physical
is triggered yet. To connect it to the real alarm hardware:

1. Uncomment `import RPi.GPIO as GPIO` and the GPIO setup block at the
   top of the file.
2. Uncomment the `GPIO.output(...)` lines inside `turn_on()` /
   `turn_off()` in the `Manual` and `Countdown` classes.
3. Adjust `SYS_PIN` to match the physical pin the alarm hardware is
   wired to.

## Usage

```bash
python3 control_panel.py
```

Press `x` on the keyboard to exit fullscreen mode and close the app.
