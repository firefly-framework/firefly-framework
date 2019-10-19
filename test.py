from firefly.application import Container

container = Container()

print(
    container.serializer.serialize(
        container.message_factory.query('firefly.ContextMaps')
    )
)
