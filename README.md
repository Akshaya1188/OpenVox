# OpenVox

**OpenVox** is an open-source, customizable desktop voice assistant for
Linux, built in Python. Speak to it, and it can tell you the time and
date, search Wikipedia, open websites and applications, do quick math,
take notes, and set reminders — all running locally except for the
Google speech-recognition call used to transcribe your voice.

OpenVox was built with rebranding in mind: change one setting and it
becomes "Nova," "Jarvis," or anything else, without touching the rest
of the code.

## Features

- 🎙️ **Voice input/output** — speech recognition via Google's API,
  text-to-speech via `pyttsx3`
- 🕒 **Time & date**
- 🌐 **Open websites** — Google, YouTube, Facebook, Wikipedia
- 📖 **Wikipedia search** with 2-sentence summaries
- 🧮 **Calculator** — safe arithmetic evaluation (no `eval()`)
- 📝 **Notes** — take a note by voice, read them back later
- ⏰ **Reminders** — "remind me in 5 minutes to take a break"
- 💻 **System info** — OS, hostname, free disk space
- 🚀 **Open applications** — launches any installed app by name
- 🙋 **Personalized profile** — asks your name once, confirms it, and
  lets you correct it if misheard
- 🧩 **Fully configurable** — name, language, voice, microphone, and
  more, all in one file
- 🛡️ **Defensive by design** — handles empty speech, network failures,
  microphone errors, and unknown commands without crashing

## Architecture

```
openvox/
├── config.py          # All user-facing settings live here
├── main.py             # Entry point
└── core/
    ├── speech.py        # Text-to-speech + speech-to-text (SpeechEngine)
    ├── profile.py       # Asks for / confirms the user's name (UserProfile)
    ├── commands.py       # Parses commands and performs actions (CommandHandler)
    └── assistant.py      # Wires the above together and runs the main loop
```

The design is intentionally simple:

- **`config.py`** is the single source of truth for anything
  customizable — assistant name, language, voice, microphone device,
  file paths, and the application whitelist.
- **`SpeechEngine`** only knows how to speak and listen. It never
  interprets commands.
- **`UserProfile`** only knows how to collect and confirm the user's
  name.
- **`CommandHandler`** owns a simple routing table mapping trigger
  phrases to methods, making it easy to add new commands.
- **`Assistant`** wires these three together and runs the main loop,
  including clean shutdown on Ctrl+C.

## Requirements

- Linux (developed and tested on Ubuntu)
- Python 3.8+
- A working microphone
- An internet connection (for Google speech recognition and Wikipedia
  search)

### Linux system packages

`PyAudio` requires PortAudio's development headers to build. Install
them before installing Python dependencies:

```bash
sudo apt update
sudo apt install portaudio19-dev python3-pyaudio espeak
```

`espeak` (or another speech-dispatcher voice) is required by `pyttsx3`
for text-to-speech on Linux.

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/OpenVox.git
cd OpenVox

# 2. Create and activate a virtual environment (conda example)
conda create -n openvox python=3.8
conda activate openvox

# --- or with venv ---
# python3 -m venv venv
# source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt
```

## Running OpenVox

```bash
cd openvox
python main.py
```

On first run, OpenVox will ask for your name, confirm it, and then wait
for commands. Say **"help"** at any time to hear what it can do, and
**"exit"**, **"quit"**, or **"goodbye"** to stop.

### Finding your microphone device index

If OpenVox can't hear you, or picks the wrong microphone, list the
available devices:

```bash
cd openvox
python -m core.speech --list-devices
```

Then set the index in `config.py` (or via environment variable):

```bash
export OPENVOX_MIC_DEVICE_INDEX=0
```

## Configuration

All settings live in `openvox/config.py`. Most can also be set via
environment variables so personal settings don't need to be committed:

| Setting | Config variable | Environment variable |
|---|---|---|
| Assistant name | `ASSISTANT_NAME` | `OPENVOX_ASSISTANT_NAME` |
| Pre-set user name | `USER_NAME` | `OPENVOX_USER_NAME` |
| Recognition language | `LANGUAGE` | `OPENVOX_LANGUAGE` |
| Microphone device index | `MICROPHONE_DEVICE_INDEX` | `OPENVOX_MIC_DEVICE_INDEX` |
| Voice speed (wpm) | `VOICE_RATE` | — |
| Voice volume (0.0–1.0) | `VOICE_VOLUME` | — |
| Voice ID substring | `VOICE_PREFERENCE` | — |
| Whitelisted apps | `APPLICATIONS` (dict) | — |
| Exit phrases | `EXIT_COMMANDS` (set) | — |

**Example — rebrand the assistant as "Nova":**

```python
# openvox/config.py
ASSISTANT_NAME = "Nova"
```

or without editing code:

```bash
export OPENVOX_ASSISTANT_NAME="Nova"
```

> **Note:** sample rate and chunk size are intentionally not
> configurable. Forcing values like 44100 Hz caused PortAudio errors on
> some Linux microphones — letting PortAudio/ALSA negotiate the
> microphone's native settings is more reliable across hardware.

## Available Commands

| Say... | OpenVox does |
|---|---|
| "what time is it" | Tells the current time |
| "what's the date" | Tells today's date |
| "who are you" / "what's your name" | Introduces itself and you |
| "open google" / "youtube" / "facebook" / "wikipedia" | Opens the site in your browser |
| "search wikipedia for `<topic>`" | Reads a 2-sentence Wikipedia summary |
| "calculate 12 plus 8" | Does the math and speaks the result |
| "take a note" | Asks what to write, then saves it with a timestamp |
| "read my notes" | Reads back your most recent notes |
| "remind me in 5 minutes to `<task>`" | Speaks a reminder after the delay |
| "system info" | Reports OS, hostname, and free disk space |
| "open `<app>`" | Launches any installed application by name (e.g. "open firefox"); `config.APPLICATIONS` can map friendly phrases like "text editor" to a specific executable |
| "change my name" | Re-asks for and saves a new name |
| "help" | Lists available commands |
| "exit" / "quit" / "stop" / "goodbye" | Ends the session |

OpenVox remembers your name after the first run (saved to
`openvox/data/profile.json`), so it won't ask again on future runs
unless you say "change my name" or delete that file.

## Example Interaction

```text
OpenVox: Hello. I am OpenVox.
OpenVox: What would you like me to call you?
You: call me comedy
OpenVox: Did you say comedy?
You: yes call me comedy
OpenVox: Got it. I will call you Comedy.
OpenVox: How can I help you, Comedy?
You: what time is it
OpenVox: The time is 09:42 PM.
You: calculate 12 plus 8
OpenVox: That equals 20.
You: goodbye
OpenVox: Goodbye Comedy.
```

## Project Structure

```
Openvox/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── .gitignore
├── requirements.txt
├── openvox/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── data/          # Notes and other runtime data (gitignored)
│   ├── logs/           # Reserved for future logging (gitignored)
│   └── core/
│       ├── __init__.py
│       ├── speech.py
│       ├── profile.py
│       ├── commands.py
│       └── assistant.py
└── tests/
    ├── conftest.py
    ├── test_config.py
    ├── test_profile.py
    └── test_commands.py
```

## Running Tests

Tests never touch the microphone or a real TTS engine — a fake speech
object is used instead. From the repository root:

```bash
pip install pytest
pytest
```

## Troubleshooting

**ALSA/JACK warnings on startup** (`ALSA lib pcm_dsnoop.c...`, `jack
server is not running...`) — these are harmless console noise from
PortAudio probing audio devices and can be ignored.

**`Expression 'parameters->channelCount <= maxChans' failed`** — this
happens when a sample rate or chunk size is forced that your
microphone doesn't support. OpenVox avoids this by letting
PortAudio/ALSA use the microphone's native settings; if you've modified
`speech.py` to force these values, remove that.

**OpenVox doesn't hear anything** — run
`python -m core.speech --list-devices` from inside `openvox/`, find
your microphone's index, and set `OPENVOX_MIC_DEVICE_INDEX`.

**No sound when OpenVox speaks** — make sure `espeak` (or another
speech-dispatcher backend) is installed: `sudo apt install espeak`.

**`PyAudio` fails to install** — install PortAudio's dev headers first:
`sudo apt install portaudio19-dev`.

**Wikipedia search fails or times out** — check your internet
connection; Wikipedia search and speech recognition both require
network access.

## How to Add a New Command

1. Add a `cmd_your_feature(self, command)` method to `CommandHandler`
   in `openvox/core/commands.py`.
2. Register a trigger phrase for it in `_build_routes()` — put more
   specific phrases above more general ones.
3. Mention it in `cmd_help`.
4. Add a test in `tests/test_commands.py`.

See `CONTRIBUTING.md` for more detail.

## Contributing

Contributions are welcome! Please read `CONTRIBUTING.md` for setup
instructions and guidelines before opening a pull request. This
project also follows a `CODE_OF_CONDUCT.md`.

## License

Released under the [MIT License](LICENSE).

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the current state of the project,
what's planned next, and notes for picking development back up after
a break.
