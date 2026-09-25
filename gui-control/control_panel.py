"""
Control Panel GUI - Alarm System
---------------------------------
Fullscreen Tkinter control panel with three pages:
  - StartPage : navigation hub
  - Manual    : manual ON/OFF control
  - Countdown : countdown timer with numeric keypad popup

Rewritten for Python 3. GPIO code is left commented out since it
depends on running on the actual Raspberry Pi hardware - uncomment
the marked lines and the `import RPi.GPIO as GPIO` line at the top
when deploying on the Pi.

Run with:  python3 control_panel.py
Exit with the "x" key.
"""

import sys
import time
import tkinter as tk
from tkinter import CENTER, DISABLED, NORMAL

# import RPi.GPIO as GPIO

# --- Raspberry Pi GPIO settings (uncomment on real hardware) ---
# SYS_PIN = 40  # physical pinout 11
# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(SYS_PIN, GPIO.OUT)
# GPIO.output(SYS_PIN, GPIO.LOW)  # start OFF

FONT_1 = ("Verdana", 16, "bold")
FONT_2 = ("Helvetica", 24, "bold")
FONT_3 = ("Helvetica", 30, "bold")
LABEL_FONT = ("Helvetica", 34)


class ControlApp(tk.Tk):
    """Main application window holding all pages."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attributes("-fullscreen", True)
        self.wm_title("Control Unit")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for page in (StartPage, Manual, Countdown):
            frame = page(container, self)
            self.frames[page] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            frame.config(background="black")

        self.show_frame(StartPage)

    def show_frame(self, page):
        self.frames[page].tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        label = tk.Label(self, text="Project Name", font=FONT_1)
        label.pack(pady=75, padx=10)

        tk.Button(
            self, text="Manual", font=FONT_1,
            command=lambda: controller.show_frame(Manual),
            bg="bisque2", height=2, width=10,
        ).place(relx=.3, rely=.4, anchor="center")

        tk.Button(
            self, text="Countdown", font=FONT_1,
            command=lambda: controller.show_frame(Countdown),
            bg="bisque2", height=2, width=10,
        ).place(relx=.8, rely=.4, anchor="center")

        # Shutdown / Restart - disabled until confirmed safe to use
        # tk.Button(self, text="Shutdown", font=FONT_1,
        #           command=lambda: os.system("sudo shutdown -h now"),
        #           bg="bisque2", height=2, width=10
        #           ).place(relx=.3, rely=.6, anchor="center")
        # tk.Button(self, text="Restart", font=FONT_1,
        #           command=lambda: os.system("sudo shutdown -r now"),
        #           bg="bisque2", height=2, width=10
        #           ).place(relx=.8, rely=.6, anchor="center")


class Manual(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        label = tk.Label(self, text="Manual", font=FONT_1)
        label.pack(pady=75, padx=10)

        tk.Label(
            self, text="Status:", font=FONT_2, bg="silver", fg="#FFFFFF",
            padx=20, pady=20,
        ).place(relx=.3, rely=.2, anchor="center")

        self.status_label = tk.Label(
            self, text="OFF", font=FONT_2, bg="silver", fg="red",
            padx=10, pady=10,
        )
        self.status_label.place(relx=.8, rely=.2, anchor="center")

        tk.Button(
            self, text="Run", font=FONT_1, command=self.turn_on,
            bg="bisque2", height=2, width=15,
        ).place(relx=.3, rely=.4, anchor="center")

        tk.Button(
            self, text="Stop", font=FONT_1, command=self.turn_off,
            bg="bisque2", height=2, width=15,
        ).place(relx=.8, rely=.4, anchor="center")

        tk.Button(
            self, text="To Home", font=FONT_1,
            command=lambda: (self.reset(), controller.show_frame(StartPage)),
            bg="bisque2", height=2, width=15,
        ).place(relx=.3, rely=.6, anchor="center")

        tk.Button(
            self, text="To Countdown", font=FONT_1,
            command=lambda: (self.reset(), controller.show_frame(Countdown)),
            bg="bisque2", height=2, width=15,
        ).place(relx=.8, rely=.6, anchor="center")

    def reset(self):
        self.turn_off()

    def turn_on(self):
        # GPIO.output(SYS_PIN, GPIO.HIGH)
        self.status_label.config(text="ON", fg="green")

    def turn_off(self):
        # GPIO.output(SYS_PIN, GPIO.LOW)
        self.status_label.config(text="OFF", fg="red")


class Countdown(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.minutes = 0        # minutes set by the user
        self.go_on = False      # whether the countdown loop should keep running
        self.time_str = tk.StringVar()

        label = tk.Label(
            self, textvariable=self.time_str, font=LABEL_FONT,
            bg="black", fg="red", relief="raised", bd=1,
        )
        label.place(relx=.5, rely=.3, anchor="center")
        self.time_str.set(self.formatter(self.minutes * 60))

        self.entry = tk.Entry(self, width=5)
        self.entry.place(relx=.8, rely=.4, anchor="center")
        self.entry.focus()

        tk.Label(self, text="Timer", font=FONT_1).pack(pady=75, padx=10)

        tk.Button(
            self, text="Set", font=FONT_1, command=self.on_set,
            bg="bisque2", height=2, width=10,
        ).place(relx=.3, rely=.4, anchor="center")

        tk.Button(
            self, text="Set&Start", font=FONT_1,
            command=lambda: (self.on_set(), self.count_down()),
            bg="bisque2", height=2, width=10,
        ).place(relx=.3, rely=.6, anchor="center")

        tk.Button(
            self, text="Reset", font=FONT_1, command=self.reset,
            bg="bisque2", height=2, width=10,
        ).place(relx=.8, rely=.6, anchor="center")

        tk.Button(
            self, text="To Home", font=FONT_1,
            command=lambda: (self.reset(), controller.show_frame(StartPage)),
            bg="bisque2", height=2, width=10,
        ).place(relx=.8, rely=.8, anchor="center")

        tk.Button(
            self, text="To Manual", font=FONT_1,
            command=lambda: (self.reset(), controller.show_frame(Manual)),
            bg="bisque2", height=2, width=10,
        ).place(relx=.3, rely=.8, anchor="center")

        tk.Button(
            self, text="Open Keypad", command=self.open_keypad,
        ).place(relx=.1, rely=.1, anchor="center")

    # --- time helpers -------------------------------------------------

    def formatter(self, sec):
        days, r1 = divmod(sec, 86400)
        hours, r2 = divmod(r1, 3600)
        mins, sec = divmod(r2, 60)
        return "{:02d}:{:02d}:{:02d}:{:02d}".format(days, hours, mins, sec)

    def count_down(self):
        self.turn_on()
        self.go_on = True

        for t in range(self.minutes * 60 - 1, -1, -1):
            self.time_str.set(self.formatter(t))
            self.update()

            # delay ~1 second, but stay responsive to UI events
            for _ in range(2):
                time.sleep(0.5)
                self.update()

            if not self.go_on:
                self.turn_off()
                return

        self.reset()

    def on_set(self):
        try:
            self.minutes = int(self.entry.get())
        except ValueError:
            self.minutes = 0
        self.time_str.set(self.formatter(self.minutes * 60))
        self.update()
        self.entry.config(state=DISABLED)

    def reset(self):
        self.entry.config(state=NORMAL)
        self.entry.delete(0, "end")
        self.go_on = False
        self.minutes = 0
        self.time_str.set(self.formatter(self.minutes * 60))
        self.turn_off()
        self.update()

    def turn_on(self):
        # GPIO.output(SYS_PIN, GPIO.HIGH)
        pass

    def turn_off(self):
        # GPIO.output(SYS_PIN, GPIO.LOW)
        pass

    # --- numeric keypad popup -----------------------------------------

    def open_keypad(self):
        """Open a small popup window with a numeric keypad to type
        minutes into, instead of using the keyboard."""
        popup = tk.Toplevel(self)
        popup.title("Enter Time In Minutes")

        tk.Label(popup, text="Enter Time In Minutes").grid(
            row=0, column=0, columnspan=3, sticky="nsew", pady=5
        )

        box = tk.Entry(popup, justify=CENTER)
        box.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=5)
        box.insert(0, "0")
        box.focus()

        state = {"new_num": True}

        def display(value):
            box.delete(0, tk.END)
            box.insert(0, value)

        def num_press(digit):
            current = box.get()
            if state["new_num"]:
                state["new_num"] = False
                display(digit)
            else:
                display(current + digit)

        def backspace():
            current = box.get()[:-1]
            if current == "":
                state["new_num"] = True
                current = "0"
            display(current)

        def confirm():
            self.entry.config(state=NORMAL)
            self.entry.delete(0, "end")
            self.entry.insert(0, box.get())
            popup.destroy()

        digits = "1234567890"
        for i, digit in enumerate(digits):
            row = 2 + i // 3
            col = i % 3
            tk.Button(
                popup, text=digit, height=2, width=5, bg="bisque2",
                command=lambda d=digit: num_press(d),
            ).grid(row=row, column=col)

        tk.Button(
            popup, text="Back", command=backspace, bg="bisque2",
            height=2, width=5,
        ).grid(row=6, column=0, sticky="nsew")

        tk.Button(
            popup, text="Set", command=confirm, bg="bisque2",
            height=2, width=5,
        ).grid(row=6, column=1, columnspan=2, sticky="nsew")


if __name__ == "__main__":
    app = ControlApp()
    app.bind("x", lambda event: sys.exit())
    app.mainloop()
