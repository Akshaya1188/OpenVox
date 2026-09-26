# Roadmap

This file exists so this project can be paused for weeks, months, or
years and picked back up without having to reconstruct context from
memory. If you're reading this after a long break: welcome back. Start
at "Where things stand" below.

## Where things stand (v0.1.0)

OpenVox is a working, tested, locally-run voice assistant:

- Speech in/out via `SpeechRecognition` (Google's free endpoint) and
  `pyttsx3`.
- Keyword/phrase-based command routing (see `core/commands.py`).
- Name is asked once and persisted to `data/profile.json`.
- 34 passing tests, none of which require a microphone.

**Known limitation, by design, not yet fixed:** command matching is
plain keyword/phrase routing, not real intent understanding. It works
for the phrasing it was written for and nothing else. This is the
single biggest thing to fix next — see "Next milestone" below.

## Why development paused here

Not a dead end — a deliberate stopping point after getting a solid,
tested, honestly-scoped v1 shipped. The next milestone is a genuine
architecture change (see below) that deserves focused time rather than
being squeezed in.

## Next milestone: v0.2 — real intent understanding

**Goal:** replace the keyword routing table in `CommandHandler` with an
LLM tool-use call, so commands are matched by *meaning* instead of
exact phrasing.

**Why this first, above everything else in this file:** it fixes an
entire class of bugs at once (the "6 times 7" vs. "what time" bug we
hit was a symptom of keyword matching, not a one-off), and it's the
change that makes this project meaningfully different from the many
other beginner voice-assistant clones on GitHub, rather than just
having more features than them.

**How, concretely:**
1. Keep `SpeechEngine.speak()` / `.listen()` exactly as they are — this
   change is isolated to `CommandHandler`.
2. Define the existing commands (`get_time`, `search_wikipedia`,
   `open_app`, `calculate`, etc.) as tool schemas for the Anthropic API
   (or another LLM with tool use).
3. Send the transcribed text to the model with those tools available;
   let it choose which function to call and with what arguments,
   instead of `if "time" in command`.
4. Fall back to today's keyword routing if the API call fails (offline,
   rate-limited, no key configured) — this keeps OpenVox usable
   without a paid API key, which matters for an open-source project.
5. Update tests: mock the API response instead of testing exact
   trigger strings.

**Estimated effort:** 1–2 focused evenings, not a redesign of the rest
of the app.

## Alternative next milestone (pick one, not both)

**Offline speech recognition** — replace the Google free endpoint
(unofficial, can disappear or rate-limit at any time) with Vosk or
faster-whisper, so OpenVox works with no internet dependency at all.
This is a different skill (audio/ML pipeline) than the LLM-routing
option above. Only pick this instead if that's specifically what you
want to learn next — don't do both in the same milestone.

## After v0.2: plugin architecture

Once command routing is no longer one giant `if/elif` (or one big tool
list), split `core/commands.py` into a `commands/` directory where each
command is its own file, auto-discovered at startup. This is the
change that lets the project grow without `CommandHandler` becoming
unreadable, and it's a legitimate "designed for extensibility" talking
point.

## Cheap, parallel improvements (do anytime, low effort)

- [ ] GitHub Actions workflow to run `pytest` on every push
- [ ] Tag releases (`v0.1.0`, `v0.2.0`, ...) instead of only pushing to `main`
- [ ] Keep a `CHANGELOG.md` alongside version tags
- [ ] Revisit `config.APPLICATIONS` and `EXIT_COMMANDS` as real usage surfaces gaps

## Explicitly deprioritized (don't do these instead of the above)

- More surface-level commands (weather, more websites, more note
  features) — doesn't address the core limitation, just makes the
  keyword router bigger.
- A GUI — doesn't fix intent understanding, and is a lot of effort for
  a beginner for something that isn't the project's weak point.
- Rewriting in a different framework/language "to modernize" —
  architecture is fine as-is; the routing logic is the actual weak
  point, and a rewrite doesn't fix that on its own.

## Notes to future-me on dependencies

- `wikipedia` (PyPI package) is unmaintained and has a known bug where
  `auto_suggest` hits a broken API path (`Expecting value: line 1
  column 1`). Already worked around in `cmd_search_wikipedia` by using
  `auto_suggest=False` with a manual search fallback. If this breaks
  again, check whether Wikipedia's REST API
  (`/api/rest_v1/page/summary/<title>`) is a more reliable replacement.
- `recognize_google()` in `SpeechRecognition` is an unofficial,
  undocumented free endpoint. It can be rate-limited or removed without
  notice. This is the strongest argument for the offline-STT milestone
  above, whenever it happens.
