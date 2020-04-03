#!/usr/bin/env python3

import logging
import os
import re
import subprocess
import sys
from fnmatch import fnmatch

import yaml
from yaml.scanner import ScannerError

# Setup logging
logging.basicConfig(format="%(levelname)s %(message)s")
LOG = logging.getLogger("cli")


def log_and_exit(log_level: str, log_message: str, exit_code: int) -> None:
    """Handles the log_message and exit_code"""
    logger = getattr(LOG, log_level.lower())
    logger(log_message)
    sys.exit(exit_code)


class GitDiffConditional:
    """The class to generate the pipeline from environment variables"""

    def __init__(self, diff, plugin_prefix):
        self.diff = diff
        self.plugin_prefix = plugin_prefix

    def load_dynamic_pipeline(self, env_var_suffix: str) -> dict:
        """Load the pipeline from the given file_name

        Returns:
            dict: Contains the buildkite pipeline
        """
        env_var = f"{self.plugin_prefix}_{env_var_suffix}"

        LOG.info("Checking env var: %s for file name", env_var)

        pipeline_file_name = os.environ[env_var]

        try:
            with open(pipeline_file_name, "r") as stream:
                pipeline = yaml.safe_load(stream)
        except FileNotFoundError as e:
            LOG.error(e)
            log_and_exit("error", f"File Name: ({pipeline_file_name}) Not Found", 1)
        except ScannerError:
            LOG.error("Invalid YAML in File: %s", pipeline_file_name)
        else:
            return pipeline

    def load_conditions_from_environment(self) -> dict:
        """Loads the defined conditions from the environment variables
        """
        regex = re.compile(f"{self.plugin_prefix}_STEPS_[0-9]*_LABEL")
        step_labels = {k: v for k, v in os.environ.items() if re.search(regex, k)}

        conditions = {}

        for key, label in step_labels.items():
            LOG.debug("Checking %s", key)

            step_conditions = {}
            step_number = key.replace(f"{self.plugin_prefix}_STEPS_", "").replace(
                "_LABEL", ""
            )
            for option in ["INCLUDE", "EXCLUDE"]:
                LOG.debug("Checking %s", option)

                step_regex = re.compile(
                    f"{self.plugin_prefix}_STEPS_{step_number}_{option}"
                )

                patterns = [
                    v for k, v in os.environ.items() if re.search(step_regex, k)
                ]

                LOG.debug("Found patterns: (%s)", patterns)
                step_conditions[option] = patterns

            if step_conditions:
                conditions[label] = self.generate_skip(
                    label, step_conditions["INCLUDE"], step_conditions["EXCLUDE"]
                )

        return conditions

    def generate_skip(self, label: str, include: list, exclude: list) -> bool:
        skip = False
        if not include and not exclude:
            LOG.warning("label (%s) passed in but no skip settings configured", label)
            pass
        elif exclude:
            # Should skip the step (exclude is stronger than include)
            skip = self.pattern_match(exclude)
        elif include:
            # Should include the step
            skip = not self.pattern_match(include)

        return skip

    def pattern_match(self, patterns: list) -> bool:
        result = False

        for pattern in patterns:
            if any(fnmatch(_file, pattern) for _file in self.diff):
                result = True
                break

        return result

    def generate_pipeline_from_conditions(
        self, dynamic_pipeline: dict, conditions: dict
    ) -> dict:
        """Generate the pipeline based on logic held in the origial file

        Returns:
            dict: Contains the steps for the pipeline
        """
        pipeline = {"steps": []}

        for step in dynamic_pipeline["steps"]:
            if isinstance(step, dict):
                # Only check for actual steps, not waits
                step["skip"] = self.check_if_skip(conditions, step)

            # Always put the step back onto the pipeline even if it is skipped
            pipeline["steps"].append(step)

        return pipeline

    @staticmethod
    def check_if_skip(conditional_steps: dict, step: dict) -> bool:
        label = step["label"] if "label" in step else step["block"]

        if "skip" in step:
            # Skip setings already exist
            LOG.warning("label (%s) already has a skip key", label)
            return step["skip"]

        if label not in conditional_steps:
            LOG.warning("No Conditions set for label (%s)", label)
            return False

        return conditional_steps[label]


def get_diff():
    try:
        with open(".git_diff_conditional/git_diff", "r") as _fp:
            diff = [_file.strip() for _file in _fp.readlines() if _file.strip() != ""]
    except FileNotFoundError:
        log_and_exit("error", "Error getting diff from file", 1)
    else:
        return diff


def handler():
    # Setup Defaults
    plugin_prefix = "BUILDKITE_PLUGIN_GIT_DIFF_CONDITIONAL"

    log_level = os.getenv(f"{plugin_prefix}_LOG_LEVEL", "INFO")
    LOG.setLevel(log_level)

    # Get the git diff
    diff = get_diff()

    # Instantiate the Class
    git_diff_conditions = GitDiffConditional(diff, plugin_prefix)

    # Get the dynamic_pipeline
    dynamic_pipeline = git_diff_conditions.load_dynamic_pipeline("DYNAMIC_PIPELINE")

    # Get the conditions
    conditions = git_diff_conditions.load_conditions_from_environment()

    # Generate the pipeline
    pipeline = git_diff_conditions.generate_pipeline_from_conditions(
        dynamic_pipeline, conditions
    )

    if not pipeline["steps"]:
        log_and_exit("info", f"No pipeline generated for diff: ({diff})", 0)
    else:
        LOG.info("Dynamic pipeline generated, saving for agent upload")

        try:
            with open(".git_diff_conditional/pipeline_output", "w") as _fp:
                yaml.dump(pipeline, _fp, default_flow_style=False)
        except Exception:
            log_and_exit("error", "error saving pipeline to disk", 1)


if __name__ == "__main__":
    handler()
