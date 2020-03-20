import logging

import pytest

from scripts.generate_pipeline import log_and_exit


@pytest.mark.parametrize("log_level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
def test_log_level(log_level, mocker, logger):
    exit_mock = mocker.patch("builtins.exit", side_effect=None)

    exit_code = 0
    log_message = "TEST"

    log_and_exit(log_level, log_message, exit_code)

    # Tests
    assert len(logger.record_tuples) == 1
    assert logger.record_tuples[0] == ("cli", getattr(logging, log_level), log_message)
    exit_mock.assert_called_with(exit_code)


@pytest.mark.parametrize("exit_code", range(0, 255))
def test_exit_code(exit_code, mocker, logger):
    exit_mock = mocker.patch("builtins.exit", side_effect=None)
    log_message = "TEST"

    log_and_exit("info", log_message, exit_code)

    # Tests
    exit_mock.assert_called_with(exit_code)
    assert len(logger.record_tuples) > 0
