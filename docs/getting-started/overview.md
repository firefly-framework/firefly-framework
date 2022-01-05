&laquo; [Back](../index.md)

# Overview

Firefly is a highly-opinionated application framework, intended to ease the burden of
prototyping and releasing highly-scalable, service-oriented, domain-driven applications.
It uses a layered-architecture, much like a hexagonal (ports & adapters) architecture,
to keep concerns clearly separated, which allows your domain logic to be free of any
infrastructural or presentation concerns.

At its core, the framework provides the following components:

1. System Bus, comprised of 3 distinct buses: event, command and query
1. A dependency injection container
1. A repository registry

In addition to the primary concerns above, Firefly comes with a few other handy features,
baked in:

1. Marshalling and unmarshalling of your aggregates, entities and value objects
1. Automatic generation of json-schemas for aggregate roots that can be used for form/dto generation by front-end code
1. A router for restful http endpoints
1. Integration with argparse to easily expose your Application Services to a CLI
1. A plugin-based system for deploying your applications to cloud services
1. An asynchronous HTTP server for testing or VM/bare metal deployments
1. A myriad of Bounded Contexts (services) that you can include in your application for out-of-the-box functionality
