# Firefly Framework

Firefly is primarily tested on Debian. Most of the setup described below should work on most *nix systems.

### 1. Installation

```bash
$ virtualenv --python=python3.9 venv
$ source venv/bin/activate
$ pip install firefly-framework
$ firefly generate project -n hello_world -p .
$ pip install -e .
```

