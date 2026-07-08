# verible-py pre-commit hook

[![main](https://github.com/WernerFS/verible-py/actions/workflows/main.yml/badge.svg)](https://github.com/WernerFS/verible-py/actions/workflows/main.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/WernerFS/verible-py/main.svg)](https://results.pre-commit.ci/latest/github/WernerFS/verible-py/main)

To be used for linting and formatting verilog and system-verilog with [verible] using pre-commit.

## Usage

See [pre-commit] for instructions

Sample `.pre-commit-config.yaml`:

```yaml
-   repo: https://github.com/WernerFS/verible-py.git
    rev: 0.0.4080
    hooks:
      - id: verible-verilog-format
        args: [--inplace]
      - id: verible-verilog-lint
```

[verible]: https://chipsalliance.github.io/verible/
[pre-commit]: https://pre-commit.com
