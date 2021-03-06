
import io
from unittest.mock import patch

import pytest

from peony import BasePeonyClient, iterators, requests
from peony.api import APIPath

from . import dummy

url = "http://whatever.com/endpoint.json"


@pytest.fixture
def api_path():
    client = BasePeonyClient("", "")
    return APIPath(['http://whatever.com', 'endpoint'], '.json', client)


@pytest.fixture
def request(api_path):
    return requests.Request(api_path, 'get')


def test_sanitize_params(request):
    l = [1, 2, 3]
    kwargs, skip_params = request.sanitize_params('get', _test=1, boom=0,
                                                  test=True, l=l, a=None,
                                                  text="aaa")

    assert kwargs == {'test': 1, 'params': {'boom': '0',
                                            'test': "true",
                                            'l': "1,2,3",
                                            'text': "aaa"}}
    assert skip_params is False


def test_sanitize_params_skip(request):
    data = io.BytesIO(b'test')
    kwargs, skip_params = request.sanitize_params('post', _test=1, boom=data)

    assert kwargs == {'test': 1, 'data': {'boom': data}}
    assert skip_params is True


@pytest.mark.asyncio
async def test_skip_params(api_path):
    request = requests.Request(api_path, 'get', _skip_params=False)
    with patch.object(request.api._client, 'request',
                      side_effect=dummy) as client_request:
        await request
        client_request.assert_called_with(method='get', skip_params=False,
                                          url=api_path.url())

    request = requests.Request(api_path, 'get', _skip_params=True)
    with patch.object(request.api._client, 'request',
                      side_effect=dummy) as client_request:
        await request
        client_request.assert_called_with(method='get', skip_params=True,
                                          url=api_path.url())


@pytest.mark.asyncio
async def test_error_handling(api_path):
    request = requests.Request(api_path, 'get', _error_handling=False)
    client = request.api._client
    with patch.object(client, 'request', side_effect=dummy):
        with patch.object(client, 'error_handler',
                          side_effect=dummy_error_handler) as error_handler:
            await request
            assert not error_handler.called


def test_get_params(request):
    kwargs, skip_params, req_url = request._get_params(_test=1, test=2)

    assert kwargs == {'test': 1, 'params': {'test': '2'}}
    assert skip_params is False
    assert url == req_url


def test_get_iterator(request):
    assert isinstance(request.iterator.with_cursor(),
                      iterators.CursorIterator)
    assert isinstance(request.iterator.with_max_id(),
                      iterators.MaxIdIterator)
    assert isinstance(request.iterator.with_since_id(),
                      iterators.SinceIdIterator)


def test_get_iterator_from_factory(api_path):
    factory = requests.RequestFactory(api_path, 'get')
    assert isinstance(factory.iterator.with_cursor(), iterators.CursorIterator)
    assert isinstance(factory.iterator.with_max_id(), iterators.MaxIdIterator)


def test_iterator_params_from_factory(api_path):
    factory = requests.RequestFactory(api_path, 'get')
    iterator = factory.iterator.with_since_id(_force=False)
    assert isinstance(iterator, iterators.SinceIdIterator)
    assert iterator.force is False
    iterator = factory.iterator.with_since_id(_force=True)
    assert isinstance(iterator, iterators.SinceIdIterator)
    assert iterator.force is True


def test_iterator_unknown_iterator(request):
    with pytest.raises(AttributeError):
        request.iterator.whatchamacallit()


def dummy_error_handler(request):
    return request


def test_request_without_error_handler(request):
    client = request.api._client
    with patch.object(client, 'request') as client_request:
        with patch.object(client, 'error_handler') as error_handler:
            request(_error_handling=False, test=1, _test=2)
            assert client_request.called_with(method='get',
                                              url=url,
                                              skip_params=False,
                                              test=2,
                                              params={'test': 1})
            assert not error_handler.called


@pytest.mark.asyncio
async def test_request_with_error_handler(request):
    with patch.object(request.api._client, 'request',
                      side_effect=dummy) as client_request:
        with patch.object(request.api._client, 'error_handler',
                          side_effect=dummy_error_handler) as error_handler:
            await request(test=1, _test=2)
            assert client_request.called_with(method='get',
                                              url=url,
                                              skip_params=False,
                                              test=2,
                                              params={'test': 1})
            assert error_handler.called


def test_streaming_request(api_path):
    streaming_request = requests.StreamingRequest(api_path, 'get')

    with patch.object(streaming_request.api._client,
                      'stream_request') as client_request:
        streaming_request(test=1, _test=2)
        assert client_request.called_with(method='get',
                                          url=url,
                                          skip_params=False,
                                          test=1,
                                          params={'test': 2})
