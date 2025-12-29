# Contributing

## env

```sh
uv venv env --python 3.14
source env/bin/activate
uv pip install pip
```

## packages

```sh
pip install pru
pru -r requirements-all.txt
```

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
