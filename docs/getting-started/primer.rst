.. _primer:

Framework Primer
================

.. contents:: Table of Contents
    :local:
    :depth: 3

Introduction
============

Firefly is a highly-opinionated application framework, intended to ease the burden of
prototyping and releasing highly-scalable, service-oriented, domain-driven applications.
It uses a layered-architecture, much like a hexagonal (ports & adapters) architecture,
to keep concerns clearly separated, which allows your domain logic to be free of any
infrastructural or presentation concerns.

At its core, the framework provides the following components:

#. System Bus, comprised of 3 distinct buses: event, command and query
#. A dependency injection container
#. A repository registry

In addition to the primary concerns above, Firefly comes with a few other handy features,
baked in:

#. Marshalling and unmarshalling of your aggregates, entities and value objects
#. Automatic generation of json-schemas for aggregate roots that can be used for form/dto generation by front-end code
#. A router for restful http endpoints
#. Integration with argparse to easily expose your Application Services to a CLI
#. A plugin-based system for deploying your applications to cloud services
#. An asynchronous HTTP server for testing or VM/bare metal deployments
#. A myriad of Bounded Contexts (services) that you can include in your application for out-of-the-box functionality

Foobar
======