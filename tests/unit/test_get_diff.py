import subprocess

from CONSTANTS import PLUGIN_PREFIX
from scripts.generate_pipeline import get_diff, run_command

#
# function run_command tests
#


def test_run_command_success(mocker, logger):
    """
    This checks that the correct amount of files are returned based on the directory
    """

    subprocess_return_value = """test.py
        folder_a/test.tf
        folder_a/folder_b/test.txt"""

    subprocess_mock = mocker.patch("subprocess.run")

    test_command = "git diff"
    subprocess_mock.return_value = mocker.Mock(
        stdout=bytes(subprocess_return_value, "UTF-8")
    )

    result = run_command(test_command)

    # Tests
    assert result == list(
        subprocess_return_value.replace(" ", "").strip("\t").split("\n")
    )
    assert logger.record_tuples == [
        ("cli", 20, f"Getting git diff using: ({test_command})")
    ]
    subprocess_mock.assert_called_once_with(
        test_command, check=True, stdout=-1, shell=True
    )


def test_run_command_returns_empty_list(mocker, logger):
    """
    Checks that an empty list is returned if git diff has no diff
    """

    subprocess_return_value = ""

    subprocess_mock = mocker.patch("subprocess.run")

    test_command = "NO DIFF"
    subprocess_mock.return_value = mocker.Mock(
        stdout=bytes(subprocess_return_value, "UTF-8")
    )

    result = run_command(test_command)

    # Tests
    assert isinstance(result, list)
    assert len(result) == 0
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
    run_command_mock = mocker.patch(
        "scripts.generate_pipeline.run_command", return_value=[]
    )

    result = get_diff(PLUGIN_PREFIX)

    # Tests
    run_command_mock.assert_has_calls(
        [mocker.call("git diff --name-only origin/master...HEAD")], any_order=True
    )
    assert result == run_command_mock.return_value
