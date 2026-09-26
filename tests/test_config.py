"""Tests for config.py — mostly sanity checks on defaults and paths."""

import os

import config


def test_assistant_name_is_set():
    assert config.ASSISTANT_NAME


def test_exit_commands_contains_common_words():
    assert "exit" in config.EXIT_COMMANDS
    assert "quit" in config.EXIT_COMMANDS
    assert "goodbye" in config.EXIT_COMMANDS


def test_data_and_log_dirs_exist():
    assert os.path.isdir(config.DATA_DIR)
    assert os.path.isdir(config.LOG_DIR)


def test_microphone_device_index_is_int():
    assert isinstance(config.MICROPHONE_DEVICE_INDEX, int)


def test_applications_whitelist_is_a_dict_of_strings():
    assert isinstance(config.APPLICATIONS, dict)
    for phrase, executable in config.APPLICATIONS.items():
        assert isinstance(phrase, str)
        assert isinstance(executable, str)
