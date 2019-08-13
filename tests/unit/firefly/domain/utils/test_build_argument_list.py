from firefly import build_argument_list


def test_reserved_words():
    def foo(id_: str):
        pass

    args = build_argument_list({'id': 'bar'}, foo)

    assert 'id_' in args and args['id_'] == 'bar'
