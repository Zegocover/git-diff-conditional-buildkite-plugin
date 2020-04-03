import subprocess

import pytest

from CONSTANTS import PLUGIN_PREFIX
from scripts.generate_pipeline import get_diff

#
# function get_diff tests
#


@pytest.mark.parametrize(
    "file_contents,expected_result",
    [
        (
            """test.py
        folder_a/test.tf
        folder_a/folder_b/test.txt""",
            ["test.py", "folder_a/test.tf", "folder_a/folder_b/test.txt"],
        ),  # Diff present
        ("\n", []),  # No Diff
    ],
)
def test_get_diff(mocker, file_contents, expected_result):
    open_mock = mocker.patch(
        "scripts.generate_pipeline.open", mocker.mock_open(read_data=file_contents)
    )

    result = get_diff()
    assert result == expected_result


def test_get_diff_no_file(mocker, log_and_exit_mock):
    open_mock = mocker.patch(
        "scripts.generate_pipeline.open", side_effect=FileNotFoundError
    )

    result = get_diff()
    assert result is None
    log_and_exit_mock.assert_called_once_with(
        "error", "Error getting diff from file", 1
    )
