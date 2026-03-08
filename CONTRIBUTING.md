# Contributing

## env

To install Python environment, use:

```sh
uv venv env --python 3.12
source env/bin/activate
uv pip install pip
```

> [!Note]  
> Python 3.12 currently needed for `matlabengine`.

## packages

### Requirements

```sh
uv pip install pru
pru -r requirements-all.txt
```

### Matlab

Optionally, if you want to test matlab compatibility, you can install `matlabengine`

```shell
uv pip install matlabengine
```


## Install in development mode

```shell
uv pip install -e ."[dev]"
```

## Pytest

```shell
pytest -n auto -rA --lf -c pyproject.toml --cov-report term-missing --cov=matpowercaseframes tests/
pytest --lf -rA -c pyproject.toml --cov-report term-missing --cov=matpowercaseframes --nbmake
```

## Pre-Commit

```shell
pre-commit install
pre-commit run --all-files
```
