&laquo; [Back](../index.md)

# Repositories

Firefly uses the [repository pattern](https://www.martinfowler.com/eaaCatalog/repository.html) 
to persist [aggregates](aggregate-root.md). The framework ships with an `sqlite` repository out of
the box. Additional storage back-ends can be added through plugins. For example, the
[firefly-aws](https://github.com/firefly-framework/firefly-aws) extension provides both a `data_api_mysql` and
a `data_api_pg` repository that communicate with the RDB via the `data api`. These are for `mysql` and
`postgresql` respectively, and work well with `AWS Aurora Serverless`.

## Not an ORM

The official repositories provided by Firefly are NOT ORM's. They do not map entity fields to specific columns in
the database. Instead, the entities are serialized into json and stored as BLOBs or JSONB, depending on the
implementation. Indexes are created on the json fields or in dedicated columns; again, depending on the
implementation. The trade-off is that, with databases like sqlite or older versions of mysql, you will not
be able to execute ad-hoc queries against the DB unless the fields are indexed. This is not a problem with postgresql
because JSONB fields can be queried ad-hoc, though the sql syntax is a little different.

## How they work

A repository is a generic class constructed for a single aggregate root. Only aggregates can be persisted or
loaded via a repository, so if you try to persist an `Entity` you will get an error. Fundamentally a repository
is just an interface that mimics a collection, very similar to a python `list`. So, you can imagine a 
repository is a list containing all the entities you have in storage. The repository will attempt to
query your back-end storage as efficiently as possible based on your search criteria. Note that typical
query rules do apply here, so if you're going to frequently be accessing an Aggregate by a field `foo`
then you should make `foo` an index.

### Aggregate Roots, Entities and Value Objects

These are the building blocks for domain models as popularized by Eric Evans. Entities and value objects
are very similar, except that entities have an identity. For example, if I have a value object that
represents 1 dollar, and I add a serial number to it, then I now have an entity representing a specific
dollar bill.

Aggregates are boundaries around groups of entities. They represent the API that you are providing
for yourself and other developers. A popular example is an order-tracking system. One Order may represent
an aggregate root in your domain model, and that Order may contain one or more Product entities.
If you wanted to remove a product from an order, you wouldn't directly delete the product entity
in your storage back-end. Instead, you'd load the Order aggregate and call a dedicated method 
to remove the product. One of the primary purposes of Aggregate Roots is to enforce invariants
in your domain model. For example, if your business has as rule that an Order cannot have both
"Product A" and "Product B", then your Order Aggregate would have the responsibility of checking
this rule and raising a Domain Error if the rule is violated.

#### Defining aggregates, entities and value objects

The following is an example domain model using the Order/Product example from above.

```python
from __future__ import annotations  # < python 3.8

import firefly as ff
from typing import List


class Address(ff.ValueObject):
    street: str = ff.required()
    street_number: int = ff.required()
    city: str = ff.required()
    state: str = ff.required()
    postal_code: str = ff.required()
    
    def __eq__(self, other: Address):
        return self.street == other.street and \
            self.street_number == other.street_number and \
            self.city == other.city and \
            self.state == other.state and \
            self.postal_code == other.postal_code


class Product(ff.Entity):
    id: str = ff.id_()
    name: str = ff.required()
    price: float = ff.required()


class Order(ff.AggregateRoot):
    id: str = ff.id_()
    user: str = ff.required()
    products: List[Product] = ff.list_()
    shipping_address: Address = ff.required()
    total: float = ff.optional(default=0.0)
    
    def add_product(self, product: Product):
        self.total += product.price
        self.products.append(product)
        
    def remove_product(self, product: Product):
        self.products.remove(product)

```

When you extend any of `ValueObject`, `Entity`, or `AggregateRoot`, your class will become a
[dataclass](https://docs.python.org/3/library/dataclasses.html). To provide metadata about the
fields in your objects, Firefly provides a set of functions that generate dataclass `fields`.
The following functions are provided:

1. `id_()`: Denotes that this property is an ID. By default, it is a UUID stored as a string.
In general, you should always put an `id_()` field on your `Entity` and `AggregateRoot` with the name
`id`.
2. `list_()`: A python list.
3. `dict_()`: A python dict.
4. `now()`: A datetime field that will automatically default to the current time.
5. `today()`: A date field that will automatically default to today.
6. `required()`: Denotes that this field is required upon instantiation.
7. `optional(default=MISSING)`: Denotes that this field is optional. A default value can be provided.
8. `hidden()`: DEPRECATED.

### Getting a repository

Repositories are added to a `Registry` when the kernel boots. Thus, to get a repository for a particular aggregate,
you must inject the `Registry` and ask it for the `Repository` associated with the given aggregate.

```python
import firefly as ff
from domain import Order


class GetOrderRepository(ff.DomainService):
    _registry: ff.Registry = None

    def __call__(self, id_: str):
        orders = self._registry(Order)  # orders is now an instance of Repository[Order]
        
        return orders

```

### Finding data

Once you have a repository, there are two methods of retrieving data; `find` and `filter`. Find will attempt to locate
and return a single aggregate root. The find method can take the `UUID` of the aggregate you want, or a callable
that represents your [search criteria](search-criteria.md).

```python
import firefly as ff
from domain import Order


class FetchOrderById(ff.DomainService):
    _registry: ff.Registry = None

    def __call__(self, id_: str):
        orders = self._registry(Order)
        order_by_id = orders.find(id_)
        # The above is roughly equivalent to the following:
        order_by_criteria = orders.find(lambda w: w.id == id_)

```

If you want a list of aggregates that match a set of [search criteria](search-criteria.md)
then you can use the filter method:

```python
import firefly as ff
from domain import Order


class FetchOrder(ff.DomainService):
    _registry: ff.Registry = None

    def __call__(self, user_id: str, min_price: float):
        orders = self._registry(Order)
        my_orders = orders.filter(lambda o: (o.user == user_id) & (o.total >= min_price))

```

### Persisting Data

With the repository essentially being a list, we can append Aggregates onto it like so:

```python
import firefly as ff
from domain import Order


class FetchOrder(ff.DomainService):
    _registry: ff.Registry = None

    def __call__(self):
        orders = self._registry(Order)
        order = Order(id='abc123')
        orders.append(order)

```

Note that the data is not persisted when `append()` is called. Instead, the data is queued up along
with any deletions and updates to be flushed to the back-end storage mechanism when `commit()` is
called. This is a public method, and you can use it, but you should know what you're doing in these
cases. The framework has a `TransactionHandlingMiddleware` class by default. This class will
automatically call `commit()` on all project repositories so long as no error was raised. If an
error was raised, nothing is persisted and the request can be retried. Thus, you typically don't
want to call `commit()` from within your services.

### Updates

When an Aggregate is pulled from a repository, a hash of the object is saved internally. When
`commit()` is called, every Aggregate that was retrieved in this manner is checked against this
hash to determine if the object changed. If it did, the changes will be persisted. Thus, to update
an Aggregate you can do something like this:

```python
import firefly as ff
from domain import Order


class FetchOrder(ff.DomainService):
    _registry: ff.Registry = None

    def __call__(self):
        orders = self._registry(Order)
        order = orders.find('abc123')
        order.name = 'New Name'  # This will be persisted on commit

```

### Deletions

Deletions are handled through the `remove()` method. Similar to the other methods we've covered,
these changes will not get persisted until `commit()` is called. Additionally, the `remove()` method
has some conventions baked in to handle soft deletes. If your Aggregate has a `datetime` attribute
called `deleted_on` then, instead of permanently removing this data from the back-end, the 
`deleted_on` field will be populated with the current time and an `update` is performed on the data.

```python
import firefly as ff
from domain import Order


class FetchOrder(ff.DomainService):
    _registry: ff.Registry = None

    def __call__(self):
        orders = self._registry(Order)
        order = orders.find('abc123')
        orders.remove(order)

```
