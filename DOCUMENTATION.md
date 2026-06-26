# Jimmy & Sammy — Developer Documentation

**A complete guide to understanding, setting up, and extending the dual-persona voice assistant.**

Version: 1.0 | Last Updated: June 26, 2026 | Author: Yashwanth | GitHub: github.com/yashwanth-23

---

## Table of Contents

1. [What Is This Project?](#1-what-is-this-project)
2. [Architecture Overview](#2-architecture-overview)
3. [Prerequisites & System Requirements](#3-prerequisites--system-requirements)
4. [Step-by-Step Setup Guide](#4-step-by-step-setup-guide)
5. [Project Structure](#5-project-structure)
6. [How the Code Works — Module by Module](#6-how-the-code-works--module-by-module)
7. [Voice Command Reference](#7-voice-command-reference)
8. [AI Code Generation (Antigravity SDK)](#8-ai-code-generation-antigravity-sdk)
9. [Configuration Reference](#9-configuration-reference)
10. [Adding Your Own Commands](#10-adding-your-own-commands)
11. [Adding a New Persona](#11-adding-a-new-persona)
12. [Running on Windows Startup](#12-running-on-windows-startup)
13. [Troubleshooting](#13-troubleshooting)
14. [FAQ](#14-faq)

---

## 1. What Is This Project?

Jimmy & Sammy is a voice-activated personal assistant that runs entirely on your Windows PC. It listens for a wake word ("Hey Jimmy" or "Hey Sammy"), then processes voice commands to control your computer — open apps, play music, search the web, control volume, set timers, and even build entire software projects using AI.

**Key design decisions:**

- **100% offline voice processing.** Speech recognition (faster-whisper) and text-to-speech (pyttsx3) run locally. Your voice never leaves your machine.
- **Dual personas.** Two wake words activate two different Windows voices (David = male, Zira = female). Both share the same command set.
- **AI code generation.** When you say "build a python script that does X", the assistant spawns a Google Antigravity SDK agent that autonomously writes code into a project folder. This is the only feature that requires internet.
- **Single-file simplicity.** The core logic lives in one file (`jimmy.py`). No frameworks, no complex architecture. Easy to read, easy to modify.

---

## 2. Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                        MAIN LOOP                             │
│                       (jimmy.py)                             │
│                                                              │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────┐   │
│  │  Microphone  │───▶│ faster-whisper│───▶│ Wake Word Check│   │
│  │ (sounddevice)│    │   (Whisper)   │    │                │   │
│  └─────────────┘    └──────────────┘    └───────┬────────┘   │
│                                                  │            │
│                                          ┌───────▼────────┐   │
│                                          │   on_wake()     │   │
│                                          │ • Open Brave    │   │
│                                          │ • Greet user    │   │
│                                          │ • Listen 60s    │   │
│                                          └───────┬────────┘   │
│                                                  │            │
│                                          ┌───────▼────────┐   │
│                                          │handle_command() │   │
│                                          │ Pattern matching│   │
│                                          └───────┬────────┘   │
│                                                  │            │
│         ┌────────────┬──────────┬────────────┬───┘            │
│         ▼            ▼          ▼            ▼                │
│   ┌──────────┐ ┌──────────┐ ┌────────┐ ┌──────────────┐      │
│   │ App      │ │ Volume   │ │ Timers │ │ Antigravity  │      │
│   │ Control  │ │ Control  │ │        │ │ Bridge       │      │
│   │ (os)     │ │ (pycaw)  │ │(thread)│ │ (SDK agent)  │      │
│   └──────────┘ └──────────┘ └────────┘ └──────────────┘      │
│                                                              │
│  ┌─────────────┐                                             │
│  │   pyttsx3    │◀── speak() called from anywhere            │
│  │  (TTS out)   │                                            │
│  └─────────────┘                                             │
└──────────────────────────────────────────────────────────────┘
```

**Data flow:**

1. The microphone continuously captures 7-second audio chunks.
2. Each chunk is passed to faster-whisper for local transcription.
3. The transcribed text is checked against the wake words ("hey jimmy", "hey sammy").
4. If a wake word is detected, Brave browser opens and a welcome greeting plays.
5. For the next 60 seconds, every audio chunk is transcribed and matched against command patterns.
6. When a command matches, the corresponding function executes (open app, play song, etc.).
7. The session ends when the user says "thank you" / "goodbye" or the 60-second window expires.

---

## 3. Prerequisites & System Requirements

### Hardware

| Component | Minimum | Recommended |
| :--- | :--- | :--- |
| OS | Windows 10 | Windows 11 |
| Python | 3.10+ | 3.12+ |
| RAM | 4 GB | 8 GB+ |
| Microphone | Any USB/built-in mic | Decent quality mic for accuracy |
| GPU | Not required | NVIDIA GPU with CUDA (for faster transcription) |

### Software

| Software | Required? | Purpose |
| :--- | :--- | :--- |
| Python 3.10+ | Yes | Runtime |
| pip | Yes | Package manager (comes with Python) |
| Brave Browser | No (but commands won't work without it) | Web browsing / search |
| Spotify Desktop | No (but music commands won't work without it) | Music playback |
| Antigravity IDE | No (but "open antigravity" won't work without it) | AI code editor |
| NVIDIA CUDA Toolkit | No (auto-falls back to CPU) | GPU-accelerated transcription |
| Google Gemini API Key | No (only needed for "build a project" AI feature) | AI code generation |

---

## 4. Step-by-Step Setup Guide

### Step 1: Clone the Repository

```bash
git clone https://github.com/yashwanth-23/jimmy-assistant.git
cd jimmy-assistant
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `faster-whisper` — Local speech-to-text (Whisper model)
- `pyttsx3` — Offline text-to-speech
- `sounddevice` — Microphone audio capture
- `numpy` — Audio processing
- `python-dotenv` — Environment variable loading
- `pycaw` — Windows volume control
- `comtypes` — Windows COM interface (needed by pycaw)
- `Pillow` — Screenshot capture
- `google-antigravity` — AI code generation SDK

### Step 3: Configure App Paths

Open `jimmy.py` and update these paths to match YOUR system:

```python
BRAVE_EXE = r"C:\Users\YOUR_USERNAME\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"
SPOTIFY_EXE = r"C:\Users\YOUR_USERNAME\AppData\Local\Microsoft\WindowsApps\Spotify.exe"
ANTIGRAVITY_EXE = r"C:\Users\YOUR_USERNAME\AppData\Local\Programs\antigravity\Antigravity.exe"
```

To find the correct paths on your machine, run this in PowerShell:

```powershell
# Find Brave
Get-ChildItem $env:LOCALAPPDATA -Recurse -Filter 'brave.exe' -ErrorAction SilentlyContinue | Select -First 1 -ExpandProperty FullName

# Find Spotify
Get-ChildItem $env:LOCALAPPDATA -Recurse -Filter 'Spotify.exe' -ErrorAction SilentlyContinue | Select -First 1 -ExpandProperty FullName
```

If you don't use Brave or Spotify, that's fine — those commands simply won't do anything. The assistant won't crash.

### Step 4: Set Up AI Code Generation (Optional)

If you want the "build a project" feature, you need a free Google Gemini API key:

1. Go to https://aistudio.google.com/
2. Create a new project. **Do NOT attach a billing account** (to keep the free tier active).
3. Generate an API key.
4. Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_key_here
```

### Step 5: Personalize the Welcome Message

In `jimmy.py`, change this line to your name:

```python
WELCOME_PHRASE = "Welcome back, Yash. Good to see you. I am ready when you are."
```

### Step 6: Run It

```bash
python jimmy.py
```

You should see:

```
12:00:00 INFO Starting assistant...
12:00:00 INFO Wake words: ['hey jimmy', 'hey sammy']
12:00:00 INFO TTS engine: pyttsx3 (offline, free)
12:00:01 INFO Loading Whisper model (base) on cuda...
12:00:02 INFO Whisper loaded.
12:00:02 INFO Listening... Say one of ['hey jimmy', 'hey sammy'] to activate.
12:00:02 INFO Assistant online. Waiting for wake word...
```

Now say **"Hey Jimmy"** and the assistant will respond!

---

## 5. Project Structure

```
jimmy-assistant/
│
├── jimmy.py               # Core assistant logic (single file)
│                           #   - Configuration constants
│                           #   - TTS engine (speak function)
│                           #   - System helpers (screenshot, power, close app)
│                           #   - Volume control (pycaw)
│                           #   - Timers & reminders
│                           #   - App launchers (Spotify, Brave, Antigravity)
│                           #   - Speech recognition (faster-whisper)
│                           #   - Wake word detection
│                           #   - Command handler (pattern matching)
│                           #   - Wake session manager
│                           #   - Main loop
│
├── antigravity_bridge.py   # Spawns an Antigravity SDK agent in a background thread
│                           #   - Connects to the Gemini API via the SDK
│                           #   - Sends the user's voice prompt to the AI
│                           #   - Streams the response and logs it
│
├── requirements.txt        # Python package dependencies
├── .env                    # API keys (not committed to git)
├── jimmy.log               # Auto-generated log file (rotates at 5 MB)
├── start_jimmy.vbs         # VBScript to launch Jimmy minimized (for startup)
├── create_startup.ps1      # PowerShell script to add Jimmy to Windows startup
├── projects/               # AI-generated code goes here (one subfolder per project)
├── screenshots/            # Screenshots saved here
└── README.md               # Quick-start guide for GitHub
```

---

## 6. How the Code Works — Module by Module

### 6.1 Configuration (Lines 1–60)

The top of `jimmy.py` contains all configurable constants. No config files, no CLI flags — just edit the variables directly.

| Variable | What it controls |
| :--- | :--- |
| `WAKE_WORDS` | Dictionary mapping wake phrases to voice names |
| `ACTIVE_VOICE` | Currently active TTS voice ("david" or "zira") |
| `WELCOME_PHRASE` | What the assistant says when activated |
| `BRAVE_EXE` / `SPOTIFY_EXE` / `ANTIGRAVITY_EXE` | Full paths to app executables |
| `WHISPER_MODEL_SIZE` | Whisper model: "tiny", "base", "small", or "medium" |
| `WHISPER_DEVICE` | "cuda" for GPU or "cpu" |
| `LISTEN_DURATION_S` | How many seconds of audio per capture (default: 7) |
| `COMMAND_LISTEN_TIMEOUT_S` | How long the command session stays open (default: 60) |

### 6.2 Text-to-Speech Engine

```python
def speak(text: str) -> None:
```

This is the voice output function. It uses `pyttsx3` which wraps the Windows SAPI (Speech API) voices. Key details:

- **Thread-safe.** A `threading.Lock` prevents two threads from speaking simultaneously.
- **COM initialization.** On Windows, pyttsx3 uses COM objects. Background threads (like timers) need `pythoncom.CoInitialize()` before they can use COM. Without this, timer reminders would silently fail.
- **Fresh engine per call.** We create a new `pyttsx3.Engine` every time `speak()` is called. This avoids a known bug where reusing engines across threads causes crashes.
- **Voice selection.** The `_make_engine()` function reads the global `ACTIVE_VOICE` variable and selects the matching Windows voice.

### 6.3 System Helpers

| Function | What it does |
| :--- | :--- |
| `take_screenshot()` | Captures the screen using PIL/Pillow and saves to `screenshots/` |
| `execute_power_command(action)` | Runs `shutdown /s /t 10` or `shutdown /r /t 10` via `os.system()` |
| `close_app(app_name)` | Runs `taskkill /IM appname.exe /F` to force-kill a process |
| `is_process_running(process_name)` | Checks `tasklist` output to see if a process is running |

### 6.4 Volume Control

Uses the `pycaw` library to interact with Windows audio endpoints via COM.

The `_get_volume_interface()` helper returns the `IAudioEndpointVolume` interface, which is then used by:

- `set_volume(level)` — Absolute volume (0–100%)
- `change_volume(delta)` — Relative change (+10 or -10)
- `mute_volume(mute)` — Mute or unmute

### 6.5 Timers & Reminders

```python
def set_timer(minutes: float, message: str) -> None:
```

Spawns a daemon thread that sleeps for `N * 60` seconds, then calls `speak()` with the reminder message. Because it's a daemon thread, it dies automatically if the main process exits.

**Important:** Timers are stored in memory only. If you restart the assistant, all active timers are lost.

### 6.6 App Launchers

| Function | Details |
| :--- | :--- |
| `open_spotify_minimized()` | Uses `ShellExecuteW` with `SW_SHOWMINIMIZED (7)` to open Spotify without it taking focus |
| `open_brave(force_new)` | Uses `os.startfile()`. Skips if already running (unless `force_new=True`) |
| `search_web(query)` | Opens Brave with a `search.brave.com` URL |
| `play_spotify_song(song_name)` | Opens a `spotify:search:` URI which triggers Spotify's built-in search |
| `open_antigravity()` | Uses `os.startfile()` to launch the Antigravity IDE |

### 6.7 Speech Recognition

```python
def load_whisper() -> WhisperModel:
def record_audio(duration_s: float) -> np.ndarray:
def transcribe(model: WhisperModel, audio: np.ndarray) -> str:
```

- `load_whisper()` loads the faster-whisper model. Tries CUDA first, falls back to CPU.
- `record_audio()` captures `N` seconds of audio from the default microphone at 16kHz mono (what Whisper expects).
- `transcribe()` runs the Whisper model on the audio array with VAD (Voice Activity Detection) enabled. VAD filters out silence so the model only processes actual speech.

### 6.8 Wake Word Detection

```python
def is_wake_word(text: str) -> str:
def extract_wake_command(text: str, wake_word: str) -> str:
```

- `is_wake_word()` checks if the transcribed text contains any registered wake word. Returns the matched wake word string (e.g., `"hey jimmy"`) or an empty string.
- `extract_wake_command()` extracts anything spoken AFTER the wake word. For example, `"hey jimmy open brave"` → `"open brave"`. This enables single-pass commands.

**Fuzzy matching:** The wake word check uses `all(w in text for w in wake.split() if len(w) > 2)` which allows slight word order variations that Whisper might produce.

### 6.9 Command Handler

```python
def handle_command(text: str, model: WhisperModel = None) -> bool:
```

This is the brain. It receives the transcribed text and matches it against patterns using simple Python string operations (`in`, `startswith`, regex). No NLP, no intent classification — just straightforward pattern matching.

**Why not use an LLM for command parsing?** Speed and cost. Pattern matching takes microseconds. Sending audio to an LLM would add latency and require internet. For a fixed set of commands, simple matching is the right tool.

The function returns `True` if a command was matched (which resets the 60-second timeout) and `False` if nothing matched.

### 6.10 Wake Session

```python
def on_wake(model: WhisperModel, inline_command: str = "") -> None:
```

This function orchestrates everything that happens after a wake word is detected:

1. Opens Brave browser (if not already running).
2. Speaks the welcome phrase.
3. Handles any inline command (e.g., from "Hey Jimmy, open Spotify").
4. Enters a 60-second command loop.
5. Each recognized command resets the 60-second timer.
6. Saying a different wake word mid-session switches the active voice.
7. Dismiss phrases ("thank you", "goodbye") end the session early.

### 6.11 Main Loop

```python
def main() -> int:
```

- Creates a Windows mutex to prevent multiple instances from running simultaneously.
- Loads the Whisper model.
- Enters an infinite loop: record → transcribe → check for wake word → trigger `on_wake()`.
- Handles `KeyboardInterrupt` (Ctrl+C) gracefully.

---

## 7. Voice Command Reference

### Wake Words

| Say this | Voice |
| :--- | :--- |
| "Hey Jimmy" | Microsoft David (male) |
| "Hey Sammy" | Microsoft Zira (female) |

### Commands (say these AFTER the wake word)

**App Control:**
- "Open Spotify" / "Launch Spotify" / "Start Spotify"
- "Close Spotify" / "Stop Spotify"
- "Open Brave" / "Open browser" / "Launch Brave"
- "Close Brave" / "Close browser"
- "Open Antigravity" (also matches fuzzy variants like "anti gravity", "entire gravity")

**Music:**
- "Play [song name]" — e.g., "Play Shape of You"

**Web Search:**
- "Search for [query]" — e.g., "Search for python tutorials"
- "What is [query]" — e.g., "What is machine learning"
- "Who is [query]" — e.g., "Who is Elon Musk"

**Volume:**
- "Volume up" / "Increase volume" (+10%)
- "Volume down" / "Decrease volume" (-10%)
- "Set volume to [number]" — e.g., "Set volume to 50"
- "Mute" / "Mute audio"
- "Unmute" / "Unmute audio"

**Timers:**
- "Set a timer for [N] minutes"
- "Remind me to [task] in [N] minutes"

**Screenshots:**
- "Take a screenshot" / "Capture screen"

**Power:**
- "Shut down the laptop" (10-second delay)
- "Restart the laptop" (10-second delay)

**AI Code Generation:**
- "Build a [description]" — e.g., "Build a python script that prints fibonacci numbers"
- "Build a project" (asks what to build)
- "Ship a feature" (asks what to build)

**Session Control:**
- "Thank you" / "Thanks" / "Goodbye" / "Go to sleep" — ends command session
- Say the other wake word — switches persona mid-session

---

## 8. AI Code Generation (Antigravity SDK)

### How It Works

When you say "Build a python script that does X", the following happens:

1. Jimmy captures your full sentence as the feature request.
2. Jimmy asks "What should we name the project folder?" and records your answer.
3. A new folder is created at `projects/<folder_name>/`.
4. The `antigravity_bridge.py` module spawns a background thread.
5. Inside that thread, it connects to the Google Antigravity SDK via WebSocket.
6. It sends your feature request to a Gemini 2.5 Flash model.
7. The AI agent autonomously writes code files into the project folder.
8. When done, Jimmy announces "Antigravity agent has finished execution."

### The Bridge Module (antigravity_bridge.py)

```python
async def _async_spawn(feature_request, model_id, workspace_dir):
    config = LocalAgentConfig(
        model=model_id,
        workspaces=[workspace_dir],
        system_instructions="You are an expert autonomous developer. You MUST write all code inside {workspace_dir}. Complete the user's feature request.",
        capabilities=CapabilitiesConfig(),
    )
    async with Agent(config) as agent:
        response = await agent.chat(feature_request)
        async for token in response:
            full_response += token
```

Key details:
- `workspaces=[workspace_dir]` tells the SDK which directory the agent is allowed to operate in.
- `system_instructions` explicitly tells the AI to write files ONLY in the designated folder.
- The agent runs in a background thread so it doesn't block the voice assistant.
- The model used is `gemini-2.5-flash` (free tier, fast, smart).

### Free Tier Limits

The Gemini 2.5 Flash free tier gives you generous daily limits. If you hit a 429 error, you've exhausted your daily quota — just wait until the next day or create a new Google Cloud project without a billing account.

---

## 9. Configuration Reference

All configuration is at the top of `jimmy.py`. Here's every setting you can change:

```python
# Add or modify wake words and their associated voice
WAKE_WORDS = {"hey jimmy": "david", "hey sammy": "zira"}

# Default voice on startup
ACTIVE_VOICE = "david"

# What the assistant says when activated
WELCOME_PHRASE = "Welcome back, Yash. Good to see you. I am ready when you are."

# Executable paths (update to match YOUR system)
BRAVE_EXE = r"C:\...\brave.exe"
SPOTIFY_EXE = r"C:\...\Spotify.exe"
ANTIGRAVITY_EXE = r"C:\...\Antigravity.exe"

# Whisper speech recognition settings
WHISPER_MODEL_SIZE = "base"    # Options: tiny, base, small, medium
WHISPER_DEVICE = "cuda"        # Options: cuda, cpu
WHISPER_COMPUTE = "int8"       # Options: int8 (all hardware), float16 (CUDA only)

# Audio capture
LISTEN_DURATION_S = 7.0        # Seconds per audio capture chunk
SAMPLE_RATE = 16000            # Must be 16000 (Whisper requirement)
CHANNELS = 1                   # Mono audio

# Command session timeout
COMMAND_LISTEN_TIMEOUT_S = 60.0  # Seconds before returning to wake-word listening
```

---

## 10. Adding Your Own Commands

Adding a new voice command is straightforward. All command matching happens inside `handle_command()` in `jimmy.py`.

### Example: Add a "Lock the PC" Command

**Step 1:** Add a helper function (in the System Helpers section):

```python
def lock_pc() -> None:
    """Lock the Windows workstation."""
    if sys.platform != "win32":
        return
    import ctypes
    ctypes.windll.user32.LockWorkStation()
    log.info("PC locked.")
```

**Step 2:** Add the command match (inside `handle_command()`, before `return False`):

```python
    # Lock PC
    if "lock the pc" in text or "lock the computer" in text or "lock screen" in text:
        speak("Locking the PC.")
        lock_pc()
        return True
```

**That's it.** The pattern is always:
1. Write a function that does the thing.
2. Add an `if` block in `handle_command()` that matches the voice pattern and calls your function.
3. Return `True` so the command session timer resets.

### Tips for Voice Pattern Matching

- **Always match lowercase.** The text is already lowercased by `transcribe()`.
- **Use `in` for flexible matching.** `"lock" in text` matches "lock the pc", "please lock", "lock it", etc.
- **Use tuples for multiple triggers.** `if text in ("mute", "mute audio", "mute volume"):` for exact matches.
- **Use `any()` for fuzzy multi-word matching.** `if any(w in text for w in ("lock", "secure")):` for keyword detection.
- **Use regex for dynamic values.** `re.search(r"set brightness to (\d+)", text)` to extract numbers.
- **Add Whisper mishearing variants.** Whisper sometimes transcribes words incorrectly. Test your command and add common misheard variants.

---

## 11. Adding a New Persona

Want to add a third persona? Here's how.

**Step 1:** Check which voices are installed on the target machine:

```python
import pyttsx3
engine = pyttsx3.init()
for voice in engine.getProperty("voices"):
    print(voice.name)
```

Windows default installs are "Microsoft David" and "Microsoft Zira". Additional voices can be installed via **Settings → Time & Language → Speech → Manage voices**.

**Step 2:** Add the new wake word to the `WAKE_WORDS` dictionary:

```python
WAKE_WORDS = {
    "hey jimmy": "david",
    "hey sammy": "zira",
    "hey alex": "mark",      # New persona using Microsoft Mark voice
}
```

**Step 3:** The voice name (e.g., "mark") must be a substring of the Windows voice name (e.g., "Microsoft Mark Desktop"). The `_make_engine()` function matches using `if ACTIVE_VOICE in voice.name.lower()`.

That's it — the system handles everything else automatically.

---

## 12. Running on Windows Startup

The project includes two scripts for auto-starting Jimmy when Windows boots.

### start_jimmy.vbs

A VBScript wrapper that launches `jimmy.py` using `pythonw.exe` (the windowless Python interpreter). This prevents a console window from appearing on screen.

### create_startup.ps1

A PowerShell script that copies `start_jimmy.vbs` to your Windows Startup folder so it runs automatically on login.

Run it once:

```powershell
powershell -ExecutionPolicy Bypass -File create_startup.ps1
```

### To Stop Jimmy When It's Running in the Background

Open Task Manager → find `pythonw.exe` → End Task.

Or from PowerShell:

```powershell
taskkill /IM pythonw.exe /F
```

---

## 13. Troubleshooting

### "Jimmy doesn't hear me"

- Check that your microphone is set as the **default recording device** in Windows Sound settings.
- Watch the console output. If you see very low `rms` values, your mic gain is too quiet. Increase it in Windows sound settings.
- Try increasing `LISTEN_DURATION_S` from 7.0 to 10.0 if your sentences are getting cut off.

### "CUDA errors on startup"

- The assistant automatically falls back to CPU if CUDA fails. No action required.
- To permanently disable GPU, set `WHISPER_DEVICE = "cpu"` in the config.
- If you want GPU acceleration, install the NVIDIA CUDA Toolkit and ensure your GPU drivers are updated.

### "Wrong voice or no speech"

- pyttsx3 uses Windows SAPI voices. Only installed voices are available.
- Check installed voices: **Settings → Time & Language → Speech → Manage voices**.
- If `speak()` silently fails, check the log file (`jimmy.log`) for TTS errors.

### "Spotify/Brave won't open"

- The executable path in the config is wrong. Use the PowerShell commands in Section 4 to find the correct path.
- If you don't have Brave or Spotify installed, those commands will simply log a warning and do nothing.

### "Build a project gives a 429 error"

- Your Gemini API free tier quota is exhausted. Wait until the daily reset.
- Make sure your Google Cloud project does NOT have a billing account attached. A billing account with $0 credits disables the free tier entirely.
- Create a fresh project at https://aistudio.google.com/ without billing to get full free-tier access.

### "Timer reminder didn't fire"

- You probably restarted Jimmy before the timer expired. Timers live in memory only — restarting the process kills all active timers.
- Solution: Don't restart the assistant while a timer is running.

### "The AI agent created files in the wrong folder"

- The `antigravity_bridge.py` explicitly tells the agent where to write files via `workspaces=[workspace_dir]` and `system_instructions`. If files still end up in the wrong place, the AI model occasionally ignores workspace constraints. This is a limitation of the SDK — the instruction is a strong hint, not a hard sandbox.

---

## 14. FAQ

**Q: Does this work on Mac or Linux?**
A: Not currently. The app uses several Windows-specific APIs: `taskkill` for closing apps, `pycaw` for volume control, `ShellExecuteW` for minimized app launching, and Windows SAPI for TTS. Porting would require replacing all of these with platform-specific equivalents.

**Q: Can I use a different browser instead of Brave?**
A: Yes. Change `BRAVE_EXE` to point to your browser's executable (e.g., Chrome, Firefox, Edge). Update the `search_web()` function's URL template if you want to use a different search engine.

**Q: Can I use a different music player instead of Spotify?**
A: Yes, but you'll need to modify the `play_spotify_song()` function. The current implementation uses Spotify's `spotify:search:` URI scheme. Other players have different URI schemes or may require different approaches.

**Q: Does the AI code generation cost money?**
A: No, if you use the Gemini API free tier correctly. The free tier for `gemini-2.5-flash` provides generous daily limits. Just make sure your Google Cloud project doesn't have a billing account attached.

**Q: Can I change the speaking speed?**
A: Yes. In the `_make_engine()` function, change `engine.setProperty("rate", 175)`. Higher = faster, lower = slower. 175 is a comfortable conversational speed.

**Q: Can I change the Whisper model?**
A: Yes. Set `WHISPER_MODEL_SIZE` to `"tiny"` (fastest, less accurate), `"small"` (slower, more accurate), or `"medium"` (slowest, most accurate). The default `"base"` is a good balance.

**Q: How do I add the project to GitHub?**
A: Make sure your `.env` file is in `.gitignore` (never commit API keys). Then:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/jimmy-assistant.git
git push -u origin main
```

---

*End of documentation.*
