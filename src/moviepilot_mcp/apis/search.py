from typing import Optional, Dict, Any, List
from ..movie_pilot_client import MoviePilotClient, default_client


class SearchAPI:
    """Handles API calls related to searching resources (torrents)."""

    def __init__(self, client: MoviePilotClient = default_client):
        self.client = client

    async def search_resources_by_media_id(
            self,
            media_id: str,
            mtype: Optional[str] = None,
            season: Optional[int] = None,
            sites: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        精确搜索资源（种子）
        Args:
            media_id: tmdb:123, douban:456
            mtype: 电影/电视剧/系列/未知
            season: 季号
            sites: 站点id列表

        Returns: 资源信息列表

        """
        endpoint = f"/api/v1/search/media/{media_id}"
        params = {}
        if mtype: params["mtype"] = mtype
        if season: params["season"] = season
        if sites: params["sites"] = sites

        return await self.client._request("GET", endpoint, params=params)

    async def search_resources_by_title(
            self,
            keyword: Optional[str] = None,
            page: int = 0,
            sites: Optional[str] = None,
    ) -> Dict[str, Any]:  # Assuming Response schema
        """
        模糊搜索资源（种子）
        """
        endpoint = "/api/v1/search/title"
        params = {"page": page}
        if keyword: params["keyword"] = keyword
        if sites: params["sites"] = sites
        return await self.client._request("GET", endpoint, params=params)

    async def get_last_search_results(self) -> List[Dict[str, Any]]:
        """
        获取最近的搜索结果
        """
        endpoint = "/api/v1/search/last"
        return await self.client._request("GET", endpoint)

    # TODO: 搜索进度SSE接口
