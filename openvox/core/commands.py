"""
Command handling for OpenVox.

Parses a recognized voice command and performs the matching action.
Commands are checked in order via a simple, easy-to-extend routing
table built in `_build_routes`. To add a new command: write a method
on this class, then add a (trigger_words, method) entry to the list.
"""

import ast
import datetime
import operator
import os
import platform
import re
import shutil
import socket
import subprocess
import threading
import webbrowser

import wikipedia

import config


class CommandHandler:
    """Interprets a recognized command string and takes an action."""

    def __init__(self, speech, user_name):
        self.speech = speech
        self.user_name = user_name
        self.routes = self._build_routes()

    def _build_routes(self):
        """Ordered list of (trigger words, handler). The first matching
        entry wins, so more specific triggers must come before generic
        ones (e.g. 'open google' before the generic 'open ')."""
        return [
            (["help", "what can you do"], self.cmd_help),
            (["time"], self.cmd_time),
            (["date", "what day"], self.cmd_date),
            (["your name", "who are you"], self.cmd_identity),
            (["system info", "system information", "computer info"], self.cmd_system_info),
            (["calculate"], self.cmd_calculate),
            (["take a note", "add a note", "make a note"], self.cmd_add_note),
            (["read my notes", "read notes", "my notes"], self.cmd_read_notes),
            (["remind me"], self.cmd_reminder),
            (["open google"], lambda c: self.open_website("Google", "https://www.google.com")),
            (["open youtube"], lambda c: self.open_website("YouTube", "https://www.youtube.com")),
            (["open facebook"], lambda c: self.open_website("Facebook", "https://www.facebook.com")),
            (["open wikipedia"], lambda c: self.open_website("Wikipedia", "https://www.wikipedia.org")),
            (["according to wikipedia", "search wikipedia"], self.cmd_search_wikipedia),
            (["open"], self.cmd_open_app),
        ]

    def handle(self, command):
        """Route a recognized command string to the right handler."""
        if not command:
            return

        command = command.strip().lower()

        if not command:
            return

        for triggers, handler in self.routes:
            if any(self._matches(trigger, command) for trigger in triggers):
                handler(command)
                return

        self.speech.speak(
            "I don't know that command yet. Say 'help' to hear what I can do."
        )

    @staticmethod
    def _matches(trigger, command):
        """Whole-word/phrase matching so short triggers like 'time' don't
        false-positive inside other words (e.g. '6 times 7')."""
        pattern = r"\b" + re.escape(trigger.strip()) + r"\b"
        return re.search(pattern, command) is not None

    # ------------------------------------------------------------------
    # Informational commands
    # ------------------------------------------------------------------

    def cmd_help(self, command=None):
        self.speech.speak(
            "Here is what I can do. "
            "Ask me the time or date. "
            "Ask who I am. "
            "Say open google, youtube, facebook, or wikipedia. "
            "Say search wikipedia for a topic. "
            "Say calculate followed by a math expression. "
            "Say take a note, or read my notes. "
            "Say remind me in a number of minutes to do something. "
            "Say system info for details about this computer. "
            "Say open, followed by an application name, to launch it. "
            "Say change my name if you want me to call you something else. "
            "Say exit, quit, or goodbye to stop."
        )

    def cmd_time(self, command=None):
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        self.speech.speak(f"The time is {current_time}.")

    def cmd_date(self, command=None):
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        self.speech.speak(f"Today is {today}.")

    def cmd_identity(self, command=None):
        self.speech.speak(
            f"I am {config.ASSISTANT_NAME}, your open source voice assistant. "
            f"You are {self.user_name}."
        )

    def cmd_system_info(self, command=None):
        try:
            system = platform.system()
            release = platform.release()
            hostname = socket.gethostname()

            _total, _used, free = shutil.disk_usage("/")
            free_gb = free // (2 ** 30)

            self.speech.speak(
                f"You are running {system} {release} on {hostname}. "
                f"There are {free_gb} gigabytes free on disk."
            )

        except Exception as error:
            print(f"System info error: {error}")
            self.speech.speak("Sorry, I could not read system information.")

    # ------------------------------------------------------------------
    # Websites and applications
    # ------------------------------------------------------------------

    def open_website(self, name, url):
        self.speech.speak(f"Opening {name}.")

        try:
            webbrowser.open(url)
        except Exception as error:
            print(f"Browser error: {error}")
            self.speech.speak(f"Sorry, I could not open {name}.")

    def cmd_open_app(self, command):
        """Handle 'open <application>'.

        config.APPLICATIONS lets you map a friendly spoken phrase (e.g.
        "text editor") to a specific executable (e.g. "gedit"). Anything
        not in that mapping is tried directly as the executable's own
        name — so "open firefox" launches "firefox" if it's installed.

        This is still safe: shutil.which() only matches executables
        already present on the system PATH, and subprocess.Popen is
        called with a list (never shell=True), so no shell string is
        ever interpreted and nothing not already installed can run.
        """
        request = command.replace("open", "", 1).strip()

        if not request:
            self.speech.speak("Which application would you like me to open?")
            return

        # Friendly alias first (e.g. "text editor" -> "gedit"); otherwise
        # treat the spoken words as the executable name itself.
        target = config.APPLICATIONS.get(request, request)

        # Try the name as spoken, then a couple of common variants
        # (people often say "vs code" for the "code" command, etc.).
        candidates = [target, target.replace(" ", "-"), target.replace(" ", "")]
        executable = next((c for c in candidates if shutil.which(c)), None)

        if not executable:
            self.speech.speak(
                f"I couldn't find {request} installed on this system."
            )
            return

        try:
            subprocess.Popen([executable])
            self.speech.speak(f"Opening {request}.")
        except Exception as error:
            print(f"Application launch error: {error}")
            self.speech.speak(f"Sorry, I could not open {request}.")

    # ------------------------------------------------------------------
    # Wikipedia
    # ------------------------------------------------------------------

    def cmd_search_wikipedia(self, command):
        topic = command

        for phrase in ("according to wikipedia", "search wikipedia", "tell me about"):
            topic = topic.replace(phrase, "")

        topic = topic.strip()

        if not topic:
            self.speech.speak("What would you like me to search for?")
            return

        self.speech.speak(f"Searching Wikipedia for {topic}.")

        try:
            try:
                # auto_suggest routes through an older Wikipedia API path
                # that frequently returns malformed JSON and breaks the
                # library. Going straight for the exact title avoids it.
                summary = wikipedia.summary(topic, sentences=2, auto_suggest=False)
            except wikipedia.exceptions.PageError:
                results = wikipedia.search(topic)

                if not results:
                    raise

                summary = wikipedia.summary(results[0], sentences=2, auto_suggest=False)

            if summary:
                self.speech.speak(summary)
            else:
                self.speech.speak(f"I could not find useful information about {topic}.")

        except wikipedia.exceptions.DisambiguationError:
            self.speech.speak(
                f"There are multiple results for {topic}. Please be more specific."
            )

        except wikipedia.exceptions.PageError:
            self.speech.speak(f"I could not find a Wikipedia page for {topic}.")

        except Exception as error:
            print(f"Wikipedia error: {error}")
            self.speech.speak("Sorry, I could not search Wikipedia right now.")

    # ------------------------------------------------------------------
    # Calculator
    # ------------------------------------------------------------------

    _OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def cmd_calculate(self, command):
        expression = command.replace("calculate", "", 1)

        expression = (
            expression.replace("multiplied by", "*")
            .replace("divided by", "/")
            .replace("plus", "+")
            .replace("minus", "-")
            .replace("times", "*")
            .strip()
        )

        if not expression:
            self.speech.speak("What would you like me to calculate?")
            return

        try:
            result = self._safe_eval(expression)
            self.speech.speak(f"That equals {result}.")

        except (ValueError, SyntaxError, ZeroDivisionError, TypeError):
            self.speech.speak(
                "Sorry, I couldn't calculate that. Try something like "
                "'calculate 12 plus 8'."
            )

    def _safe_eval(self, expression):
        """Safely evaluate a basic arithmetic expression without using
        Python's eval(). Only numbers and + - * / % ** are supported,
        so this cannot execute arbitrary code."""
        node = ast.parse(expression, mode="eval").body
        return self._eval_node(node)

    def _eval_node(self, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in self._OPERATORS:
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return self._OPERATORS[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp) and type(node.op) in self._OPERATORS:
            return self._OPERATORS[type(node.op)](self._eval_node(node.operand))

        raise ValueError("Unsupported expression")

    # ------------------------------------------------------------------
    # Notes
    # ------------------------------------------------------------------

    def cmd_add_note(self, command=None):
        self.speech.speak("What should the note say?")
        note = self.speech.listen()

        if not note:
            self.speech.speak("I didn't catch that. Note not saved.")
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        try:
            with open(config.NOTES_FILE, "a", encoding="utf-8") as notes_file:
                notes_file.write(f"[{timestamp}] {note}\n")

            self.speech.speak("Note saved.")

        except OSError as error:
            print(f"Note save error: {error}")
            self.speech.speak("Sorry, I could not save that note.")

    def cmd_read_notes(self, command=None):
        if not os.path.exists(config.NOTES_FILE):
            self.speech.speak("You don't have any notes yet.")
            return

        try:
            with open(config.NOTES_FILE, "r", encoding="utf-8") as notes_file:
                lines = [line.strip() for line in notes_file if line.strip()]

            if not lines:
                self.speech.speak("You don't have any notes yet.")
                return

            self.speech.speak(f"You have {len(lines)} notes. Here are the most recent.")

            for line in lines[-5:]:
                self.speech.speak(line)

        except OSError as error:
            print(f"Note read error: {error}")
            self.speech.speak("Sorry, I could not read your notes.")

    # ------------------------------------------------------------------
    # Reminders
    # ------------------------------------------------------------------

    def cmd_reminder(self, command):
        """Handle 'remind me in <N> minutes to <message>'. Uses a
        background timer so the assistant keeps listening in the
        meantime."""
        digits = "".join(char if char.isdigit() else " " for char in command)
        numbers = digits.split()

        if not numbers:
            self.speech.speak(
                "Please tell me how many minutes, for example "
                "'remind me in 5 minutes to take a break'."
            )
            return

        minutes = int(numbers[0])

        message = command
        for phrase in ("remind me in", "remind me"):
            message = message.replace(phrase, "")

        message = message.replace(numbers[0], "", 1)
        message = message.replace("minutes", "").replace("minute", "")
        message = message.replace("to", "", 1).strip()

        if not message:
            message = "your reminder"

        self.speech.speak(f"Okay, I will remind you in {minutes} minutes.")

        timer = threading.Timer(
            minutes * 60,
            self.speech.speak,
            args=[f"Reminder: {message}"],
        )
        timer.daemon = True
        timer.start()
