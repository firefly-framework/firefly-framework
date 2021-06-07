.. _installation:

Installation
============

We recommend setting up a virtual environment first:

.. code-block:: bash
    :substitutions:

    virtualenv --python=python|python-version| venv
    source venv/bin/activate

Then install Firefly::

    pip install firefly-framework

Bootstrap the framework::

    firefly generate project -n my-project -p .

