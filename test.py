import firefly.domain as ffd

n = ffd.NetworkTopology(forwarders=[
    ffd.Forwarder(name='foo', subscribers=[
        ffd.Queue(name='foo_queue')
    ]),
    ffd.Forwarder(name='bar', subscribers=[
        ffd.Queue(name='bar_queue')
    ])
])

print(n)
d = n.to_dict()
# print(d)

ne = ffd.NetworkTopology()
ne.load_dict(d)

print(ne)
