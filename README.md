# Alarm-System

A Raspberry Pi based alarm controller written in Python. The Pi watches a log file for a motion/amplitude value and, when the value becomes non-zero, switches on a 12 V siren for a fixed time and then re-arms itself.

Built as my final year project.

## How it works

```
 [ sensor / scanner ]        [ Raspberry Pi ]              [ 12 V side ]
  writes Amplitude=N   --->   Alarm.py polls the   --->   Solid-state relay  --->  12 V siren
  into scanLog.txt            file every 0.5 s             (driven by GPIO pin)
```

1. Some other process writes a line such as `Amplitude=0` or `Amplitude=1` to `scanLog.txt`.
2. `Alarm.py` reads the file continuously.
3. If every `Amplitude=` value is `0`, nothing happens.
4. If a value is greater than `0`, the siren pin goes HIGH for 10 seconds.
5. The siren is switched off, the file is reset to `Amplitude=0`, and monitoring resumes.

## Hardware

| Part | Purpose |
|------|---------|
| Raspberry Pi (any model with a 40-pin header) | Runs the script |
| 12 V siren | The alarm |
| Solid-state relay (SSR) | Switches the 12 V siren. The Pi cannot do this itself: its GPIO pins output 3.3 V at only a few mA |
| 12 V power supply | Powers the siren |

### Wiring

- SSR input (+) -> Pi physical pin **3** (BOARD numbering, GPIO2)
- SSR input (-) -> any Pi GND pin (e.g. physical pin 6)
- SSR output side in series with the siren: 12 V supply (+) -> SSR -> siren (+), siren (-) -> 12 V supply (-)

> Check that your SSR's input range accepts 3.3 V and that it is rated for the siren's current. The script assumes an **active-high** relay (HIGH = siren on).

## Software requirements

- Raspberry Pi OS with Python 3.8+
- `RPi.GPIO` (preinstalled on Raspberry Pi OS; otherwise `sudo apt install python3-rpi.gpio`)

## Installation

```bash
git clone https://github.com/MahmoudRaafat93/Alarm-System.git
cd Alarm-System
```

## Usage

```bash
python3 Alarm.py
```

Options (all optional):

| Flag | Default | Description |
|------|---------|-------------|
| `--log-file` | `/home/pi/Desktop/scanLog.txt` | File watched for `Amplitude=` values |
| `--pin` | `3` | Physical (BOARD) pin connected to the relay |
| `--duration` | `10` | Seconds the siren stays on |
| `--poll` | `0.5` | Seconds between checks of the file |

Example:

```bash
python3 Alarm.py --log-file /home/pi/scanLog.txt --duration 20
```

### Testing without a sensor

In a second terminal, simulate a detection:

```bash
echo "Amplitude=1" > /home/pi/Desktop/scanLog.txt
```

The siren should sound for `--duration` seconds and the file should return to `Amplitude=0`.

### Run at boot (systemd)

Create `/etc/systemd/system/alarm.service`:

```ini
[Unit]
Description=Alarm-System
After=multi-user.target

[Service]
User=pi
WorkingDirectory=/home/pi/Alarm-System
ExecStart=/usr/bin/python3 /home/pi/Alarm-System/Alarm.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now alarm.service
journalctl -u alarm.service -f    # live logs
```

## Log file format

```
Amplitude=0     # idle
Amplitude=1     # triggers the alarm (any value > 0 does)
```

## Troubleshooting

| Symptom | Check |
|---------|-------|
| Siren never sounds | Relay wiring/polarity, relay input voltage range, `--pin` matches the physical pin used |
| Script exits with a permission error | Run as a user in the `gpio` group (default `pi` user is) |
| Nothing happens after writing `Amplitude=1` | Confirm the path passed to `--log-file` matches the file your sensor writes |
| Siren stays on after stopping the script | Should not happen (the pin is driven LOW on exit); check the relay is not latched/wired normally-closed |

## Known limitations / ideas

- Detection depends on an external process writing `Amplitude=`; polling a file is simple but not instant. A GPIO input or MQTT message would be more direct.
- No arming/disarming and no notification (SMS/email/push) yet.
- Single siren output, fixed on-time.

## Author

Mahmoud Raafat, [@MahmoudRaafat93](https://github.com/MahmoudRaafat93)
