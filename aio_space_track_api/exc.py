# -*- coding: utf-8 -*-


class SpaceTrackEntityNotSupported(Exception):
    def __init__(self, entity=None):
        super().__init__('Entity "%s" not supported' % entity)
