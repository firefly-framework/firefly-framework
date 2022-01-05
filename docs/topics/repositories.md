&laquo; [Back](../index.md)

# Repositories

Firefly uses the [repository pattern](https://www.martinfowler.com/eaaCatalog/repository.html) 
to persist [aggregates](aggregate-root.md). The framework ships with an `sqlite` repository out of
the box. Additional storage back-ends can be added through plugins. For example, the
[firefly-aws](https://github.com/firefly-framework/firefly-aws) extension provides both a `data_api_mysql` and
a `data_api_pg` repository that communicate with the RDB via the `data api`. These are for `mysql` and
`postgresql` respectively, and work well with `AWS Aurora Serverless`.

## Not an ORM

The official repositories provided by Firefly or NOT ORM's. They do not map entity fields to specific columns in
the database. Instead, the entities are serialized into json and stored as BLOBs or JSONB, depending on the
implementation. Indexes are created on the json fields or in dedicated columns; again, depending on the
implementation. The trade-off is that, with databases like sqlite or older versions of mysql, you will not
be able to execute ad-hoc queries against the DB unless the fields are indexed. This is not a problem with postgresql
because JSONB fields can be queried ad-hoc, though the sql syntax is a little different.

## How they work

A repository is a generic class constructed for a single aggregate root. Only aggregates can be persisted or
loaded via a repository, so if you try to persist an `Entity` you will get an error. Fundamentally a repository
is just an interface that mimics a collection, very similar to a python `list`.

### Getting a repository

Repositories are added to a `Registry` when the kernel boots. Thus, to get a repository for a particular aggregate,
you must inject the `Registry` and ask it for the `Repository` associated with the given aggregate.

```python
import firefly as ff
from domain import Widget


class FetchWidgetById(ff.DomainService):
    _registry: ff.Registry = None

    def __call__(self, id_: str):
        widgets = self._registry(Widget)  # widgets is now an instance of Repository[Widget]

```

### Finding data

Once you have a repository, there are two methods of retrieving data; `find` and `filter`. Find will attempt to locate
and return a single aggregate root. The find method can take the `UUID` of the aggregate you want, or a callable
that represents your [search criteria](search-criteria.md).

```python
import firefly as ff
from domain import Widget


class FetchWidgetById(ff.DomainService):
    _registry: ff.Registry = None

    def __call__(self, id_: str):
        widgets = self._registry(Widget)
        widget_by_id = widgets.find(id_)
        widget_by_criteria = widgets.find(lambda w: w.id == id_)

```

If you want a list of aggregates that match a set of [search criteria](search-criteria.md)
then you can use the filter method:

```python
import firefly as ff
from domain import Widget


class FetchWidgetById(ff.DomainService):
    _registry: ff.Registry = None

    def __call__(self, id_: str):
        widgets = self._registry(Widget)
        my_widgets = widgets.find(lambda w: (w.foo == 'bar') & (w.baz > 1))

```
