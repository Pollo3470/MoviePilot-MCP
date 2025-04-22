from enum import Enum


class MediaType(str, Enum):
    """媒体类型，电影或电视剧"""
    MOVIES = 'movies'
    TVS = 'tvs'
