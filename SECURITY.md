# Security Policy

OpenVox is a local, offline-first desktop voice assistant. It does not
handle passwords, payment information, or user accounts. Voice audio is
sent only to Google's speech recognition API for transcription (via the
`SpeechRecognition` library) and is not stored by OpenVox itself.

## Reporting a Vulnerability

If you discover a security issue (for example, a way that a voice
command could execute unintended system commands, or a dependency with
a known vulnerability), please open a GitHub issue with the label
`security`, or contact the maintainer directly if the issue is
sensitive. Please include:

- A description of the issue
- Steps to reproduce it
- The potential impact

We will do our best to respond promptly and release a fix.

## Scope Notes

- The `open <application>` command will launch any executable that is
  already installed and present on the system `PATH` (found via
  `shutil.which`), using `subprocess.Popen` with an argument list —
  never `shell=True` and never a raw shell string. This means it can
  only start programs already installed by the user; it cannot execute
  arbitrary shell commands, chained commands, or anything not already
  a real executable on disk. `config.APPLICATIONS` additionally lets
  you map a friendly spoken phrase (e.g. "text editor") to a specific
  executable name.
- The `calculate` command evaluates expressions using Python's `ast`
  module with a fixed whitelist of arithmetic operators, not `eval()`,
  so it cannot execute arbitrary code.
