&laquo; [Back](../index.md)

# Installation

We recommend setting up a virtual environment first:

```bash
virtualenv --python=python3.7 venv
source venv/bin/activate
```

Then install Firefly::

    pip install firefly-framework

Bootstrap the framework::

    firefly generate project -n my-project -p .

