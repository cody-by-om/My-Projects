import tkinter as tk
import math
import time
import threading
import queue
import webbrowser
import subprocess


import os
from datetime import datetime

import speech_recognition as sr
import sounddevice as sd
import numpy as np
import pyttsx3


# =========================
# JARVIS SETTINGS
# =========================

APP_TITLE = "JARVIS AI"
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 650

SAMPLE_RATE = 16000
RECORD_SECONDS = 5


# =========================
# TEXT TO SPEECH
# =========================

speech_queue = queue.Queue()


def speech_worker():
    """Own the Windows TTS engine from one consistent thread."""

    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 175)
        engine.setProperty("volume", 1.0)
    except Exception as error:
        print("TTS initialization error:", error)
        return

    while True:
        text = speech_queue.get()

        if text is None:
            return

        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as error:
            print("TTS Error:", error)


threading.Thread(target=speech_worker, daemon=True).start()


def speak(text):
    """Queue text for the dedicated JARVIS voice thread."""

    print("JARVIS:", text)
    speech_queue.put(str(text))


# =========================
# SPEECH RECOGNITION
# =========================

recognizer = sr.Recognizer()
ui_queue = queue.Queue()


def post_ui(callback, *args, **kwargs):
    """Queue a UI update for the Tkinter main thread."""

    ui_queue.put((callback, args, kwargs))


def process_ui_queue():

    while True:

        try:
            callback, args, kwargs = ui_queue.get_nowait()
        except queue.Empty:
            return

        callback(*args, **kwargs)


def update_status(text, color):
    """Update a Tkinter label from the main UI thread."""

    post_ui(status_label.config, text=text, fg=color)


def update_command(text):
    """Update the command label from the main UI thread."""

    post_ui(command_label.config, text=text)


def listen():
    """Record microphone without PyAudio."""

    try:
        update_status("● Listening...", "#00ff88")

        audio = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16"
        )

        sd.wait()


        update_status("● Processing...", "#ffaa00")

        audio_bytes = audio.tobytes()

        audio_data = sr.AudioData(
            audio_bytes,
            SAMPLE_RATE,
            2
        )

        try:
            text = recognizer.recognize_google(
                audio_data,
                language="en-IN"
            )

            print("YOU:", text)

            update_status("● Command received", "#00ff88")

            update_command(text)

            handle_command(text.lower())

        except sr.UnknownValueError:
            update_status("● Could not understand", "#ff5555")
            speak("Sorry, I could not understand that.")

        except sr.RequestError:
            update_status("● Speech service unavailable", "#ff5555")
            speak("Speech recognition service is unavailable.")

    except Exception as e:
        print("Microphone Error:", e)

        update_status("● Microphone error", "#ff5555")

        speak("There is a problem with the microphone.")


def start_listening():
    """Start listening without freezing GUI."""

    threading.Thread(
        target=listen,
        daemon=True
    ).start()


# =========================
# COMMAND SYSTEM
# =========================

def handle_command(command):

    command = command.strip()

    print("COMMAND:", command)

    # -------------------------
    # YOUTUBE
    # -------------------------

    if "open youtube" in command or "youtube" == command:
        speak("Opening YouTube.")
        webbrowser.open("https://www.youtube.com")


    # -------------------------
    # GOOGLE
    # -------------------------

    elif "open google" in command or "google" == command:
        speak("Opening Google.")
        webbrowser.open("https://www.google.com")


    # -------------------------
    # GITHUB
    # -------------------------

    elif "open github" in command or "github" == command:
        speak("Opening GitHub.")
        webbrowser.open("https://github.com")


    # -------------------------
    # CHATGPT
    # -------------------------

    elif "open chatgpt" in command or "chatgpt" in command:
        speak("Opening ChatGPT.")
        webbrowser.open("https://chatgpt.com")


    # -------------------------
    # VS CODE
    # -------------------------

    elif "open vs code" in command or "open vscode" in command:
        speak("Opening Visual Studio Code.")

        try:
            subprocess.Popen("code", shell=True)
        except Exception as e:
            print("VS Code Error:", e)


    # -------------------------
    # NOTEPAD
    # -------------------------

    elif "open notepad" in command or "notepad" in command:
        speak("Opening Notepad.")
        subprocess.Popen("notepad.exe")


    # -------------------------
    # CREATE FOLDER
    # -------------------------

    elif "create folder" in command:

        folder_name = "Jarvis Folder"
        folder_path = os.path.join(
            os.path.expanduser("~"),
            "Desktop",
            folder_name
        )

        try:
            os.makedirs(folder_path, exist_ok=True)

            speak(
                "I created a folder named Jarvis Folder on your desktop."
            )

        except Exception as e:
            print("Folder Error:", e)
            speak("I could not create the folder.")


    # -------------------------
    # CURRENT TIME
    # -------------------------

    elif "time" in command:

        current_time = datetime.now().strftime("%I:%M %p")

        speak(
            f"The current time is {current_time}."
        )


    # -------------------------
    # CURRENT DATE
    # -------------------------

    elif "date" in command:

        current_date = datetime.now().strftime(
            "%d %B %Y"
        )

        speak(
            f"Today is {current_date}."
        )


    # -------------------------
    # STATUS
    # -------------------------

    elif "status" in command:

        speak(
            "All systems are running normally."
        )


    # -------------------------
    # SEARCH GOOGLE
    # -------------------------

    elif command.startswith("search"):

        search_text = command.replace(
            "search",
            "",
            1
        ).strip()

        if search_text:

            speak(
                f"Searching Google for {search_text}."
            )

            url = (
                "https://www.google.com/search?q="
                + search_text.replace(" ", "+")
            )

            webbrowser.open(url)

        else:
            speak("What should I search for?")


    # -------------------------
    # EXIT
    # -------------------------

    elif (
        "exit jarvis" in command
        or "close jarvis" in command
        or "shutdown jarvis" in command
    ):

        speak("Goodbye.")

        post_ui(root.after, 1500, root.destroy)


    # -------------------------
    # GREETINGS
    # -------------------------

    elif "hello" in command or "hi jarvis" in command:

        speak(
            "Hello. I am JARVIS. How can I help you?"
        )


    # -------------------------
    # UNKNOWN COMMAND
    # -------------------------

    else:

        speak(
            "I heard you, but I don't have that command yet."
        )

    update_status("● System Ready", "#00ff88")


# =========================
# GUI
# =========================

root = tk.Tk()

root.title(APP_TITLE)

root.geometry(
    f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
)

root.configure(
    bg="#05070b"
)

root.resizable(False, False)


# =========================
# CANVAS
# =========================

canvas = tk.Canvas(
    root,
    width=WINDOW_WIDTH,
    height=WINDOW_HEIGHT,
    bg="#05070b",
    highlightthickness=0
)

canvas.pack()


# =========================
# TITLE
# =========================

canvas.create_text(
    WINDOW_WIDTH // 2,
    45,
    text="J A R V I S",
    fill="#00eaff",
    font=("Segoe UI", 26, "bold")
)

canvas.create_text(
    WINDOW_WIDTH // 2,
    78,
    text="PERSONAL AI ASSISTANT",
    fill="#68727f",
    font=("Segoe UI", 9)
)


# =========================
# STATUS
# =========================

status_label = tk.Label(
    root,
    text="● System Ready",
    bg="#05070b",
    fg="#00ff88",
    font=("Segoe UI", 11, "bold")
)

status_label.place(
    x=20,
    y=570
)


# =========================
# COMMAND DISPLAY
# =========================

command_label = tk.Label(
    root,
    text="Say:  Jarvis, open YouTube",
    bg="#05070b",
    fg="#aab4c0",
    font=("Segoe UI", 11)
)

command_label.place(
    x=WINDOW_WIDTH // 2,
    y=565,
    anchor="center"
)


# =========================
# MIC BUTTON
# =========================

mic_button = tk.Button(
    root,
    text="🎙  LISTEN",
    command=start_listening,
    bg="#0b141c",
    fg="#00eaff",
    activebackground="#10232d",
    activeforeground="#ffffff",
    font=("Segoe UI", 11, "bold"),
    relief="flat",
    bd=0,
    padx=22,
    pady=10,
    cursor="hand2"
)

mic_button.place(
    x=WINDOW_WIDTH // 2,
    y=605,
    anchor="center"
)


# =========================
# JARVIS CORE
# =========================

center_x = WINDOW_WIDTH // 2
center_y = 325

angle = 0
pulse = 0
fps_counter = 0
last_fps_time = time.time()


# =========================
# FPS DISPLAY
# =========================

fps_label = tk.Label(
    root,
    text="FPS: 0",
    bg="#05070b",
    fg="#53606c",
    font=("Consolas", 9)
)

fps_label.place(
    x=820,
    y=20
)


# =========================
# ANIMATION
# =========================

def animate():

    global angle
    global pulse
    global fps_counter
    global last_fps_time

    process_ui_queue()
    canvas.delete("core")

    angle += 1.5
    pulse += 0.08

    # -------------------------
    # Outer ring
    # -------------------------

    canvas.create_oval(
        center_x - 150,
        center_y - 150,
        center_x + 150,
        center_y + 150,
        outline="#083c48",
        width=2,
        tags="core"
    )

    # -------------------------
    # Second ring
    # -------------------------

    canvas.create_oval(
        center_x - 125,
        center_y - 125,
        center_x + 125,
        center_y + 125,
        outline="#075968",
        width=2,
        tags="core"
    )

    # -------------------------
    # Rotating dots
    # -------------------------

    for i in range(12):

        a = math.radians(
            angle + i * 30
        )

        radius = 135

        x = center_x + math.cos(a) * radius
        y = center_y + math.sin(a) * radius

        canvas.create_oval(
            x - 4,
            y - 4,
            x + 4,
            y + 4,
            fill="#00eaff",
            outline="",
            tags="core"
        )

    # -------------------------
    # Inner rotating ring
    # -------------------------

    for i in range(6):

        a = math.radians(
            -angle * 1.7 + i * 60
        )

        radius = 95

        x = center_x + math.cos(a) * radius
        y = center_y + math.sin(a) * radius

        canvas.create_oval(
            x - 5,
            y - 5,
            x + 5,
            y + 5,
            fill="#00aaff",
            outline="",
            tags="core"
        )

    # -------------------------
    # Pulsing core
    # -------------------------

    pulse_size = 45 + math.sin(pulse) * 8

    canvas.create_oval(
        center_x - pulse_size,
        center_y - pulse_size,
        center_x + pulse_size,
        center_y + pulse_size,
        outline="#00eaff",
        width=3,
        tags="core"
    )

    inner_size = 27 + math.sin(
        pulse * 1.4
    ) * 5

    canvas.create_oval(
        center_x - inner_size,
        center_y - inner_size,
        center_x + inner_size,
        center_y + inner_size,
        fill="#06232c",
        outline="#00eaff",
        width=2,
        tags="core"
    )

    # -------------------------
    # JARVIS text
    # -------------------------

    canvas.create_text(
        center_x,
        center_y,
        text="J",
        fill="#ffffff",
        font=("Segoe UI", 30, "bold"),
        tags="core"
    )

    # -------------------------
    # FPS
    # -------------------------

    fps_counter += 1

    current_time = time.time()

    if current_time - last_fps_time >= 1:

        fps_label.config(
            text=f"FPS: {fps_counter}"
        )

        fps_counter = 0
        last_fps_time = current_time

    root.after(
        16,
        animate
    )


# =========================
# KEYBOARD SHORTCUT
# =========================

def keyboard_listen(event):

    start_listening()


root.bind(
    "<space>",
    keyboard_listen
)


# =========================
# START
# =========================

animate()

root.after(
    1000,
    lambda: speak(
        "JARVIS systems online. How can I help you?"
    )
)

root.mainloop()