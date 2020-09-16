import pytest

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

    # Tests
    assert result == expected_result
    open_mock.assert_called_once_with(".git_diff_conditional/git_diff", "r")


def test_get_diff_no_file(mocker, log_and_exit_mock):
    open_mock = mocker.patch(
        "scripts.generate_pipeline.open", side_effect=FileNotFoundError
    )

    result = get_diff()

    # Tests
    assert result is None
    open_mock.assert_called_once_with(".git_diff_conditional/git_diff", "r")
    log_and_exit_mock.assert_called_once_with(
        "error", "Error getting diff from file", 1
    )
