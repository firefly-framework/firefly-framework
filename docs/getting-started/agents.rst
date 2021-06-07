.. _agents:

Agents
======

Every time you deploy your Firefly project, an Agent is responsible for packaging your
code, deploying, and setting up any infrastructure needed for the project. There is a
default Agent bundled with firefly-framework that will deploy your code to an aiohttp
server. This works well for local testing, but most projects will need another extension
installed that provides a different Agent. Official Agents are listed below:

#. `AWS <https://github.com/firefly-framework/firefly-aws>`_
