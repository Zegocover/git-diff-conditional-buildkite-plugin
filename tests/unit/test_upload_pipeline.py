import subprocess

import pytest

from CONSTANTS import LOGGER_NAME
from scripts.generate_pipeline import upload_pipeline


@pytest.fixture
def test_pipeline():
    return {"steps": []}


def test_upload_pipeline_sucess(mocker, test_pipeline):
    subprocess_mock = mocker.patch("scripts.generate_pipeline.subprocess.run")

    upload_pipeline(test_pipeline)
    # Tests
    subprocess_mock.assert_called_once_with(
        ['echo "steps: []\n" | buildkite-agent pipeline upload'], shell=True
    )


def test_upload_pipeline_failure(mocker, logger, log_and_exit_mock, test_pipeline):
    # test_command = "Error"
    exit_code = 1
    subprocess_mock = mocker.patch(
        "scripts.generate_pipeline.subprocess.run",
        side_effect=subprocess.CalledProcessError(exit_code, "boom"),
    )

    upload_pipeline(test_pipeline)

    # Tests
    subprocess_mock.assert_called_once_with(
        ['echo "steps: []\n" | buildkite-agent pipeline upload'], shell=True
    )
    assert logger.record_tuples == [
        (LOGGER_NAME, 10, "Command 'boom' returned non-zero exit status 1.")
    ]
    log_and_exit_mock.assert_called_once_with("error", "Error uploading pipeline", 1)
