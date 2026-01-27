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

The `examples/` folder contains a set of examples you can explore. Before running any example, install the required dependencies with:

```bash
pip install -e .[examples]
```

Next, add your HyperSync token to the `.env` file. You can then run an example using:

```bash
python examples/<example>.py
```

## Troubleshooting

### HyperSync Installation Issues

If you encounter build errors when installing `hypersync`, ensure Rust and system dependencies are installed.

**Ubuntu/Debian:**
```bash
# Install all required dependencies
sudo apt-get update
sudo apt-get install build-essential capnproto libcapnp-dev

# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

**macOS:**
```bash
# Install Xcode command line tools
xcode-select --install

# Install Cap'n Proto via Homebrew
brew install capnp

# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

**Then install hypersync:**
```bash
pip install --no-cache-dir --use-pep517 "hypersync==0.7.17"
```

Common errors:
- **"cargo not found"**: Install Rust toolchain
- **"capnp: No such file or directory"**: Install Cap'n Proto (`apt-get install capnproto libcapnp-dev` on Ubuntu, `brew install capnp` on macOS)
- **Build fails on Linux**: Install build essentials: `apt-get install build-essential`

