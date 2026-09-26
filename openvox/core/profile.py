"""
User profile setup for OpenVox: asks for the user's name, confirms it,
and lets them correct it if it was misheard.
"""

import json
import os
import re

import config


NAME_PREFIXES = [
    "you can call me ",
    "just call me ",
    "please call me ",
    "call me ",
    "my name is ",
    "i am ",
    "i'm ",
    "it's ",
    "its ",
]

CORRECTION_PREFIXES = [
    "no call me ",
    "actually call me ",
] + NAME_PREFIXES

YES_WORDS = [
    "yes", "yeah", "yep", "yup", "correct", "that's right",
    "thats right", "right", "exactly", "sure", "affirmative",
]

NO_WORDS = ["no", "nope", "wrong", "not correct", "incorrect", "negative"]

INVALID_NAMES = {"yes", "yeah", "yep", "yup", "no", "nope", "okay", "ok"}


class UserProfile:
    """Collects and confirms the name OpenVox should call the user."""

    def __init__(self, speech):
        self.speech = speech
        self.name = None

    def setup(self, force=False):
        """Return the user's name, asking and confirming it by voice only
        when necessary.

        Order of preference:
        1. config.USER_NAME, if set (unless force=True).
        2. A name already saved from a previous run (unless force=True).
        3. Ask interactively, then save the result for next time.

        Pass force=True (e.g. from a "change my name" command) to skip
        the first two and always ask fresh.
        """

        if config.USER_NAME and not force:
            self.name = config.USER_NAME
            return self.name

        if not force:
            saved_name = self.load_saved_name()

            if saved_name:
                self.name = saved_name
                self.speech.speak(f"Welcome back, {self.name}.")
                return self.name

        while True:
            self.speech.speak("What would you like me to call you?")
            response = self.speech.listen()

            if not response:
                self.speech.speak("I didn't catch that. Please tell me again.")
                continue

            name = self.extract_name(response)

            if not name:
                self.speech.speak(
                    "I couldn't understand the name. Please try again."
                )
                continue

            self.speech.speak(f"Did you say {name}?")
            confirmation = self.speech.listen()

            if self.is_yes(confirmation):
                return self._confirm_and_save(name)

            if self.is_no(confirmation):
                corrected_name = self.extract_correction(confirmation)

                if corrected_name:
                    self.speech.speak(f"Did you say {corrected_name}?")
                    second_confirmation = self.speech.listen()

                    if self.is_yes(second_confirmation):
                        return self._confirm_and_save(corrected_name)

                self.speech.speak("Okay. Let's try again.")
                continue

            self.speech.speak("I didn't understand. Please say yes or no.")

    def _confirm_and_save(self, name):
        """Set self.name, speak confirmation, persist it for next run,
        and return it."""
        self.name = name
        self.speech.speak(f"Got it. I will call you {self.name}.")
        self.save_name(self.name)
        return self.name

    def load_saved_name(self):
        """Return the name saved from a previous run, or None."""
        if not os.path.exists(config.PROFILE_FILE):
            return None

        try:
            with open(config.PROFILE_FILE, "r", encoding="utf-8") as profile_file:
                data = json.load(profile_file)
            return data.get("name") or None

        except (OSError, json.JSONDecodeError) as error:
            print(f"Could not read saved profile: {error}")
            return None

    def save_name(self, name):
        """Persist the confirmed name so future runs don't have to ask."""
        try:
            with open(config.PROFILE_FILE, "w", encoding="utf-8") as profile_file:
                json.dump({"name": name}, profile_file)

        except OSError as error:
            print(f"Could not save profile: {error}")

    def _normalize(self, text):
        """Lowercase, collapse whitespace, and drop punctuation so that
        speech-recognition artifacts like commas and periods don't break
        prefix or keyword matching."""
        if not text:
            return ""

        text = text.strip().lower()
        text = re.sub(r"[.,!?;:]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def extract_name(self, text):
        text = self._normalize(text)

        if not text:
            return None

        for prefix in NAME_PREFIXES:
            if text.startswith(prefix):
                name = text[len(prefix):].strip()

                if name:
                    return self.clean_name(name)

                return None

        return self.clean_name(text)

    def extract_correction(self, text):
        text = self._normalize(text)

        if not text:
            return None

        for prefix in CORRECTION_PREFIXES:
            if text.startswith(prefix):
                name = text[len(prefix):].strip()

                if name:
                    return self.clean_name(name)

        return None

    def clean_name(self, name):
        if not name:
            return None

        name = self._normalize(name)

        if not name or name in INVALID_NAMES:
            return None

        return name.title()

    def is_yes(self, text):
        text = self._normalize(text)

        if not text:
            return False

        return any(
            text == word or text.startswith(word + " ") for word in YES_WORDS
        )

    def is_no(self, text):
        text = self._normalize(text)

        if not text:
            return False

        return any(
            text == word or text.startswith(word + " ") for word in NO_WORDS
        )
