# git-diff-conditional-buildkite-plugin

![Github Actions: CI](https://github.com/Zegocover/git-diff-conditional-buildkite-plugin/workflows/CI/badge.svg)

This plugin can be used to create a dynamic pipeline based on your `git diff`. This requires TWO pipeline files in total and uses `docker` to run the plugin:

- `initial_pipeline` - The one that tells buildkite to load the plugin
- `dynamic_pipeline` - The pipeline which you want to run, but have steps skipped based on conditions held in the `initial`

But what about [mono-repo-diff](https://github.com/chronotc/monorepo-diff-buildkite-plugin), it is designed to spin up multiple pipelines based on your `git diff`. The purpose of this plugin is to spin up a single pipeline based on your `git diff`. For another similar concept check out the gitlab plugin [onlychangesexceptchanges](https://docs.gitlab.com/ee/ci/yaml/#onlychangesexceptchanges)

## Getting Started

Please see the below examples on how to use this plugin with buildkite. The [buildkite-agent](https://buildkite.com/docs/agent/v3) also requires access to `docker`.

### Example

`initial_pipeline`
```yaml
steps:
  - label: ":partyparrot: Creating the pipeline"
    plugins:
      - ssh://git@github.com/Zegocover/git-diff-conditional-buildkite-plugin#v1.0.0:
          dynamic_pipeline: ".buildkite/dynamic_pipeline.yml"
          steps:
            - label: "build and deploy lambda"
              include:
                - "function_code/*"
```

`dynamic_pipeline`
```yaml
steps:
  - label: "build and deploy lambda"
    commands:
      - make lambda
    agents:
      queue: awesome
    timeout_in_minutes: 10

  - wait

  - label: "terraform apply"
    commands:
      - terraform apply
    agents:
      queue: awesome
    timeout_in_minutes: 10
```

The above example `initial_pipeline` will skip the `build and deploy lambda` step unless there has been a change to the `function_code` directory. Everything else in the `dynamic_pipeline` file will be left intact and passed through to buildkite. It is possible to configure numerous `label` fields, using the configuration options below.


## Configuration

| Option           | Required |   Type    | Default | Description                                                                                                                                     |
| ---------------- | :------: | :-------: | :-----: | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| dynamic_pipeline |   Yes    | `string`  |         | The name including the path to the pipeline that contains all the actual `steps`                                                                |
| disable_plugin   |    No    | `boolean` | `false` | This can be used to pass the entire `dynamic_pipeline` pipeline straight to buildkite without skipping a single step.                           |
| diff             |    No    | `string`  |         | Can be used to override the default commands (see below for a better explanation of the defaults)                                               |
| log_level        |    No    | `string`  | `INFO`  | The Level of logging to be used by the python script underneath. Pass `DEBUG` for verbose logging if errors occur                               |
| steps            |   Yes    |  `array`  |         | Each Step should contain a `label` with the `include`/`exclude` settings relevant to the label it applies to within the `dynamic_pipeline` file |
| label            |   Yes    | `string`  |         | The `label` these conditions apply to within the `dynamic_pipeline` file. (These should be an EXACT match)                                      |
| include          |    No    |  `array`  |         | If any element is found within the `git diff` then this step will NOT be skipped                                                                |
| exclude          |    No    |  `array`  |         | If any alement is found within the `git diff` then this step will be SKIPPED                                                                    |

Other useful things to note:
- Both `include` and `exclude` make use of Unix shell-style wildcards (Look at `.gitignore` files for inspiration)
- Every `label` defined within the `initial_pipeline` should contain `include`, `exclude` or both

### `diff` command

The default `diff` commands are (run in the order shown):

```bash
# Used to check if on a feature branch and check diff against master
git diff --name-only origin/master...HEAD

# Useful for checking master against master in a merge commit strategy environment
git diff --name-only HEAD HEAD~1
```

Both of the above commands are run, in their order listed above to detect if there is any `diff`. If there isn't any `diff` then there will be no `dynamic_pipeline` uploaded. If you wish to disable the plugin temporarily then see the above [Configuration](#Configuration)

Depending on your [merge strategy](https://help.github.com/en/github/administering-a-repository/about-merge-methods-on-github), you might need to use different `diff` commands.

## Contributing

Please read [CONTRIBUTING](https://github.com/Zegocover/git-diff-conditional-buildkite-plugin/blob/master/.github/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/Zegocover/git-diff-conditional-buildkite-plugin/tags). 

## Authors

* **Jack** - *Initial work* - [jack1902](https://github.com/jack1902)
* **Elliot** - *Initial work* - [wizardels](https://github.com/wizardels)

See also the list of [contributors](https://github.com/Zegocover/git-diff-conditional-buildkite-plugin/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* Initially looked at the [mono-repo-diff-buildkite-plugin](https://github.com/chronotc/monorepo-diff-buildkite-plugin)
* Also looked at the gitlab plugin [onlychangesexceptchanges](https://docs.gitlab.com/ee/ci/yaml/#onlychangesexceptchanges)
