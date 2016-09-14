# -*- coding: utf-8 -*-

from . import general, iterators


class BaseRequest:

    def __init__(self, api, method):
        self.api = api
        self.method = method

    def __call__(self, _suffix=".json", **kwargs):
        return (*self.api.sanitize_params(self.method, **kwargs),
                self.api.url(_suffix))


class Iterators:

    def __init__(self, api, method):
        self.api = api
        self.method = method

    def _get_iterator(self, iterator):
        def iterate(**kwargs):
            return iterator(getattr(self.api, self.method), **kwargs)
        return iterate

    def __getattr__(self, key):
        return self._get_iterator(getattr(iterators, key))


class Request(BaseRequest):

    def __init__(self, api, method):
        super().__init__(api, method)
        self.iterator = Iterators(api, method)

    async def __call__(self, _skip_params=None,
                       _error_handling=True,
                       **kwargs):
        kwargs, skip_params, url = super().__call__(**kwargs)

        skip_params = skip_params if _skip_params is None else _skip_params

        kwargs.update(method=self.method,
                      url=url,
                      skip_params=skip_params)

        client_request = self.api._client.request

        if self.api._client.error_handler:
            client_request = self.api._client.error_handler(client_request,
                                                            _error_handling)

        return await client_request(**kwargs)


class StreamingRequest(BaseRequest):

    def __call__(self, **kwargs):
        kwargs, skip_params, url = super().__call__(**kwargs)

        return self.api._client.stream_request(self.method,
                                               url=url,
                                               skip_params=skip_params,
                                               **kwargs)