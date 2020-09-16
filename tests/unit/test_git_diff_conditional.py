import pytest
from CONSTANTS import LOGGER_NAME, PLUGIN_PREFIX

from scripts.generate_pipeline import GitDiffConditional

# Fixtures


@pytest.fixture(scope="module")
def file_name_env_var_suffix():
    return "PIPELINE_FILE"


@pytest.fixture(scope="module")
def file_name():
    return "pipeline.yml"


@pytest.fixture(autouse=True)
def put_env_var(monkeypatch, file_name_env_var_suffix, file_name):
    monkeypatch.setenv(f"{PLUGIN_PREFIX}_{file_name_env_var_suffix}", file_name)


@pytest.fixture(scope="function")
def git_diff_conditional():
    return GitDiffConditional([], PLUGIN_PREFIX)


#
# Class GitDiffConditional Method load_dynamic_pipeline tests
#


def test_load_dynamic_pipeline_success(
    mocker, file_name_env_var_suffix, git_diff_conditional, logger
):
    file_name_env_var = f"{PLUGIN_PREFIX}_{file_name_env_var_suffix}"
    open_mock = mocker.patch(
        "scripts.generate_pipeline.open",
        mocker.mock_open(
            read_data="""
steps:
  - label: test
    queue: test
"""
        ),
    )

    result = git_diff_conditional.load_dynamic_pipeline(file_name_env_var_suffix)

    # Tests

    assert result == {"steps": [{"label": "test", "queue": "test"}]}

    open_mock.assert_called_once_with("pipeline.yml", "r")
    assert logger.record_tuples == [
        (LOGGER_NAME, 20, f"Checking env var: {file_name_env_var} for file name")
    ]


def test_load_dynamic_pipeline_file_not_found(
    mocker, log_and_exit_mock, file_name_env_var_suffix, git_diff_conditional, logger
):
    file_name_env_var = f"{PLUGIN_PREFIX}_{file_name_env_var_suffix}"

    open_mock = mocker.patch(
        "scripts.generate_pipeline.open", side_effect=FileNotFoundError
    )
    yaml_load_patch = mocker.patch("scripts.generate_pipeline.yaml.safe_load")

    result = git_diff_conditional.load_dynamic_pipeline(file_name_env_var_suffix)

    # Tests

    assert result is None

    open_mock.assert_called_once_with("pipeline.yml", "r")
    yaml_load_patch.assert_not_called()
    assert logger.record_tuples == [
        (LOGGER_NAME, 20, f"Checking env var: {file_name_env_var} for file name"),
        (LOGGER_NAME, 40, ""),
    ]
    log_and_exit_mock.assert_called_once_with(
        "error", "File Name: (pipeline.yml) Not Found", 1
    )


def test_load_dynamic_pipeline_bad_yaml(
    mocker, log_and_exit_mock, file_name_env_var_suffix, git_diff_conditional, logger
):
    file_name_env_var = f"{PLUGIN_PREFIX}_{file_name_env_var_suffix}"
    open_mock = mocker.patch(
        "scripts.generate_pipeline.open", mocker.mock_open(read_data="bad_yaml: - :")
    )

    result = git_diff_conditional.load_dynamic_pipeline(file_name_env_var_suffix)

    # Tests
    assert result is None

    open_mock.assert_called_once_with("pipeline.yml", "r")
    assert logger.record_tuples == [
        (LOGGER_NAME, 20, f"Checking env var: {file_name_env_var} for file name"),
        (LOGGER_NAME, 40, "Invalid YAML in File: pipeline.yml"),
    ]


#
# Class GitDiffConditional Method generate_skip tests
#


def test_generate_skip_empty(logger, git_diff_conditional):
    label = "test"

    result = git_diff_conditional.generate_skip(label, [], [])

    # Tests
    assert not result
    assert logger.record_tuples == [
        (LOGGER_NAME, 30, f"label ({label}) passed in but no skip settings configured")
    ]


#
# Class GitDiffConditional Method load_conditions_from_environment tests
#


@pytest.mark.parametrize(
    "pipeline_as_env,diff,expected_result",
    [
        (  # Test only one label with include
            {"0_LABEL": "test_1", "0_INCLUDE": "terraform/*.tf"},
            ["terraform/main.tf"],
            {"test_1": False},
        ),
        (  # Test only one label with exclude
            {"0_LABEL": "test_2", "0_EXCLUDE": "folder/**"},
            ["folder/file"],
            {"test_2": True},
        ),
        (  # Test two labels with include/exclude
            {
                "0_LABEL": "test_3",
                "0_INCLUDE": "**/file_0",
                "1_LABEL": "test_3_other",
                "1_EXCLUDE": "**/*_1",
            },
            ["folder_a/file_0", "folder_b/.folder/file_2"],
            {"test_3": False, "test_3_other": False},
        ),
        ({}, ["file.py"], {}),  # Test with no vars passed
        (
            {"0_LABEL": "test_4", "0_INCLUDE": "file.py"},
            [],
            {"test_4": True},
        ),  # Test with no diff
        (
            {"0_LABEL": "test_5", "0_INCLUDE": "*"},
            ["file.py", "folder/file.tf"],
            {"test_5": False},
        ),  # Test with always include if diff
    ],
)
def test_load_conditions_from_environment(
    monkeypatch,
    git_diff_conditional,
    pipeline_as_env,
    diff,
    expected_result,
):

    for key, value in pipeline_as_env.items():
        monkeypatch.setenv(f"{PLUGIN_PREFIX}_STEPS_{key}", value)

    git_diff_conditional = GitDiffConditional(diff, PLUGIN_PREFIX)
    conditions = git_diff_conditional.load_conditions_from_environment()

    # Tests
    assert conditions == expected_result


#
# Class GitDiffConditional Method generate_pipeline_from_conditions tests
#


@pytest.mark.parametrize(
    "dynamic_steps,conditions,result_steps",
    [
        (
            [{"label": "test_0"}],
            {"test_0": True},
            [{"label": "test_0", "skip": True}],
        ),  # skip True
        (
            [{"label": "test_1"}],
            {"test_1": False},
            [{"label": "test_1", "skip": False}],
        ),  # skip False
        ([], {"test": True}, []),  # no dynamic_pipeline
        (
            [{"label": "test_3"}, {"label": "test_3_a"}],
            {"test_3": True},
            [{"label": "test_3", "skip": True}, {"label": "test_3_a", "skip": False}],
        ),  # skip true/false
        (
            [{"label": "test_4_label"}, {"block": "test_4_block"}],
            {"test_4_label": True, "test_4_block": True},
            [
                {"label": "test_4_label", "skip": True},
                {"block": "test_4_block", "skip": True},
            ],
        ),  # Check label and block
    ],
)
def test_generate_pipeline_from_conditions(
    logger, git_diff_conditional, dynamic_steps, conditions, result_steps
):
    dynamic_pipeline = {"steps": dynamic_steps}
    result = git_diff_conditional.generate_pipeline_from_conditions(
        dynamic_pipeline, conditions
    )

    # Tests
    assert result == {"steps": result_steps}


def test_generate_pipeline_from_conditions_with_skip_in_step(
    logger, git_diff_conditional
):
    dynamic_pipeline = {"steps": [{"label": "already contains skip", "skip": False}]}
    conditions = {}

    result = git_diff_conditional.generate_pipeline_from_conditions(
        dynamic_pipeline, conditions
    )

    # Tests
    assert result == {"steps": [{"label": "already contains skip", "skip": False}]}
    assert logger.record_tuples == [
        ("cli", 30, "label (already contains skip) already has a skip key")
    ]
