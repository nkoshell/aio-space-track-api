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
