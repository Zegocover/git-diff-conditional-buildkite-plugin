import subprocess
import pytest
from CONSTANTS import PLUGIN_PREFIX
from scripts.generate_pipeline import get_diff, run_command

#
# function run_command tests
#


@pytest.mark.parametrize("subprocess_return_value,expected_result", [("""test.py
        folder_a/test.tf
        folder_a/folder_b/test.txt""", ["test.py", "folder_a/test.tf", "folder_a/folder_b/test.txt"]), ("", [])])
def test_run_command(mocker, logger, subprocess_return_value, expected_result):
    """
    Checks that the expected_result is returned given an expected input
    """

    subprocess_mock = mocker.patch("scripts.generate_pipeline.subprocess.run")

    test_command = "git diff"
    subprocess_mock.return_value = mocker.Mock(
        stdout=bytes(subprocess_return_value, "UTF-8")
    )

    result = run_command(test_command)

    # Tests
    assert result == expected_result
    assert logger.record_tuples == [
        ("cli", 20, f"Getting git diff using: ({test_command})")
    ]
    subprocess_mock.assert_called_once_with(
        test_command, check=True, stdout=-1, shell=True
    )


def test_run_command_raises_error(mocker, logger, log_and_exit_mock):
    test_command = "Error"
    exit_code = 1
    subprocess_mock = mocker.patch(
        "subprocess.run",
        side_effect=subprocess.CalledProcessError(exit_code, test_command),
    )

    result = run_command(test_command)

    # Tests
    assert result is None
    assert logger.record_tuples == [
        ("cli", 20, f"Getting git diff using: ({test_command})"),
        ("cli", 10, f"Command '{test_command}' returned non-zero exit status 1."),
    ]
    subprocess_mock.assert_called_once_with(
        test_command, check=True, stdout=subprocess.PIPE, shell=True
    )
    log_and_exit_mock.assert_called_once_with(
        "error", f"Error getting diff using command: {test_command}", exit_code
    )


#
# function get_diff tests
#


def test_get_diff(mocker):
    run_command_mock = mocker.patch(
        "scripts.generate_pipeline.run_command", return_value=["diff.py"]
    )

    result = get_diff(PLUGIN_PREFIX)

    # Tests
    run_command_mock.assert_called_once_with(
        "git diff --name-only origin/master...HEAD"
    )
    assert result == run_command_mock.return_value


def test_get_diff_custom(monkeypatch, mocker):
    "Test that run_command is called with the passed custom git diff command"

    custom_diff_command = "custom diff command"
    monkeypatch.setenv(f"{PLUGIN_PREFIX}_DIFF", custom_diff_command)
    run_command_mock = mocker.patch(
        "scripts.generate_pipeline.run_command", return_value=["diff.py"]
    )

    result = get_diff(PLUGIN_PREFIX)

    # Tests
    run_command_mock.assert_called_once_with(custom_diff_command)
    assert result == run_command_mock.return_value


def test_get_diff_no_diff(mocker):
    "Test that run_command is called twice with both default commands"

    run_command_mock = mocker.patch(
        "scripts.generate_pipeline.run_command", return_value=[]
    )

    result = get_diff(PLUGIN_PREFIX)

    # Tests
    run_command_mock.assert_has_calls(
        [mocker.call("git diff --name-only origin/master...HEAD"), mocker.call("git diff --name-only HEAD HEAD~1")], any_order=False
    )
    assert result == run_command_mock.return_value
