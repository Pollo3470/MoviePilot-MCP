from typing import Optional, Dict, Any, List, Union
from ..movie_pilot_client import MoviePilotClient, default_client
from ..schemas.douban_discover import DoubanDiscover
from ..schemas.tmdb_discover import TMDBDiscover


class DiscoverAPI:
    """处理与媒体信息相关的API调用，包括发现功能。"""

    def __init__(self, client: MoviePilotClient = default_client):
        self.client = client

    async def discover_douban(
            self,
            filters: DoubanDiscover,
            page: int = 1,
    ) -> List[Dict[str, Any]]:  # 返回MediaInfo列表
        """
        基于过滤条件探索豆瓣媒体
        """
        endpoint = f"/api/v1/{filters.api_path}"
        params = filters.api_params
        params["page"] = page
        return await self.client._request("GET", endpoint, params=params)

    async def discover_tmdb(
            self,
            filters: TMDBDiscover,
            page: int = 1
    ) -> List[Dict[str, Any]]:  # 返回MediaInfo列表
        """
        基于过滤条件探索TMDB媒体
        """
        endpoint = f"/api/v1/{filters.api_path}"
        params = filters.api_params
        params["page"] = page
        return await self.client._request("GET", endpoint, params=params)
