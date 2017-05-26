# -*- coding: utf-8 -*-
import logging

from aiohttp import ClientSession, ClientResponseError
from space_track_api import SpaceTrackApi, SpaceTrackQueryBuilder

from .utils import AsyncRateLimiter


class AsyncSpaceTrackApi(SpaceTrackApi):
    def __init__(self, login, password, session=None, loop=None, **kwargs):
        kwargs.setdefault('logger', logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__)))

        super().__init__(login, password, **kwargs)

        self.session = session if isinstance(session, ClientSession) else ClientSession(loop=loop)

    @AsyncRateLimiter(max_calls=20, period=60)
    async def query(self, **kwargs):
        qb = SpaceTrackQueryBuilder(**kwargs)
        url = '{url}/{query}'.format(url=self.url, query=qb)
        self.logger.info('Send request to %s', url)
        async with self.session.get(url) as resp:
            m = self.get_response_method(qb.format)
            try:
                return await getattr(resp, m)()
            except (AttributeError, ClientResponseError) as e:
                self.logger.exception(e)
                return await resp.text()

    async def login(self):
        async with self.session.post('{}/{}'.format(self.url, self.login_url), data=self.credentials) as resp:
            if resp.reason == 'OK':
                self.logger.info('"Successfully logged in"')
                return self.session

    async def logout(self):
        async with self.session.get('{}/{}'.format(self.url, self.logout_url)) as resp:
            if resp.reason == 'OK':
                self.logger.info(await resp.text())

    @staticmethod
    def get_response_method(fmt):
        method_mapping = {
            'json': 'json',
            'xml': 'text',
            'html': 'text',
            'csv': 'text',
            'tle': 'text',
            '3le': 'text',
            'kvn': 'text',
            'stream': 'read'
        }
        return method_mapping.get(fmt, 'read')

    async def __call__(self, **kwargs):
        return await self.query(**kwargs)

    def __enter__(self):
        raise NotImplementedError('Only async use')

    async def __aenter__(self):
        await self.login()
        return self

    async def __aexit__(self, *args):
        await self.logout()
        self.close()
