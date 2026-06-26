<p align="center">
  <img src="https://img.icons8.com/fluency/96/microphone.png" alt="Logo" width="96" height="96" />
</p>

<h1 align="center">JIMMY & SAMMY</h1>

<p align="center">
  <strong>Dual-persona, offline voice assistant for Windows with AI-powered code generation</strong>
</p>

<p align="center">
  <a href="#voice-commands"><img src="https://img.shields.io/badge/wake_words-Hey_Jimmy_|_Hey_Sammy-blueviolet?style=for-the-badge" alt="Wake Words" /></a>
  <img src="https://img.shields.io/badge/100%25-Offline-success?style=for-the-badge&logo=wifi" alt="Offline" />
  <img src="https://img.shields.io/badge/cost-$0-brightgreen?style=for-the-badge" alt="Free" />
  <img src="https://img.shields.io/badge/platform-Windows-0078D6?style=for-the-badge&logo=windows" alt="Windows" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/STT-Faster_Whisper-orange?style=flat-square" alt="Faster Whisper" />
  <img src="https://img.shields.io/badge/TTS-pyttsx3-blue?style=flat-square" alt="pyttsx3" />
  <img src="https://img.shields.io/badge/AI-Antigravity_SDK-ff69b4?style=flat-square" alt="Antigravity SDK" />
  <img src="https://img.shields.io/badge/GPU-CUDA_supported-76B900?style=flat-square&logo=nvidia&logoColor=white" alt="CUDA" />
</p>

---

## What is this?

A **fully offline, zero-cost** voice assistant that runs entirely on your local machine. No cloud APIs for voice processing, no subscriptions, no data leaving your PC.

Say **"Hey Jimmy"** (male voice) or **"Hey Sammy"** (female voice) and they get to work — opening apps, controlling volume, searching the web, and even **building entire software projects** using the Google Antigravity SDK.

---

## Features

| Category | What it does |
| :--- | :--- |
| **Dual Personas** | Two wake words with distinct voices — switch seamlessly mid-session |
| **AI Code Generation** | Say *"build a python script"* and an AI agent writes the code for you |
| **App Control** | Open/close Spotify, Brave browser, Antigravity IDE by voice |
| **Music** | Search and play songs on Spotify |
| **Web Search** | Voice-activated search via Brave Search |
| **Volume Control** | Mute, unmute, volume up/down, or set to a specific percentage |
| **Screenshots** | Capture your screen with a voice command |
| **Timers & Reminders** | Set countdown timers or named reminders |
| **Power Control** | Shutdown or restart your laptop by voice |
| **100% Offline Voice** | Speech recognition and TTS run locally — no internet needed |
| **GPU Accelerated** | CUDA support for NVIDIA GPUs with automatic CPU fallback |

---

## Quick Start

### Prerequisites

- **Python 3.10+**
- **Windows 10/11**
- A working **microphone**
- *(Optional)* NVIDIA GPU with CUDA for faster transcription
- *(Optional)* [Google Gemini API key](https://aistudio.google.com/) for AI code generation

### Installation

```bash
git clone https://github.com/Yashwanth-23/jimmy-assistant.git
cd jimmy-assistant

pip install -r requirements.txt

python jimmy.py
```

### AI Code Generation Setup (Optional)

To enable the "build a project" feature, create a `.env` file:

```
GOOGLE_API_KEY=your_gemini_api_key_here
```

> [!TIP]
> On first run, Whisper will download its model (~150 MB for `base`). This only happens once.

---

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   🎤  Microphone continuously captures audio            │
│    ↓                                                    │
│   🔍  Faster-Whisper transcribes speech locally          │
│    ↓                                                    │
│   🗣️  "Hey Jimmy" or "Hey Sammy" detected?              │
│    ↓ YES                                                │
│   ✅  Wake actions fire:                                 │
│       • Brave browser launches (if not running)         │
│       • Welcome greeting spoken                         │
│    ↓                                                    │
│   👂  Listens for voice commands (60s window)            │
│       • "Build a python script" → AI agent spawns       │
│       • "Play Shape of You" → opens in Spotify          │
│       • "Search for python tutorials" → Brave Search    │
│       • "Thank you" / "Goodbye" → back to sleep         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Voice Commands

After saying **"Hey Jimmy"** or **"Hey Sammy"**, a 60-second command window opens. You can say any of the following:

### AI Code Generation

| Command | What happens |
| :--- | :--- |
| `"Build a python script that..."` | Spawns an AI agent to write the code |
| `"Build a project"` | Asks what to build, then spawns an agent |
| `"Ship a feature"` | Same as above |

### App Control

| Command | What happens |
| :--- | :--- |
| `"Open Spotify"` / `"Launch Spotify"` | Opens Spotify (minimized) |
| `"Close Spotify"` / `"Stop Spotify"` | Force-closes Spotify |
| `"Open Brave"` / `"Open browser"` | Opens Brave browser |
| `"Close Brave"` / `"Close browser"` | Force-closes Brave |
| `"Open Antigravity"` | Opens the Antigravity IDE |

### Music

| Command | What happens |
| :--- | :--- |
| `"Play [song name]"` | Searches and plays on Spotify |

### Web Search

| Command | What happens |
| :--- | :--- |
| `"Search for [query]"` | Opens Brave Search with the query |
| `"What is [query]"` | Same as above |
| `"Who is [query]"` | Same as above |

### Volume

| Command | What happens |
| :--- | :--- |
| `"Volume up"` / `"Increase volume"` | Increases volume by 10% |
| `"Volume down"` / `"Decrease volume"` | Decreases volume by 10% |
| `"Set volume to [number]"` | Sets volume to exact percentage |
| `"Mute"` / `"Mute audio"` | Mutes system audio |
| `"Unmute"` / `"Unmute audio"` | Unmutes system audio |

### Timers & Reminders

| Command | What happens |
| :--- | :--- |
| `"Set a timer for [N] minutes"` | Speaks "Time is up" when done |
| `"Remind me to [task] in [N] minutes"` | Speaks the reminder when done |

### Screenshots

| Command | What happens |
| :--- | :--- |
| `"Take a screenshot"` | Saves screenshot to `screenshots/` |

### Power

| Command | What happens |
| :--- | :--- |
| `"Shut down the laptop"` | Shuts down in 10 seconds |
| `"Restart the laptop"` | Restarts in 10 seconds |

### Session Control

| Command | What happens |
| :--- | :--- |
| `"Thank you"` / `"Thanks"` | Ends the command session |
| `"Goodbye"` / `"Go to sleep"` | Ends the command session |
| Say the other wake word mid-session | Switches persona and voice |

> [!NOTE]
> You can combine wake word + command in one phrase: **"Hey Jimmy, open Brave"** — it handles it in a single pass.

---

## Switching Between Jimmy & Sammy

Both personas share the same brain and capabilities. The only difference is their voice:

- **Jimmy** → Microsoft David (male)
- **Sammy** → Microsoft Zira (female)

You can switch mid-session by saying the other wake word. For example, if Jimmy is active and you say **"Hey Sammy"**, the voice switches to Zira immediately.

---

## Configuration

All settings live at the top of [`jimmy.py`](jimmy.py):

```python
WAKE_WORDS = {"hey jimmy": "david", "hey sammy": "zira"}

BRAVE_EXE       = r"C:\...\brave.exe"
SPOTIFY_EXE     = r"C:\...\Spotify.exe"
ANTIGRAVITY_EXE = r"C:\...\Antigravity.exe"

WHISPER_MODEL_SIZE = "base"      # tiny | base | small | medium
WHISPER_DEVICE     = "cuda"      # cuda | cpu
WHISPER_COMPUTE    = "int8"      # int8 | float16

LISTEN_DURATION_S        = 7.0   # seconds per audio capture
COMMAND_LISTEN_TIMEOUT_S = 60.0  # how long to listen after wake
```

### Whisper Model Comparison

| Model | Size | Speed | Accuracy | Best for |
| :--- | :--- | :--- | :--- | :--- |
| `tiny` | ~75 MB | ⚡⚡⚡ | ★★☆☆ | Low-end hardware, fastest response |
| `base` | ~150 MB | ⚡⚡ | ★★★☆ | **Recommended** — good balance |
| `small` | ~500 MB | ⚡ | ★★★★ | Higher accuracy, needs more RAM |
| `medium` | ~1.5 GB | 🐢 | ★★★★★ | Best accuracy, needs GPU |

---

## Project Structure

```
jimmy-assistant/
├── jimmy.py              # Main assistant — voice loop, commands, wake detection
├── antigravity_bridge.py  # Spawns Antigravity SDK agents for code generation
├── requirements.txt       # Python dependencies
├── .env                   # Gemini API key (optional, for AI features)
├── start_jimmy.vbs        # Windows startup script (run minimized)
├── create_startup.ps1     # PowerShell script to add Jimmy to Windows startup
├── projects/              # AI-generated project folders go here
├── screenshots/           # Saved screenshots go here
└── README.md
```

---

## Tech Stack

| Component | Library | Purpose |
| :--- | :--- | :--- |
| **Speech-to-Text** | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Local, GPU-accelerated transcription |
| **Text-to-Speech** | [pyttsx3](https://github.com/nateshmbhat/pyttsx3) | Offline speech synthesis (Windows SAPI) |
| **Audio Capture** | [sounddevice](https://github.com/spatialaudio/python-sounddevice) | Microphone input |
| **AI Agent** | [Google Antigravity SDK](https://ai.google.dev) | Autonomous code generation |
| **Volume Control** | [pycaw](https://github.com/AndreMiras/pycaw) | Windows audio endpoint control |

---

## Troubleshooting

<details>
<summary><strong>🔇 Jimmy doesn't hear me</strong></summary>

- Make sure your microphone is set as the **default recording device** in Windows Sound settings.
- Check the console — if `rms` values are very low, your mic gain may be too quiet.

</details>

<details>
<summary><strong>⚠️ CUDA errors on startup</strong></summary>

- Jimmy automatically falls back to CPU if CUDA fails — no action needed.
- To force CPU mode, set `WHISPER_DEVICE = "cpu"` in `jimmy.py`.

</details>

<details>
<summary><strong>🗣️ Wrong voice or robotic speech</strong></summary>

- `pyttsx3` uses Windows SAPI voices. Install additional voices via: **Settings → Time & Language → Speech → Manage voices**.
- The voice is determined by which wake word you use — "Hey Jimmy" uses David, "Hey Sammy" uses Zira.

</details>

<details>
<summary><strong>📱 Spotify / Brave won't open</strong></summary>

- Verify the executable paths in the config section of `jimmy.py`.
- Run this in PowerShell to find your paths:
  ```powershell
  Get-ChildItem $env:LOCALAPPDATA -Recurse -Filter 'brave.exe' | Select -First 1 -ExpandProperty FullName
  Get-ChildItem $env:LOCALAPPDATA -Recurse -Filter 'Spotify.exe' | Select -First 1 -ExpandProperty FullName
  ```

</details>

<details>
<summary><strong>🤖 "Build a project" gives a 429 error</strong></summary>

- This means your Gemini API free tier quota is exhausted for the day.
- Create a new Google Cloud project **without** a billing account attached to get the full free tier.
- The AI agent uses `gemini-2.5-flash` which has generous free limits.

</details>

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  <sub>Built with ❤️ and zero API costs</sub>
</p>
