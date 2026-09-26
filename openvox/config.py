"""
OpenVox configuration.

Centralized configuration for the OpenVox voice assistant. Change the
values below to customize your assistant's name, voice, language,
microphone, and behavior. Nothing else in the codebase should hardcode
these values.

Most settings can also be overridden with environment variables, which
is useful for keeping personal settings out of version control.
"""

import os

# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------

# The name the assistant uses to refer to itself. Change this (or set the
# OPENVOX_ASSISTANT_NAME environment variable) to rebrand the assistant,
# e.g. "Nova" or "Jarvis", without touching any other code.
ASSISTANT_NAME = os.environ.get("OPENVOX_ASSISTANT_NAME", "OpenVox")

# Optional: pre-set the user's name to skip the name-setup conversation
# on every run. Leave empty to have OpenVox ask for it interactively.
USER_NAME = os.environ.get("OPENVOX_USER_NAME", "")

# ---------------------------------------------------------------------------
# Speech recognition (listening)
# ---------------------------------------------------------------------------

# Language code passed to the Google speech recognition engine.
LANGUAGE = os.environ.get("OPENVOX_LANGUAGE", "en-in")

# Seconds to wait for speech to start before giving up on a listen() call.
LISTEN_TIMEOUT = 10

# Maximum length, in seconds, of a single phrase once speech has started.
PHRASE_TIME_LIMIT = 8

# PyAudio device index for the microphone to use. Run:
#   python -m core.speech --list-devices
# (from inside the openvox/ directory) to print available microphones
# and their index numbers. Override with the OPENVOX_MIC_DEVICE_INDEX
# environment variable if needed.
_mic_index_env = os.environ.get("OPENVOX_MIC_DEVICE_INDEX")
MICROPHONE_DEVICE_INDEX = int(_mic_index_env) if _mic_index_env else 0

# NOTE: sample rate and chunk size are intentionally NOT configured here.
# Forcing values such as 44100 Hz / 1024 samples caused PortAudio errors
# ("channelCount <= maxChans") on some Linux microphones. Leaving these
# unset lets PortAudio/ALSA negotiate the microphone's native settings,
# which is far more reliable across different hardware.

# ---------------------------------------------------------------------------
# Voice output (speaking)
# ---------------------------------------------------------------------------

# Speech rate in words per minute.
VOICE_RATE = 150

# Volume from 0.0 (silent) to 1.0 (full volume).
VOICE_VOLUME = 1.0

# Substring matched (case-insensitive) against available system voice IDs.
# Leave empty ("") to use the pyttsx3 engine's default voice.
VOICE_PREFERENCE = "en-us"

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PACKAGE_DIR, "data")
LOG_DIR = os.path.join(PACKAGE_DIR, "logs")
NOTES_FILE = os.path.join(DATA_DIR, "notes.txt")

# Where the confirmed user name is remembered between runs, so OpenVox
# only has to ask once. Delete this file (or say "change my name") to
# be asked again.
PROFILE_FILE = os.path.join(DATA_DIR, "profile.json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Application launcher whitelist
# ---------------------------------------------------------------------------

# Maps a spoken phrase to a system executable. Only executables listed
# here can ever be launched by voice, so it is safe to add more entries.
APPLICATIONS = {
    "text editor": "gedit",
    "calculator app": "gnome-calculator",
    "terminal": "gnome-terminal",
    "file manager": "nautilus",
}

# ---------------------------------------------------------------------------
# Conversation control
# ---------------------------------------------------------------------------

EXIT_COMMANDS = {"exit", "quit", "stop", "goodbye", "shutdown", "bye"}

# Phrases that trigger re-asking for the user's name mid-session, even
# though a name is already remembered.
RENAME_TRIGGERS = ("change my name", "change name", "reset my name")
