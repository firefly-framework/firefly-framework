&laquo; [Back](../index.md)

# Messaging

Every Firefly service has 3 separate [buses](https://en.wikipedia.org/wiki/Software_bus) used for 
messaging: command, query and event. For convenience, all 3 buses are wrapped in a 4th class called
the `SystemBus`. You can inject the `SystemBus` into one of your services by extending the `SystemBusAware`
interface (See `DomainService` or `ApplicationService`, where this is done for you by default). The
`SystemBusAware` interface looks like this:

```python
class SystemBusAware:
    _system_bus: SystemBus = None

    def dispatch(self, event: Union[Event, str], data: dict = None):
        return self._system_bus.dispatch(event, data)

    def invoke(self, command: Union[Command, str], data: dict = None, async_: bool = False):
        return self._system_bus.invoke(command, data, async_=async_)

    def request(self, request: Union[Query, str], criteria: Union[BinaryOp, Callable] = None,
                data: dict = None):
        return self._system_bus.request(request, criteria, data)
```

This interface ensures the `SystemBus` is injected and adds 3 methods to your class for interacting
with the various buses. Remember that

1. Domain Events are `dispatched`
2. Commands are `invoked`
3. Queries are `requested`

## Commands

Commands are objects that signal intent. Every command has exactly one `Handler` that is responsible
for executing that command. In Firefly, `ApplicationService`'s can be marked as a command handler
using the `command_handler` annotation like so:

```python
import firefly as ff


@ff.command_handler('service_name.CommandName')
class MyHandler(ff.ApplicationService):
    def __call__(self, *args, **kwargs):
        pass  # Do something with the command.

```

The signature for `command_handler` looks like this: 

`def __call__(self, command: Union[str, type, None] = None):`

The command can be its string form, like above, a concrete class that extends Command, or None. If
None, Firefly will assume the name of the command is the same as the name of the application service.

So, all of these are equivalent:

```python
import firefly as ff
from domain import RegisterUser


@ff.command_handler('service_name.RegisterUser')
class RegisterUser(ff.ApplicationService):
    def __call__(self, *args, **kwargs):
        pass  # Register the user


@ff.command_handler(RegisterUser)
class RegisterUser(ff.ApplicationService):
    def __call__(self, *args, **kwargs):
        pass  # Register the user


@ff.command_handler()
class RegisterUser(ff.ApplicationService):
    def __call__(self, *args, **kwargs):
        pass  # Register the user

```

Similarly, there are two ways of invoking a command:

```python
import firefly as ff
from domain import RegisterUser


class MyService(ff.ApplicationService):
    def __call__(self, first_name: str, last_name: str, **kwargs):
        self.invoke('iaaa.RegisterUser', {'first_name': first_name, 'last_name': last_name})   
        self.invoke(RegisterUser(
            first_name=first_name,
            last_name=last_name
        ))

```

The `invoke` method has a 3rd optional argument called `async_`. In general, command handlers
should not return anything. This is consistent with `CQRS`. However, not everyone adheres to CQRS
and there are still some use cases where a return value is preferable. Notably, if you want to return
some type of token so that a user can check the status of their command at a later time, then this
is generally acceptable to most programmers. Commands will be invoked synchronously by default. 
This will result in a "sub request" within the same execution. However, if you don't wish to wait for 
the command to complete, you can pass `async_=True` to `invoke` and the message will be sent to the 
service's queue instead, and control will immediately return to your process.

## Queries

Queries are classes used to request data from another service. Queries are always synchronous.
Setting up a query handler is similar to a command handler. All of these are equivalent:

```python
import firefly as ff
from domain import Users as GetUsers


@ff.query_handler('iaaa.Users')
class Users(ff.ApplicationService):
    def __call__(self, **kwargs):
        return 'something'


@ff.query_handler(GetUsers)
class Users(ff.ApplicationService):
    def __call__(self, **kwargs):
        return 'something'


@ff.query_handler()
class Users(ff.ApplicationService):
    def __call__(self, **kwargs):
        return 'something'

```

There are several ways to query data, depending on your setup. The easiest way is to pass a `Callable`
to `request` that defines the [search criteria](search-criteria.md) for the query.

```python
import firefly as ff


class MyDomainService(ff.DomainService):
    def __call__(self, **kwargs):
        users = self.request('iaaa.Users', lambda u: u.name == 'John')

```

If the api of your query handler is simple, it may be easier to just pass a parameter dict to
`request`.

```python
import firefly as ff


class MyDomainService(ff.DomainService):
    def __call__(self, **kwargs):
        users = self.request('iaaa.Users', data={'id': 'abc123'})

```

And if you're using concrete classes...

```python
import firefly as ff
from domain import Users


class MyDomainService(ff.DomainService):
    def __call__(self, **kwargs):
        users = self.request(Users(
            id='abc123'
        ))

```

## Domain Events

Domain events are objects that represent things that have happened within your domain model. Events
should typically be dispatched from Aggregates or Domain services. Domain events represent a powerful
means of asynchronous communication for your systems. Any `ApplicationService` can listen for any
event, whether it comes from the same bounded context or not. You can denote an event listener with
the `on` decorator like so:

```python
import firefly as ff


@ff.on('other_context.OrderCreated')
class HandleOrderCreated(ff.ApplicationService):
    def __call__(self, **kwargs):
        pass  # Do something in response to a new order being created

```

A domain event can have many listeners. You can also freely dispatch domain events that have no
listeners. This scenario will result in a no-op.

```python
import firefly as ff


class MyService(ff.DomainService):
    def __call__(self, **kwargs):
        self.dispatch('other_context.OrderCreated', {
            'id': 'abc123',
        })

```
