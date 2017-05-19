# -*- coding: utf-8 -*-

import logging

DEFAULT_LOG_FORMAT = '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s'
DEFAULT_LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

logger = logging.getLogger('aio_space_track_api')
