# -*- coding: utf-8 -*-

import collections
import logging

from aiohttp import ClientSession, ClientResponseError

DEFAULT_LOG_FORMAT = '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s'
DEFAULT_LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

logger = logging.getLogger(__name__)


class SpaceTrackApi(object):
    def __init__(self, login, password, **kwargs):
        self.logger = kwargs.pop('logger', logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__)))
        self.credentials = dict(identity=login, password=password)
        self.session = ClientSession()
        self.url = kwargs.pop('url', 'https://www.space-track.org')
        self.query_url = kwargs.pop('query_url', 'basicspacedata/query')
        self.login_url = kwargs.pop('login_url', 'ajaxauth/login')
        self.logout_url = kwargs.pop('logout_url', 'ajaxauth/logout')

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

    async def __aenter__(self):
        await self.login()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.logout()
        await self.session.__aexit__(exc_type, exc_val, exc_tb)


class SpaceTrackQueryBuilder(object):
    __slots__ = (
        '_predicates',
        'entity',
        'order_by',
        'sort',
        'limit',
        'format',
        'metadata',
    )

    def __init__(self, *, entity='tle', order_by=None, sort='asc',
                 limit=None, fmt='json', metadata=False, **predicates):

        self.predicates = predicates
        self.entity = str(entity)
        self.order_by = order_by and str(order_by)
        self.sort = str(sort)
        self.limit = limit and int(limit)
        self.format = str(fmt)
        self.metadata = bool(metadata)

    @property
    def predicates(self):
        return getattr(self, '_predicates', dict())

    @predicates.setter
    def predicates(self, dictionary):
        _predicates = collections.defaultdict(list)

        if isinstance(dictionary, dict):
            for key, value in dictionary.items():
                if isinstance(value, collections.Collection) and not isinstance(value, (str, bytes)):
                    _predicates[key].extend(value)
                else:
                    _predicates[key].append(value)

        setattr(self, '_predicates', _predicates)

    @property
    def query_params(self):
        predicates = "/".join('{}/{}'.format(key, ",".join(str(value) for value in values))
                              for key, values in self.predicates.items())
        return dict(entity=self.entity,
                    predicates=predicates,
                    format=self.format,
                    metadata="true" if self.metadata else "false",
                    order_by=self.order_by,
                    sort=self.sort,
                    limit=self.limit)

    def query(self):
        q = ('basicspacedata/query/'
             'class/{entity}/'
             '{predicates}/'
             'format/{format}/'
             'metadata/{metadata}/')

        if self.order_by:
            q += 'orderby/{order_by} {sort}'

        if self.limit:
            q += 'limit/{limit}'

        return q.format(**self.query_params)

    def __repr__(self):
        return '<{}("{}")>'.format(self.__class__.__name__, str(self))

    def __str__(self):
        return self()

    def __call__(self):
        return self.query()
