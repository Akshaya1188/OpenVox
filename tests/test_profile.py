"""
Tests for UserProfile. A FakeSpeech stand-in replaces SpeechEngine so
these tests never touch the microphone or text-to-speech engine, and
config.PROFILE_FILE is redirected to a temp path so tests never read
or write the real saved profile.
"""

import pytest

import config
from core.profile import UserProfile


class FakeSpeech:
    """Minimal stand-in for SpeechEngine: feeds scripted responses to
    listen() and records everything spoken."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.spoken = []

    def speak(self, text):
        self.spoken.append(text)

    def listen(self):
        if self.responses:
            return self.responses.pop(0)
        return ""


@pytest.fixture(autouse=True)
def isolated_profile_file(tmp_path, monkeypatch):
    """Every test gets its own empty profile file location, so tests
    never read a leftover name from a real run of the assistant."""
    monkeypatch.setattr(config, "PROFILE_FILE", str(tmp_path / "profile.json"))


def test_extract_name_with_prefix():
    profile = UserProfile(FakeSpeech([]))
    assert profile.extract_name("call me Alex") == "Alex"


def test_extract_name_plain_word():
    profile = UserProfile(FakeSpeech([]))
    assert profile.extract_name("comedy") == "Comedy"


def test_extract_name_with_punctuation():
    profile = UserProfile(FakeSpeech([]))
    assert profile.extract_name("my name is Sam.") == "Sam"


def test_extract_name_rejects_yes_no_words():
    profile = UserProfile(FakeSpeech([]))
    assert profile.extract_name("yes") is None
    assert profile.extract_name("okay") is None


def test_is_yes_variants():
    profile = UserProfile(FakeSpeech([]))
    assert profile.is_yes("yes")
    assert profile.is_yes("yeah, that's right")
    assert not profile.is_yes("no")


def test_is_no_variants():
    profile = UserProfile(FakeSpeech([]))
    assert profile.is_no("no")
    assert profile.is_no("nope")
    assert not profile.is_no("yes")


def test_setup_full_flow_with_confirmation():
    speech = FakeSpeech(["call me comedy", "yes"])
    profile = UserProfile(speech)

    name = profile.setup()

    assert name == "Comedy"
    assert profile.name == "Comedy"


def test_setup_with_correction_flow():
    speech = FakeSpeech(["call me comody", "no, call me comedy", "yes"])
    profile = UserProfile(speech)

    name = profile.setup()

    assert name == "Comedy"


def test_setup_retries_on_empty_response():
    speech = FakeSpeech(["", "call me alex", "yes"])
    profile = UserProfile(speech)

    name = profile.setup()

    assert name == "Alex"


def test_setup_saves_name_for_next_run():
    speech = FakeSpeech(["call me comedy", "yes"])
    profile = UserProfile(speech)
    profile.setup()

    # A fresh instance, as if the app were restarted, should load the
    # saved name instead of asking again.
    second_speech = FakeSpeech([])
    second_profile = UserProfile(second_speech)
    name = second_profile.setup()

    assert name == "Comedy"
    assert second_speech.responses == []  # never had to call listen()
    assert any("welcome back" in line.lower() for line in second_speech.spoken)


def test_setup_force_ignores_saved_name_and_asks_again():
    speech = FakeSpeech(["call me comedy", "yes"])
    profile = UserProfile(speech)
    profile.setup()

    speech.responses = ["call me alex", "yes"]
    name = profile.setup(force=True)

    assert name == "Alex"


def test_load_saved_name_returns_none_when_no_file():
    profile = UserProfile(FakeSpeech([]))
    assert profile.load_saved_name() is None


def test_load_saved_name_handles_corrupt_file(tmp_path, monkeypatch):
    bad_file = tmp_path / "profile.json"
    bad_file.write_text("not valid json{{{")
    monkeypatch.setattr(config, "PROFILE_FILE", str(bad_file))

    profile = UserProfile(FakeSpeech([]))
    assert profile.load_saved_name() is None
