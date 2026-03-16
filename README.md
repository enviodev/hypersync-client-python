# hypersync-client-python

Python package for [Envio's](https://envio.dev/) HyperSync client written in Rust

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

There are a collection of self-contained examples you can look through. To run them run `python examples/<example>.py`.

For examples that call the HyperSync API, set the Envio API token via the environment:

```bash
export ENVIO_API_TOKEN="your-token"
python examples/chain_id.py
```
