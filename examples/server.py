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
