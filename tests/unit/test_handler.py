import pytest

from CONSTANTS import LOGGER_NAME, PLUGIN_PREFIX
from scripts.generate_pipeline import GitDiffConditional, get_diff, handler


# Mocks
@pytest.fixture
def get_diff_mock(mocker):
    return mocker.patch("scripts.generate_pipeline.get_diff", return_value=[])


# Tests
def setup_git_diff_conditional_mock(mocker, condition_return_value):

    return_value = mocker.MagicMock(
        spec=GitDiffConditional,
        load_dynamic_pipeline=mocker.Mock(return_value={}),
        load_conditions_from_environment=mocker.Mock(return_value={}),
        generate_pipeline_from_conditions=mocker.Mock(
            return_value=condition_return_value
        ),
    )

    return mocker.patch(
        "scripts.generate_pipeline.GitDiffConditional", return_value=return_value
    )


def test_handler_empty_steps(
    mocker, monkeypatch, logger, log_and_exit_mock, get_diff_mock
):
    monkeypatch.setenv(f"{PLUGIN_PREFIX}_LOG_LEVEL", "DEBUG")

    open_mock = mocker.patch("scripts.generate_pipeline.open", mocker.mock_open())

    git_diff_conditional_mock = setup_git_diff_conditional_mock(mocker, {"steps": []})

    handler()

    # Tests
    assert logger.record_tuples == []
    get_diff_mock.assert_called_once_with()
    git_diff_conditional_mock.assert_called_once_with(
        get_diff_mock.return_value, PLUGIN_PREFIX
    )
    log_and_exit_mock.assert_called_once_with(
        "info", "No pipeline generated for diff: ([])", 0
    )


def test_handler_with_steps(
    mocker, monkeypatch, logger, log_and_exit_mock, get_diff_mock
):
    monkeypatch.setenv(f"{PLUGIN_PREFIX}_LOG_LEVEL", "DEBUG")

    open_mock = mocker.patch("scripts.generate_pipeline.open", mocker.mock_open())
    git_diff_conditional_mock = setup_git_diff_conditional_mock(
        mocker, {"steps": [{"label": "test"}]}
    )

    handler()

    # Tests
    assert logger.record_tuples == [
        ("cli", 20, "Dynamic pipeline generated, saving for agent upload")
    ]
    get_diff_mock.assert_called_once_with()
    git_diff_conditional_mock.assert_called_once_with(
        get_diff_mock.return_value, PLUGIN_PREFIX
    )
    open_mock.assert_called_once_with(".git_diff_conditional/pipeline_output", "w")
    log_and_exit_mock.assert_not_called()

    return None


def test_handler_error_saving_pipeline(
    mocker, monkeypatch, logger, log_and_exit_mock, get_diff_mock
):
    monkeypatch.setenv(f"{PLUGIN_PREFIX}_LOG_LEVEL", "DEBUG")

    open_mock = mocker.patch("scripts.generate_pipeline.open", side_effect=Exception)

    git_diff_conditional_mock = setup_git_diff_conditional_mock(
        mocker, {"steps": [{"label": "test"}]}
    )

    handler()

    # Tests
    assert logger.record_tuples == [
        ("cli", 20, "Dynamic pipeline generated, saving for agent upload")
    ]
    get_diff_mock.assert_called_once_with()
    git_diff_conditional_mock.assert_called_once_with(
        get_diff_mock.return_value, PLUGIN_PREFIX
    )
    open_mock.assert_called_once_with(".git_diff_conditional/pipeline_output", "w")
    log_and_exit_mock.assert_called_once_with(
        "error", "error saving pipeline to disk", 1
    )
