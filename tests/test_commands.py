"""
Tests for CommandHandler. A FakeSpeech stand-in replaces SpeechEngine
so these tests never touch the microphone, TTS engine, or network.
"""

import os

import pytest

import config
from core.commands import CommandHandler


class FakeSpeech:
    def __init__(self, responses=None):
        self.responses = list(responses or [])
        self.spoken = []

    def speak(self, text):
        self.spoken.append(text)

    def listen(self):
        if self.responses:
            return self.responses.pop(0)
        return ""


@pytest.fixture
def handler():
    return CommandHandler(FakeSpeech(), "Comedy")


def test_time_command(handler):
    handler.handle("what time is it")
    assert "time" in handler.speech.spoken[-1].lower()


def test_date_command(handler):
    handler.handle("what's the date today")
    assert "today" in handler.speech.spoken[-1].lower()


def test_identity_command_uses_user_name_and_assistant_name(handler):
    handler.handle("what is your name")
    reply = handler.speech.spoken[-1]
    assert "Comedy" in reply
    assert config.ASSISTANT_NAME in reply


def test_help_command_lists_capabilities(handler):
    handler.handle("help")
    assert "time" in handler.speech.spoken[-1].lower()


def test_unknown_command_falls_back_gracefully(handler):
    handler.handle("do a backflip")
    assert "don't know" in handler.speech.spoken[-1].lower()


def test_calculate_addition(handler):
    handler.handle("calculate 12 plus 8")
    assert "20" in handler.speech.spoken[-1]


def test_calculate_with_word_operators(handler):
    handler.handle("calculate 6 times 7")
    assert "42" in handler.speech.spoken[-1]


def test_calculate_invalid_expression_does_not_crash(handler):
    handler.handle("calculate open the pod bay doors")
    reply = handler.speech.spoken[-1].lower()
    assert "sorry" in reply or "couldn't" in reply


def test_calculate_blocks_code_execution(handler):
    # The calculator must never behave like eval(): this should fail
    # safely rather than importing/running anything.
    handler.handle("calculate __import__('os').system('echo hi')")
    reply = handler.speech.spoken[-1].lower()
    assert "sorry" in reply or "couldn't" in reply


def test_open_known_website(handler, monkeypatch):
    opened = {}
    monkeypatch.setattr(
        "core.commands.webbrowser.open", lambda url: opened.setdefault("url", url)
    )
    handler.handle("open google")
    assert opened["url"] == "https://www.google.com"


def test_open_uninstalled_application_is_reported(handler, monkeypatch):
    monkeypatch.setattr("core.commands.shutil.which", lambda name: None)
    handler.handle("open spaceship")
    assert "couldn't find" in handler.speech.spoken[-1].lower()


def test_open_app_launches_by_spoken_name_if_installed(handler, monkeypatch):
    launched = {}
    monkeypatch.setattr(
        "core.commands.shutil.which", lambda name: "/usr/bin/firefox" if name == "firefox" else None
    )
    monkeypatch.setattr(
        "core.commands.subprocess.Popen", lambda args: launched.setdefault("args", args)
    )
    handler.handle("open firefox")
    assert launched["args"] == ["firefox"]
    assert "opening firefox" in handler.speech.spoken[-1].lower()


def test_open_app_uses_friendly_alias(handler, monkeypatch):
    launched = {}
    monkeypatch.setattr(
        "core.commands.shutil.which", lambda name: "/usr/bin/gedit" if name == "gedit" else None
    )
    monkeypatch.setattr(
        "core.commands.subprocess.Popen", lambda args: launched.setdefault("args", args)
    )
    handler.handle("open text editor")
    assert launched["args"] == ["gedit"]


def test_add_and_read_note(handler, tmp_path, monkeypatch):
    notes_file = tmp_path / "notes.txt"
    monkeypatch.setattr(config, "NOTES_FILE", str(notes_file))

    handler.speech.responses = ["buy milk"]
    handler.cmd_add_note()
    assert os.path.exists(notes_file)

    handler.cmd_read_notes()
    joined = " ".join(handler.speech.spoken).lower()
    assert "buy milk" in joined


def test_reminder_schedules_without_blocking(handler):
    handler.handle("remind me in 1 minutes to stretch")
    reply = handler.speech.spoken[-1].lower()
    assert "1 minutes" in reply
