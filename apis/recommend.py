from typing import List, Dict, Any
from datetime import datetime

from client import MoviePilotClient, default_client


class RecommendAPI:
    """
    用于从 MoviePilot API 获取推荐信息的 API 类
    """

    def __init__(self, client: MoviePilotClient = default_client):
        self.client = client

    async def get_trending(self, media_type: str = "movie", page: int = 1, count: int = 10) -> List[Dict[str, Any]]:
        """
        获取 TMDb 流行趋势媒体列表。
        使用 /api/v1/discover/tmdb_movies 或 /api/v1/discover/tmdb_tvs 接口。
        Args:
            media_type: 'movie' 或 'tv'
            page: 页码
            count: 每页数量

        Returns:
            流行媒体信息列表
        """
        if media_type == "movie":
            endpoint = "/api/v1/discover/tmdb_movies"
            params = {"page": page, "count": count, "sort_by": "popular"} # 假设 discover 支持 sort_by=popular
        elif media_type == "tv":
            endpoint = "/api/v1/discover/tmdb_tvs"
            params = {"page": page, "count": count, "sort_by": "popular"} # 假设 discover 支持 sort_by=popular
        else:
            raise ValueError("media_type 必须是 'movie' 或 'tv'")

        # 注意: MoviePilot 的 discover 接口可能不直接支持按流行度排序，
        # 可能需要根据实际 API 调整参数或获取后处理。
        return await self.client._request("GET", endpoint, params=params)

    async def get_upcoming_or_newly_released(self, media_type: str = "movie", page: int = 1, count: int = 10) -> List[Dict[str, Any]]:
        """
        获取 TMDb 即将上映（电影）或新发布（剧集）的媒体列表。
        电影使用 /api/v1/recommend/douban_showing，剧集使用 /api/v1/discover/tmdb_tvs。
        Args:
            media_type: 'movie' 或 'tv'
            page: 页码
            count: 每页数量

        Returns:
            媒体信息列表 (尝试按日期排序)
        """
        results = []
        if media_type == "movie":
            # 使用豆瓣正在上映接口，比较接近 Upcoming
            endpoint = "/api/v1/recommend/douban_showing"
            params = {"page": page, "count": count}
            results = await self.client._request("GET", endpoint, params=params)
            # 该接口可能已按日期排序，或需要根据返回字段排序
            # results.sort(key=lambda x: x.get('release_date', '0'), reverse=True)

        elif media_type == "tv":
            # 使用 TMDb TV Discover，假设包含最新发布，并尝试按日期排序
            endpoint = "/api/v1/discover/tmdb_tvs"
            # 尝试让API排序，如果API不支持，则在获取后手动排序
            params = {"page": page, "count": count, "sort_by": "release_date.desc"}
            try:
                results = await self.client._request("GET", endpoint, params=params)
            except Exception: # 如果API不支持 sort_by 或其他错误
                 # 尝试不带排序参数获取
                 params = {"page": page, "count": count}
                 results = await self.client._request("GET", endpoint, params=params)
                 # 手动排序 (假设有 first_air_date 字段)
                 try:
                     results.sort(key=lambda x: datetime.strptime(x.get('first_air_date', '1900-01-01'), '%Y-%m-%d'), reverse=True)
                 except (ValueError, TypeError):
                     # 如果日期格式不符或字段不存在，无法排序
                     pass
        else:
            raise ValueError("media_type 必须是 'movie' 或 'tv'")

        return results 