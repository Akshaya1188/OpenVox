"""
Tests for the Assistant orchestration loop, focused on the "change my
name" mid-session flow. Speech and commands are faked so no real
microphone, TTS engine, or config.PROFILE_FILE write is involved.
"""

import config
from core.assistant import Assistant


class FakeSpeech:
    def __init__(self, responses):
        self.responses = list(responses)
        self.spoken = []

    def speak(self, text):
        self.spoken.append(text)

    def listen(self):
        if self.responses:
            return self.responses.pop(0)
        return ""


class FakeCommandHandler:
    """Records what it was asked to handle instead of doing anything."""

    def __init__(self, speech, user_name):
        self.speech = speech
        self.user_name = user_name
        self.handled = []

    def handle(self, command):
        self.handled.append(command)


def make_assistant(monkeypatch, profile_tmp_path, responses):
    monkeypatch.setattr(config, "PROFILE_FILE", str(profile_tmp_path / "profile.json"))
    monkeypatch.setattr(config, "USER_NAME", "")

    assistant = Assistant.__new__(Assistant)  # skip SpeechEngine() hardware init
    assistant.speech = FakeSpeech(responses)

    from core.profile import UserProfile

    assistant.profile = UserProfile(assistant.speech)
    assistant.commands = None
    return assistant


def test_change_my_name_mid_session(monkeypatch, tmp_path):
    responses = [
        "call me alex", "yes",       # initial setup
        "change my name",             # trigger rename
        "call me sam", "yes",         # new name setup
        "exit",
    ]
    assistant = make_assistant(monkeypatch, tmp_path, responses)

    original_handler_cls = None
    import core.assistant as assistant_module
    monkeypatch.setattr(assistant_module, "CommandHandler", FakeCommandHandler)

    assistant.run()

    assert assistant.commands.user_name == "Sam"
    assert any("goodbye sam" in line.lower() for line in assistant.speech.spoken)
