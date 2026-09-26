"""
Speech input/output for OpenVox.

Wraps pyttsx3 (text-to-speech) and SpeechRecognition + PyAudio
(speech-to-text) behind a single SpeechEngine class, with defensive
error handling so a microphone or network hiccup never crashes the
assistant.
"""

import sys

import pyttsx3
import speech_recognition as sr

import config


class SpeechEngine:
    """Handles all spoken input and output for OpenVox."""

    def __init__(self):
        self.engine = pyttsx3.init()
        self._select_voice()

        self.engine.setProperty("rate", config.VOICE_RATE)
        self.engine.setProperty("volume", config.VOICE_VOLUME)

        self.recognizer = sr.Recognizer()
        self.microphone_device = config.MICROPHONE_DEVICE_INDEX

    def _select_voice(self):
        """Pick a voice matching VOICE_PREFERENCE, if one is available."""
        preference = (config.VOICE_PREFERENCE or "").lower().strip()

        if not preference:
            return

        try:
            voices = self.engine.getProperty("voices")
        except Exception as error:
            print(f"Could not read available voices: {error}")
            return

        for voice in voices or []:
            voice_id = getattr(voice, "id", "") or ""

            if preference in voice_id.lower():
                self.engine.setProperty("voice", voice.id)
                return

    def speak(self, text):
        """Speak text aloud and print it to the console."""
        if not text:
            return

        text = str(text).strip()

        if not text:
            return

        print(f"{config.ASSISTANT_NAME}: {text}")

        try:
            self.engine.say(text)
            self.engine.runAndWait()

        except Exception as error:
            print(f"Text-to-speech error: {error}")

    def listen(self):
        """Listen on the microphone and return recognized text (lowercase),
        or an empty string if nothing usable was heard."""
        try:
            with sr.Microphone(device_index=self.microphone_device) as source:
                print("Listening...")

                audio = self.recognizer.listen(
                    source,
                    timeout=config.LISTEN_TIMEOUT,
                    phrase_time_limit=config.PHRASE_TIME_LIMIT,
                )

            print("Recognizing...")

            text = self.recognizer.recognize_google(
                audio,
                language=config.LANGUAGE,
            )

            text = text.strip().lower()

            if text:
                print(f"You: {text}")

            return text

        except sr.WaitTimeoutError:
            print("No speech detected.")
            return ""

        except sr.UnknownValueError:
            print("Sorry, I could not understand that.")
            return ""

        except sr.RequestError as error:
            print(f"Speech recognition service error: {error}")
            return ""

        except OSError as error:
            print(f"Microphone error: {error}")
            return ""

        except Exception as error:
            print(f"Unexpected speech error: {error}")
            return ""

    @staticmethod
    def list_microphones():
        """Print all available microphone names with their device index.
        Useful for finding the correct MICROPHONE_DEVICE_INDEX value."""
        try:
            names = sr.Microphone.list_microphone_names()
        except Exception as error:
            print(f"Could not list microphones: {error}")
            return

        if not names:
            print("No microphones found.")
            return

        for index, name in enumerate(names):
            print(f"[{index}] {name}")


if __name__ == "__main__":
    if "--list-devices" in sys.argv:
        SpeechEngine.list_microphones()
    else:
        print("Usage: python -m core.speech --list-devices")
