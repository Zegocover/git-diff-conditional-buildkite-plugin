"""Place fixtures in this file for use across all test files"""
import pytest


@pytest.fixture(scope="function")
def logger(caplog):
    caplog.set_level("DEBUG")
    return caplog


@pytest.fixture
def log_and_exit_mock(mocker):
    return mocker.patch("scripts.generate_pipeline.log_and_exit")
