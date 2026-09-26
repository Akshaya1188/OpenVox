"""
Pytest configuration.

The openvox/ package uses flat imports (e.g. `import config`,
`from core.speech import SpeechEngine`) rather than package-relative
imports, matching how main.py is run directly. This adds the openvox/
directory to sys.path so tests can import those modules the same way.
"""

import os
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)
OPENVOX_DIR = os.path.join(PROJECT_ROOT, "openvox")

if OPENVOX_DIR not in sys.path:
    sys.path.insert(0, OPENVOX_DIR)
