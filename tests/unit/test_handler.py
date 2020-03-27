import pytest

from CONSTANTS import LOGGER_NAME, PLUGIN_PREFIX
from scripts.generate_pipeline import GitDiffConditional, get_diff, handler


# Tests
def test_handler_disable_plugin(monkeypatch, logger, mocker):
    monkeypatch.setenv(f"{PLUGIN_PREFIX}_DISABLE_PLUGIN", "true")
    monkeypatch.setenv(f"{PLUGIN_PREFIX}_LOG_LEVEL", "DEBUG")

    get_diff_mock = mocker.patch("scripts.generate_pipeline.get_diff", return_value=[])
    upload_mock = mocker.patch("scripts.generate_pipeline.upload_pipeline")

    return_value = mocker.MagicMock(
        spec=GitDiffConditional, load_dynamic_pipeline=mocker.Mock(return_value={})
    )

    git_diff_conditional_mock = mocker.patch(
        "scripts.generate_pipeline.GitDiffConditional", return_value=return_value
    )

    handler()

    # Tests
    assert logger.record_tuples == [
        (
            LOGGER_NAME,
            30,
            "Plugin disable flag detected, passing entire pipeline to buildkite",
        )
    ]
    upload_mock.assert_called_once_with({})
    get_diff_mock.assert_called_once_with(PLUGIN_PREFIX)
    git_diff_conditional_mock.assert_called_once_with(
        get_diff_mock.return_value, PLUGIN_PREFIX
    )


def test_handler_empty_steps(mocker, monkeypatch, logger, log_and_exit_mock):
    monkeypatch.setenv(f"{PLUGIN_PREFIX}_LOG_LEVEL", "DEBUG")

    get_diff_mock = mocker.patch("scripts.generate_pipeline.get_diff", return_value=[])
    upload_mock = mocker.patch("scripts.generate_pipeline.upload_pipeline")

    return_value = mocker.MagicMock(
        spec=GitDiffConditional,
        load_dynamic_pipeline=mocker.Mock(return_value={}),
        load_conditions_from_environment=mocker.Mock(return_value={}),
        generate_pipeline_from_conditions=mocker.Mock(return_value={"steps": []}),
    )

    git_diff_conditional_mock = mocker.patch(
        "scripts.generate_pipeline.GitDiffConditional", return_value=return_value
    )

    handler()

    # Tests
    assert logger.record_tuples == []
    get_diff_mock.assert_called_once_with(PLUGIN_PREFIX)
    git_diff_conditional_mock.assert_called_once_with(
        get_diff_mock.return_value, PLUGIN_PREFIX
    )
    log_and_exit_mock.assert_called_once_with(
        "info", "No pipeline generated for diff: ([])", 0
    )
