# Contirbuting

## Install in development mode

```shell
pip install -e ."[dev]"
```

## Pytest

```shell
pytest -n auto -rA --lf -c pyproject.toml --cov-report term-missing --cov=matpowercaseframes tests/
```

## Pre-Commit

```shell
pre-commit install
pre-commit run --all-files
```
