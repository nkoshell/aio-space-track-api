AsyncSpaceTrackApi async client
_______________________________

Small async wrapper for "space-track-api" package.


Requirements
------------

- Python >= 3.5.0
- space-track-api > 1.0.0
- aiohttp >= 2.0.7


Installing
__________

::

    pip install aio-space-track-api


Getting started
---------------

To retrieve something from Space-Track:

.. code-block:: python

  # -*- coding: utf-8 -*-

  import asyncio
  from pprint import pprint

  from aio_space_track_api import AsyncSpaceTrackApi


  async def main(loop):
      async with AsyncSpaceTrackApi(loop=loop, login='<YOUR_LOGIN>', password='<YOUR_PASSWORD>') as api:
          tle_list = await api.tle(EPOCH='>now-3',
                                   NORAD_CAT_ID=(25544, 25541,),
                                   order_by=('EPOCH desc', 'NORAD_CAT_ID',),
                                   predicate=('EPOCH', 'NORAD_CAT_ID', 'TLE_LINE0', 'TLE_LINE1', 'TLE_LINE2',))
          pprint(tle_list, indent=2)


  if __name__ == '__main__':
      loop = asyncio.get_event_loop()
      loop.run_until_complete(main(loop))


Create simple proxy Space-Track server:

.. code-block:: python

  # -*- coding: utf-8 -*-

  from aiohttp import web

  from aio_space_track_api import AsyncSpaceTrackApi


  async def query(request):
      params = {mvk: request.query.getall(mvk) for mvk in request.query.keys()}

      result = await app['space_track'].query(**params)
      if isinstance(result, (dict, list)):
          return web.json_response(result)
      elif isinstance(result, str):
          return web.Response(text=result)
      return web.Response(body=result)


  async def start_space_track(app):
      app['space_track'] = AsyncSpaceTrackApi(loop=app.loop, login='<YOUR_LOGIN>', password='<YOUR_PASSWORD>')
      await app['space_track'].login()


  async def cleanup_space_track(app):
      await app['space_track'].logout()
      app['space_track'].session.close()


  if __name__ == '__main__':
      app = web.Application()
      app.on_startup.append(start_space_track)
      app.on_cleanup.append(cleanup_space_track)
      app.router.add_get('/', query)
      web.run_app(app, port=8080)



Retrieve with "httpie" <https://github.com/jakubroztocil/httpie> package::

  $ http 'http://localhost:8080/?EPOCH=>now-2&NORAD_CAT_ID=25544&order_by=EPOCH%20desc&order_by=NORAD_CAT_ID&predicate=NORAD_CAT_ID&predicate=EPOCH&NORAD_CAT_ID=25541&predicate=TLE_LINE0&predicate=TLE_LINE1&predicate=TLE_LINE2'

  HTTP/1.1 200 OK
  Content-Length: 787
  Content-Type: application/json; charset=utf-8
  Date: Fri, 19 May 2017 15:36:30 GMT
  Server: Python/3.6 aiohttp/2.0.7

  [
      {
          "EPOCH": "2017-05-18 12:54:34",
          "NORAD_CAT_ID": "25544",
          "TLE_LINE0": "0 ISS (ZARYA)",
          "TLE_LINE1": "1 25544U 98067A   17138.53789694 +.00010471 +00000-0 +16649-3 0  9993",
          "TLE_LINE2": "2 25544 051.6431 186.1005 0005417 167.7458 303.2068 15.53904648057142"
      },
      {
          "EPOCH": "2017-05-18 01:38:13",
          "NORAD_CAT_ID": "25541",
          "TLE_LINE0": "0 ARIANE 44LP DEB",
          "TLE_LINE1": "1 25541U 88109H   17138.06821101 +.00000205 +00000-0 +11912-2 0  9995",
          "TLE_LINE2": "2 25541 006.9551 084.3526 7116887 037.1179 355.1935 02.36325430158541"
      },
      {
          "EPOCH": "2017-05-17 18:20:34",
          "NORAD_CAT_ID": "25544",
          "TLE_LINE0": "0 ISS (ZARYA)",
          "TLE_LINE1": "1 25544U 98067A   17137.76428422 +.00000891 +00000-0 +20809-4 0  9995",
          "TLE_LINE2": "2 25544 051.6403 189.9518 0005214 167.7282 292.6823 15.54019900057027"
      }
  ]


Source code
-----------

The latest developer version is available in a github repository:
https://github.com/nkoshell/aio-space-track-api