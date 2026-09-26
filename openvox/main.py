"""
Entry point for OpenVox.

Run with (from inside the openvox/ directory):
    python main.py
"""

from core.assistant import Assistant


def main():
    assistant = Assistant()
    assistant.run()


if __name__ == "__main__":
    main()
