# Contributing

Please raise issues, and then reference the issue within a PR. This will help track bugs throughout their life-cycle if any are identified.

## Pull Requests

### Prefix commits

Please prefix commits with the following tags depending on what they are targeting:

- `[core]` - Updates to the core python script used to generate the `dynamic_pipeline`
- `[tests]` - Updates to tests
- `[docs]` - Documentation updates
- `[format]` - Commits related to formatting of the code
- `[ci]` - commits related to github actions

Use long-descriptions to go into more depth if it is required

### Running the tests (locally)

Ensure that all your tests are located within the `tests` directory and then run:

```bash
docker-compose up --build
```

The python code should be formatted with [black](https://pypi.org/project/black/) and [isort](https://pypi.org/project/isort/)

If `black` or `isort` fail, then you can fix them by running `black .` or `isort --recursive .`. Once you have formatted the code, commit formatting as a seperate commit (this reduces noise in a PR if formatting results in large changes)