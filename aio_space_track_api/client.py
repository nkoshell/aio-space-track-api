# -*- coding: utf-8 -*-
import logging

from aiohttp import ClientSession, ClientResponseError
from space_track_api import SpaceTrackApi, SpaceTrackQueryBuilder


class AsyncSpaceTrackApi(SpaceTrackApi):
    def __init__(self, login, password, session=None, loop=None, **kwargs):
        kwargs.setdefault('logger', logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__)))

        super().__init__(login, password, **kwargs)

        self.session = session if isinstance(session, ClientSession) else ClientSession(loop=loop)

    async def tle_latest(self, **kwargs):
        kwargs['entity'] = 'tle_latest'
        return await self.query(**kwargs)

    async def tle_publish(self, **kwargs):
        kwargs['entity'] = 'tle_publish'
        return await self.query(**kwargs)

    async def omm(self, **kwargs):
        kwargs['entity'] = 'omm'
        return await self.query(**kwargs)

    async def boxscore(self, **kwargs):
        kwargs['entity'] = 'boxscore'
        return await self.query(**kwargs)

    async def satcat(self, **kwargs):
        kwargs['entity'] = 'satcat'
        return await self.query(**kwargs)

    async def launch_site(self, **kwargs):
        kwargs['entity'] = 'launch_site'
        return await self.query(**kwargs)

    async def satcat_change(self, **kwargs):
        kwargs['entity'] = 'satcat_change'
        return await self.query(**kwargs)

    async def satcat_debut(self, **kwargs):
        kwargs['entity'] = 'satcat_debut'
        return await self.query(**kwargs)

    async def decay(self, **kwargs):
        kwargs['entity'] = 'decay'
        return await self.query(**kwargs)

    async def tip(self, **kwargs):
        kwargs['entity'] = 'tip'
        return await self.query(**kwargs)

    async def tle(self, **kwargs):
        return await self.query(**kwargs)

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

    async def login(self):
        async with self.session.post('{}/{}'.format(self.url, self.login_url), data=self.credentials) as resp:
            if resp.reason == 'OK':
                self.logger.info('"Successfully logged in"')
                return self.session

    async def logout(self):
        async with self.session.get('{}/{}'.format(self.url, self.logout_url)) as resp:
            if resp.reason == 'OK':
                self.logger.info(await resp.text())

    def __enter__(self):
        raise NotImplementedError('Only async use')

    async def __aenter__(self):
        await self.login()
        return self

    async def __aexit__(self, *args):
        await self.logout()
        self.close()
