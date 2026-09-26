"""
Top-level Assistant class for OpenVox.

Wires together speech, the user profile, and command handling, and
owns the main conversation loop, including clean shutdown on Ctrl+C.
"""

import config
from core.speech import SpeechEngine
from core.commands import CommandHandler
from core.profile import UserProfile


class Assistant:
    """Owns the main OpenVox run loop."""

    def __init__(self):
        self.speech = SpeechEngine()
        self.profile = UserProfile(self.speech)
        self.commands = None

    def run(self):
        """Greet the user, set up their profile, and start listening."""
        self.speech.speak(f"Hello. I am {config.ASSISTANT_NAME}.")

        user_name = self.profile.setup() or "friend"
        self.commands = CommandHandler(self.speech, user_name)

        self.speech.speak(f"How can I help you, {user_name}?")

        try:
            self._loop(user_name)
        except KeyboardInterrupt:
            print("\nInterrupted. Shutting down cleanly.")
            self.speech.speak(f"Goodbye {user_name}.")

    def _loop(self, user_name):
        while True:
            command = self.speech.listen()

            if not command:
                continue

            command = command.strip().lower()

            if command in config.EXIT_COMMANDS:
                self.speech.speak(f"Goodbye {user_name}.")
                break

            if any(trigger in command for trigger in config.RENAME_TRIGGERS):
                user_name = self.profile.setup(force=True) or user_name
                self.commands.user_name = user_name
                self.speech.speak(f"How can I help you, {user_name}?")
                continue

            self.commands.handle(command)
