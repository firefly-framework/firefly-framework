import pytest
from firefly import Message


def test_constructor():
    m = Message()
    assert m.body() is None
    assert '_id' in m.headers()
    assert len(m.headers().keys()) == 1

    headers = {'key': 'value'}
    m = Message('foo', headers)
    assert m.body() == 'foo'
    assert len(m.headers().keys()) == 2
    assert m.header('key') == 'value'


def test_to_dict(sut):
    d = sut.to_dict()
    assert 'headers' in d
    assert 'body' in d
    assert '_id' in d['headers']
    assert d['headers']['key1'] == 'value1'
    assert d['headers']['key2'] == 'value2'
    assert d['body'] == 'foo'


def test_header(sut):
    assert sut.header('key1') == 'value1'
    sut.header('key3', 'value3')
    assert sut.header('key3') == 'value3'


def test_get(sut):
    assert sut.get('key1') == 'value1'
    assert sut.get('foo') is None
    assert sut.get('foo', 'default') == 'default'


def test_headers(sut):
    sut.headers({'foo': 'bar'})
    assert sut.headers() == {'foo': 'bar'}


def test_unset(sut):
    sut.unset('key1')
    assert sut.get('key1') is None


def test_body(sut):
    sut.body('bar')
    assert sut.body() == 'bar'


def test_merge(sut):
    sut.merge(Message('bar', {'key3': 'value3'}))
    assert sut.body() == 'bar'
    assert 'key1' in sut.headers()
    assert 'key2' in sut.headers()
    assert 'key3' in sut.headers()


def test_resolve(sut):
    assert sut.resolve('headers.key1') == 'value1'
    sut.header('key3', {'foo': 'bar'})
    assert sut.resolve('headers.key3.foo') == 'bar'


def test_set_path(sut):
    sut.set_path('headers.key3.foo', 'bar')
    assert sut.header('key3') == {'foo': 'bar'}


@pytest.fixture()
def sut():
    return Message(body='foo', headers={
        'key1': 'value1',
        'key2': 'value2'
    })
