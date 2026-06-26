#!/usr/bin/env python3
"""
JIMMY & SAMMY — Dual-persona voice assistant for Windows.

Wake words: "Hey Jimmy" (male voice) | "Hey Sammy" (female voice)
STT: faster-whisper (offline, GPU-accelerated)
TTS: pyttsx3 (offline, free)
AI:  Google Antigravity SDK (Gemini 2.5 Flash)

Usage:
    pip install -r requirements.txt
    python jimmy.py
"""

from __future__ import annotations

import logging
import os
import re
import subprocess
import sys
import threading
import time
import urllib.parse

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

from pathlib import Path
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
import numpy as np
import sounddevice as sd
import pyttsx3
from faster_whisper import WhisperModel


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

WAKE_WORDS = {"hey jimmy": "david", "hey sammy": "zira"}
ACTIVE_VOICE = "david"

WELCOME_PHRASE = "Welcome back, Yash. Good to see you. I am ready when you are."

BRAVE_EXE = r"C:\Users\vasir\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"
SPOTIFY_EXE = r"C:\Users\vasir\AppData\Local\Microsoft\WindowsApps\Spotify.exe"
ANTIGRAVITY_EXE = r"C:\Users\vasir\AppData\Local\Programs\antigravity\Antigravity.exe"

WHISPER_MODEL_SIZE = "base"
WHISPER_DEVICE = "cuda"
WHISPER_COMPUTE = "int8"

LISTEN_DURATION_S = 7.0
SAMPLE_RATE = 16000
CHANNELS = 1
COMMAND_LISTEN_TIMEOUT_S = 60.0


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

load_dotenv(Path(__file__).resolve().parent / ".env")

_LOG_FILE = Path(__file__).resolve().parent / "jimmy.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(_LOG_FILE, maxBytes=5_000_000, backupCount=1, encoding="utf-8"),
    ],
)
log = logging.getLogger("jimmy")


# ---------------------------------------------------------------------------
# Text-to-Speech
# ---------------------------------------------------------------------------

_tts_lock = threading.Lock()


def _make_engine() -> pyttsx3.Engine:
    """Create a fresh pyttsx3 engine configured with the active voice."""
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)
    engine.setProperty("volume", 1.0)

    voices = engine.getProperty("voices")
    for voice in voices:
        if ACTIVE_VOICE in voice.name.lower():
            engine.setProperty("voice", voice.id)
            break
    return engine


def speak(text: str) -> None:
    """Speak text aloud (blocking, thread-safe)."""
    log.info("Speaking: %r", text)
    with _tts_lock:
        try:
            if sys.platform == "win32":
                import pythoncom
                pythoncom.CoInitialize()
            engine = _make_engine()
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            log.error("TTS error: %s", e)


# ---------------------------------------------------------------------------
# System Helpers
# ---------------------------------------------------------------------------

def take_screenshot() -> None:
    """Capture the screen and save to the screenshots folder."""
    try:
        from PIL import ImageGrab
        import datetime
        screens_dir = Path(__file__).resolve().parent / "screenshots"
        screens_dir.mkdir(exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = screens_dir / f"screenshot_{timestamp}.png"
        ImageGrab.grab().save(filepath)
        log.info("Screenshot saved to %s", filepath)
    except Exception as e:
        log.error("Screenshot error: %s", e)


def execute_power_command(action: str) -> None:
    """Shutdown or restart the PC with a 10-second delay."""
    if sys.platform != "win32":
        return
    if action == "shutdown":
        os.system("shutdown /s /t 10")
        log.info("Initiated PC shutdown (10s delay).")
    elif action == "restart":
        os.system("shutdown /r /t 10")
        log.info("Initiated PC restart (10s delay).")


def close_app(app_name: str) -> None:
    """Force-kill a Windows process by name."""
    if sys.platform != "win32":
        return
    try:
        os.system(f"taskkill /IM {app_name} /F")
        log.info("Closed %s", app_name)
    except Exception as e:
        log.error("Could not close %s: %s", app_name, e)


def is_process_running(process_name: str) -> bool:
    """Check if a process is currently running."""
    try:
        output = os.popen("tasklist").read().lower()
        return process_name.lower() in output
    except Exception as e:
        log.warning("is_process_running error: %s", e)
        return False


# ---------------------------------------------------------------------------
# Volume Control (pycaw)
# ---------------------------------------------------------------------------

def _get_volume_interface():
    """Return the Windows IAudioEndpointVolume COM interface."""
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))


def set_volume(level: int) -> None:
    """Set system volume to a percentage (0-100)."""
    try:
        volume = _get_volume_interface()
        if level > 0:
            volume.SetMute(0, None)
        scalar = max(0, min(100, level)) / 100.0
        volume.SetMasterVolumeLevelScalar(scalar, None)
        log.info("Volume set to %d%%", level)
    except Exception as e:
        log.error("Volume control error: %s", e)


def change_volume(delta: int) -> None:
    """Increase or decrease system volume by a percentage."""
    try:
        volume = _get_volume_interface()
        current = volume.GetMasterVolumeLevelScalar()
        new_vol = max(0.0, min(1.0, current + (delta / 100.0)))
        volume.SetMasterVolumeLevelScalar(new_vol, None)
        log.info("Volume changed by %d%%", delta)
    except Exception as e:
        log.error("Volume control error: %s", e)


def mute_volume(mute: bool = True) -> None:
    """Mute or unmute system audio."""
    try:
        volume = _get_volume_interface()
        volume.SetMute(1 if mute else 0, None)
        log.info("Audio %s", "muted" if mute else "unmuted")
    except Exception as e:
        log.error("Mute control error: %s", e)


# ---------------------------------------------------------------------------
# Timers & Reminders
# ---------------------------------------------------------------------------

def set_timer(minutes: float, message: str) -> None:
    """Start a background timer that speaks a reminder when done."""
    def _timer():
        log.info("Timer started for %g minutes: %s", minutes, message)
        time.sleep(minutes * 60)
        log.info("Timer done: %s", message)
        speak(f"Reminder: {message}")

    threading.Thread(target=_timer, daemon=True).start()


# ---------------------------------------------------------------------------
# App Launchers
# ---------------------------------------------------------------------------

def open_spotify_minimized() -> None:
    """Open Spotify in a minimized window."""
    if not os.path.isfile(SPOTIFY_EXE):
        log.warning("Spotify not found at %s", SPOTIFY_EXE)
        return
    try:
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.shell32.ShellExecuteW(None, "open", SPOTIFY_EXE, None, None, 7)
        else:
            subprocess.Popen([SPOTIFY_EXE])
        log.info("Opened Spotify (minimized).")
    except Exception as e:
        log.warning("Could not open Spotify: %s", e)


def open_brave(force_new: bool = False) -> None:
    """Open Brave browser. Skips if already running unless force_new is True."""
    if not os.path.isfile(BRAVE_EXE):
        log.warning("Brave not found at %s", BRAVE_EXE)
        return
    if not force_new and is_process_running("brave.exe"):
        log.info("Brave is already running. Skipping launch.")
        return
    try:
        os.startfile(BRAVE_EXE)
        log.info("Opened Brave browser.")
    except Exception as e:
        log.warning("Could not open Brave: %s", e)


def search_web(query: str) -> None:
    """Open a Brave Search tab for the given query."""
    if not os.path.isfile(BRAVE_EXE):
        log.warning("Brave not found.")
        return
    url = f"https://search.brave.com/search?q={urllib.parse.quote(query)}"
    try:
        subprocess.Popen([BRAVE_EXE, url])
        log.info("Searching web for: %r", query)
    except Exception as e:
        log.warning("Could not search web: %s", e)


def play_spotify_song(song_name: str) -> None:
    """Search for a song on Spotify."""
    try:
        uri = f"spotify:search:{urllib.parse.quote(song_name)}"
        os.startfile(uri)
        log.info("Opened Spotify search for: %r", song_name)
    except Exception as e:
        log.warning("Could not search Spotify: %s", e)


def open_antigravity() -> None:
    """Open Google Antigravity IDE."""
    if not os.path.isfile(ANTIGRAVITY_EXE):
        log.warning("Antigravity IDE not found at %s", ANTIGRAVITY_EXE)
        return
    try:
        os.startfile(ANTIGRAVITY_EXE)
        log.info("Opened Antigravity IDE.")
    except Exception as e:
        log.warning("Could not open Antigravity: %s", e)


# ---------------------------------------------------------------------------
# Speech Recognition (faster-whisper)
# ---------------------------------------------------------------------------

def load_whisper() -> WhisperModel:
    """Load the Whisper model, falling back to CPU if CUDA fails."""
    log.info("Loading Whisper model (%s) on %s...", WHISPER_MODEL_SIZE, WHISPER_DEVICE)
    try:
        model = WhisperModel(WHISPER_MODEL_SIZE, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE)
        log.info("Whisper loaded.")
        return model
    except Exception:
        log.warning("CUDA failed, falling back to CPU.")
        return WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")


def record_audio(duration_s: float) -> np.ndarray:
    """Record audio from the microphone and return as a float32 numpy array."""
    samples = int(SAMPLE_RATE * duration_s)
    audio = sd.rec(samples, samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32")
    sd.wait()
    return audio.flatten()


def transcribe(model: WhisperModel, audio: np.ndarray) -> str:
    """Transcribe an audio array to lowercase text."""
    try:
        segments, _ = model.transcribe(
            audio, language="en", beam_size=1,
            vad_filter=True, vad_parameters={"min_silence_duration_ms": 300},
        )
        return " ".join(seg.text for seg in segments).strip().lower()
    except Exception as e:
        log.error("Transcription failed: %s", e)
        return ""


# ---------------------------------------------------------------------------
# Wake Word Detection
# ---------------------------------------------------------------------------

def is_wake_word(text: str) -> str:
    """Return the matched wake word from text, or empty string if none found."""
    for wake in WAKE_WORDS:
        if wake in text or all(w in text for w in wake.split() if len(w) > 2):
            return wake
    return ""


def extract_wake_command(text: str, wake_word: str) -> str:
    """Extract any inline command spoken after the wake word."""
    if not wake_word:
        return ""
    idx = text.find(wake_word)
    if idx != -1:
        return text[idx + len(wake_word):].strip()
    return ""


# ---------------------------------------------------------------------------
# Command Handling
# ---------------------------------------------------------------------------

def handle_command(text: str, model: WhisperModel = None) -> bool:
    """Process a voice command. Returns True if a command was matched."""
    text = text.strip().lower()
    if not text:
        return False

    # Open Antigravity IDE (fuzzy match — Whisper often mishears this word)
    _antigravity_patterns = (
        "antigravity", "anti gravity", "entire gravity",
        "i gravity", "i grab it", "grab it", "anti-gravity",
    )
    if any(p in text for p in _antigravity_patterns):
        open_antigravity()
        speak("Opening Antigravity.")
        return True

    # Open Brave browser
    if any(w in text for w in ("brave", "browser")) and any(w in text for w in ("open", "launch", "start")):
        open_brave(force_new=True)
        speak("Opening Brave.")
        return True

    # Open Spotify
    if "spotify" in text and any(w in text for w in ("open", "launch", "start")):
        open_spotify_minimized()
        speak("Opening Spotify.")
        return True

    # Web search
    search_prefixes = ("search for ", "search ", "what is ", "whats ", "what's ", "who is ", "who's ")
    for prefix in search_prefixes:
        if text.startswith(prefix):
            query = text[len(prefix):].strip()
            if query:
                search_web(query)
                speak(f"Searching for {query}.")
                return True

    # Build / Ship — spawn an Antigravity AI agent
    if text.startswith("build ") or text.startswith("ship ") or "build a " in text:
        if not model:
            log.warning("Cannot start Antigravity agent without Whisper model reference.")
            return False

        import antigravity_bridge

        feature_req = text
        generic_triggers = (
            "build a project", "build a feature", "ship a feature",
            "build a new feature.", "build a new feature", "build a",
        )
        if text in generic_triggers:
            speak("What do you want to build?")
            audio_feat = record_audio(8.0)
            feature_req = transcribe(model, audio_feat)
            if not feature_req:
                speak("I didn't catch that. Canceling.")
                return True

        model_id = "gemini-2.5-flash"

        speak("What should we name the project folder?")
        audio_proj = record_audio(4.0)
        proj_name = transcribe(model, audio_proj).replace(" ", "_")
        if not proj_name:
            proj_name = "new_project"

        workspace_dir = str(Path(__file__).resolve().parent / "projects" / proj_name)
        Path(workspace_dir).mkdir(parents=True, exist_ok=True)

        speak(f"Spawning {model_id} in {proj_name}. Check your Antigravity IDE.")

        def on_complete():
            speak("Antigravity agent has finished execution.")

        antigravity_bridge.spawn_agent_background(feature_req, model_id, workspace_dir, on_complete)
        return True

    # Play a song on Spotify
    if text.startswith("play "):
        song = text[5:].strip()
        if song:
            play_spotify_song(song)
            speak(f"Playing {song}.")
            return True

    # Screenshot
    if text in ("take a screenshot", "take screenshot", "capture screen"):
        take_screenshot()
        speak("Screenshot saved.")
        return True

    # Power commands
    if "shut down the laptop" in text or "shutdown the laptop" in text:
        speak("Shutting down the laptop in 10 seconds.")
        execute_power_command("shutdown")
        return True
    if "restart the laptop" in text or "restart laptop" in text:
        speak("Restarting the laptop in 10 seconds.")
        execute_power_command("restart")
        return True

    # Close apps
    if "close brave" in text or "close browser" in text:
        close_app("brave.exe")
        speak("Closed Brave.")
        return True
    if any(p in text for p in ("close spotify", "close, spotify", "stop spotify", "stop, spotify")):
        close_app("Spotify.exe")
        speak("Closed Spotify.")
        return True

    # Volume controls
    if text in ("mute audio", "mute", "mute volume"):
        mute_volume(True)
        speak("Audio muted.")
        return True
    if text in ("unmute audio", "unmute", "unmute volume"):
        mute_volume(False)
        speak("Audio unmuted.")
        return True
    if text in ("volume up", "increase volume"):
        change_volume(10)
        speak("Volume up.")
        return True
    if text in ("volume down", "decrease volume"):
        change_volume(-10)
        speak("Volume down.")
        return True

    vol_match = re.search(r"set volume to (\d+)", text)
    if vol_match:
        vol = int(vol_match.group(1))
        set_volume(vol)
        speak(f"Volume set to {vol} percent.")
        return True

    # Timers & Reminders
    remind_match = re.search(r"remind me to (.*?) in (\d+(?:\.\d+)?) minute", text)
    if remind_match:
        task = remind_match.group(1).strip()
        mins = float(remind_match.group(2))
        set_timer(mins, task)
        speak(f"I will remind you to {task} in {mins:g} minutes.")
        return True

    timer_match = re.search(r"set a timer for (\d+(?:\.\d+)?) minute", text)
    if timer_match:
        mins = float(timer_match.group(1))
        set_timer(mins, "Time is up.")
        speak(f"Timer set for {mins:g} minutes.")
        return True

    return False


# ---------------------------------------------------------------------------
# Wake Session
# ---------------------------------------------------------------------------

def on_wake(model: WhisperModel, inline_command: str = "") -> None:
    """Handles everything after a wake word is detected."""
    log.info("=== WAKE WORD DETECTED ===")

    open_brave()
    log.info("Wake actions launched.")

    speak(WELCOME_PHRASE)

    if inline_command:
        log.info("Inline command detected: %r", inline_command)
        handle_command(inline_command, model)

    log.info("Listening for commands for %.0fs...", COMMAND_LISTEN_TIMEOUT_S)
    deadline = time.time() + COMMAND_LISTEN_TIMEOUT_S

    while time.time() < deadline:
        try:
            audio = record_audio(LISTEN_DURATION_S)

            rms = float(np.sqrt(np.mean(audio ** 2)))
            if rms < 0.005:
                continue

            text = transcribe(model, audio)
            if not text:
                continue

            log.info("Command heard: %r", text)

            wake_match = is_wake_word(text)
            if wake_match:
                global ACTIVE_VOICE
                ACTIVE_VOICE = WAKE_WORDS[wake_match]
                speak("I'm here. What do you need?")
                cmd = extract_wake_command(text, wake_match)
                if cmd:
                    handle_command(cmd, model)
                deadline = time.time() + COMMAND_LISTEN_TIMEOUT_S
                continue

            if handle_command(text, model):
                deadline = time.time() + COMMAND_LISTEN_TIMEOUT_S

            dismiss_phrases = ("thank you", "thanks", "that's all", "goodbye", "go to sleep", "stop")
            if any(phrase in text for phrase in dismiss_phrases):
                speak("Alright, going back to sleep. Call me when you need me.")
                log.info("Command session ended by user.")
                return

        except Exception as e:
            log.error("Error during command listening: %s", e)
            time.sleep(0.5)

    log.info("Command session timed out, returning to wake-word listening.")


# ---------------------------------------------------------------------------
# Main Loop
# ---------------------------------------------------------------------------

def main() -> int:
    if sys.platform == "win32":
        import ctypes
        mutex_name = "JimmyVoiceAssistant_SingletonMutex"
        mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
        if ctypes.windll.kernel32.GetLastError() == 183:
            log.error("Assistant is already running! Exiting.")
            return 1

    log.info("Starting assistant...")
    log.info("Wake words: %r", list(WAKE_WORDS.keys()))
    log.info("TTS engine: pyttsx3 (offline, free)")

    model = load_whisper()

    log.info("Listening... Say one of %r to activate.", list(WAKE_WORDS.keys()))
    log.info("Assistant online. Waiting for wake word...")

    while True:
        try:
            audio = record_audio(LISTEN_DURATION_S)

            rms = float(np.sqrt(np.mean(audio ** 2)))
            if rms < 0.005:
                continue

            text = transcribe(model, audio)
            if text:
                log.info("Heard: %r", text)

            wake_match = is_wake_word(text)
            if wake_match:
                global ACTIVE_VOICE
                ACTIVE_VOICE = WAKE_WORDS[wake_match]
                inline_cmd = extract_wake_command(text, wake_match)
                on_wake(model, inline_command=inline_cmd)
                time.sleep(2.0)

        except KeyboardInterrupt:
            log.info("Assistant stopped. Goodbye.")
            speak("Goodbye.")
            return 0
        except Exception as e:
            log.error("Error in main loop: %s", e)
            time.sleep(0.5)

    return 0


if __name__ == "__main__":
    sys.exit(main())
