# hypersync-client-python
Python package for [Envio's](https://envio.dev/) HyperSync client written in Rust

> **Note:** This package is temporarily published to PyPI as **`hypersync-temp`** (`pip install hypersync-temp`). Main releases will return to **`hypersync`** once access is restored. The import name remains `import hypersync`.

## Setup

Recommeded to use a venv to install the package.

```bash
python -m venv .venv
```

Then activate the venv before use.
```bash
source .venv/bin/activate
```

Then install the packages with pip.

```bash
pip install -e .
```

### Examples (`examples/`)

The `examples/` folder contains a set of examples you can explore. Before running any example, install the required dependencies with:

```bash
pip install -e .[examples]
```

Next, add your HyperSync token to the `.env` file. You can then run an example using:

```bash
python examples/<example>.py
```
