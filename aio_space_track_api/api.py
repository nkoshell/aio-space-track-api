# -*- coding: utf-8 -*-

import collections
import logging

from aiohttp import ClientSession, ClientResponseError

SUPPORTABLE_ENTITIES = (
    'tle_latest',
    'tle_publish',
    'omm',
    'boxscore',
    'satcat',
    'launch_site',
    'satcat_change',
    'satcat_debut',
    'decay',
    'tip',
    'tle',
)

DEFAULT_LOG_FORMAT = '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s'
DEFAULT_LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

logger = logging.getLogger(__name__)


class SpaceTrackApi(object):
    def __init__(self, login, password, session=None, loop=None, **kwargs):
        self.logger = kwargs.pop('logger', logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__)))
        self.credentials = dict(identity=login, password=password)
        self.session = session if isinstance(session, ClientSession) else ClientSession(loop=loop)
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

    def close(self):
        self.session.close()

    async def __aenter__(self):
        await self.login()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.logout()
        self.close()


class SpaceTrackEntityNotSupported(Exception):
    def __init__(self, entity=None):
        super().__init__('Entity "%s" not supported' % entity)


class SpaceTrackQueryBuilder(object):
    __slots__ = (
        '_filters',
        '_entity',
        '_order_by',
        '_limit',
        '_format',
        '_metadata',
        '_distinct',
        '_predicate',
    )

    def __init__(self, *, entity=None, order_by=None, limit=None,
                 fmt=None, metadata=False, distinct=True, predicate=None,
                 **filters):

        self.entity = entity
        self.filters = filters
        self.predicate = predicate
        self.order_by = order_by
        self.limit = limit
        self.format = fmt
        self.metadata = metadata
        self.distinct = distinct

    @property
    def entity(self):
        return self._entity

    @entity.setter
    def entity(self, value):
        if isinstance(value, collections.Iterable) and not isinstance(value, str):
            value = tuple(value)
            value = value and value[0]

        if value is None:
            value = 'tle'

        if not isinstance(value, str):
            raise TypeError('Attribute `entity` must be str()')
        elif value not in SUPPORTABLE_ENTITIES:
            raise SpaceTrackEntityNotSupported(self.entity)

        self._entity = value

    @property
    def order_by(self):
        return self._order_by

    @order_by.setter
    def order_by(self, value):
        if value is None:
            value = tuple()

        if isinstance(value, collections.Iterable) and not isinstance(value, str):
            value = tuple(value)

        if not isinstance(value, (str, collections.Iterable)):
            raise TypeError('Attribute `order_by` must be str() or collections.Iterable')

        self._order_by = value

    @property
    def predicate(self):
        return self._predicate

    @predicate.setter
    def predicate(self, value):
        if value is None:
            value = tuple()

        if isinstance(value, collections.Iterable) and not isinstance(value, str):
            value = tuple(value)

        if not isinstance(value, (str, collections.Iterable)):
            raise TypeError('Attribute `predicate` must be str() or collections.Iterable')

        self._predicate = value

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, value):
        if isinstance(value, collections.Iterable) and not isinstance(value, str):
            value = tuple(value)
            value = value and value[0]

        if value is not None:
            value = int(value)

        self._limit = value

    @property
    def format(self):
        return self._format

    @format.setter
    def format(self, value):
        if isinstance(value, collections.Iterable) and not isinstance(value, str):
            value = tuple(value)
            value = value and value[0]

        if value is None:
            value = 'json'

        if not isinstance(value, str):
            raise TypeError('Attribute `format` must be str()')

        self._format = value

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        if isinstance(value, collections.Iterable) and not isinstance(value, str):
            value = tuple(value)
            value = value and value[0]

        self._metadata = bool(value)

    @property
    def distinct(self):
        return self._distinct

    @distinct.setter
    def distinct(self, value):
        if isinstance(value, collections.Iterable) and not isinstance(value, str):
            value = tuple(value)
            value = value and value[0]

        self._distinct = bool(value)

    @property
    def filters(self):
        return self._filters

    @filters.setter
    def filters(self, dictionary):
        _filters = collections.defaultdict(list)

        if isinstance(dictionary, dict):
            for key, value in dictionary.items():
                if isinstance(value, collections.Collection) and not isinstance(value, (str, bytes)):
                    _filters[key].extend(value)
                else:
                    _filters[key].append(value)

        self._filters = _filters

    @property
    def query_params(self):
        return dict(entity=self.entity,
                    filters=self.serialize_multivalue(self.filters),
                    format=self.format,
                    limit=self.limit,
                    metadata="true" if self.metadata else "false",
                    order_by=self.serialize_multivalue(self.order_by),
                    predicates=self.serialize_multivalue(self.predicate))

    def query(self):
        q = ('basicspacedata/query/'
             'class/{entity}/'
             '{filters}/'
             'format/{format}/'
             'metadata/{metadata}/')

        if self.order_by:
            q += 'orderby/{order_by}/'

        if self.predicate:
            q += 'predicates/{predicates}/'

        if self.limit:
            q += 'limit/{limit}/'

        return q.format(**self.query_params)

    @staticmethod
    def serialize_multivalue(multivalue):
        if isinstance(multivalue, dict):
            return "/".join('{}/{}'.format(key, ",".join(str(value) for value in values))
                            for key, values in multivalue.items())
        elif isinstance(multivalue, collections.Iterable) and not isinstance(multivalue, str):
            return ",".join(str(value) for value in multivalue)

        return multivalue

    def __repr__(self):
        return '<{}("{}")>'.format(self.__class__.__name__, str(self))

    def __str__(self):
        return self()

    def __call__(self):
        return self.query()
