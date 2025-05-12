from typing import Optional, Dict, Any, List, Union

from ..movie_pilot_client import MoviePilotClient, default_client


class MediaAPI:
    """媒体相关接口"""

    def __init__(self, client: MoviePilotClient = default_client):
        self.client = client

    async def search_media(
            self,
            title: str,
            media_type: str = "media",
            page: int = 1,
            count: int = 8
    ) -> List[Dict[str, Any]]:
        """
        模糊搜索媒体/人物信息列表
        Args:
            title: 关键字
            media_type: 媒体类型  'media'-媒体信息 'person'-人物信息
            page: 页码
            count: 每页数量

        Returns: 搜索结果列表

        """
        endpoint = "/api/v1/media/search"
        params = {
            "title": title,
            "type": media_type,
            "page": page,
            "count": count,
        }
        return await self.client._request("GET", endpoint, params=params)

    async def get_media_details(
            self,
            media_id: str,  # 例如："tmdb:123", "douban:456"
            type_name: str,  # 例如："电影", "电视剧"
            title: Optional[str] = None,
            year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        获取特定媒体项目的详细信息。
        对应接口: GET /api/v1/media/{mediaid}
        """
        endpoint = f"/api/v1/media/{media_id}"
        params: Dict[str, Any] = {"type_name": type_name}
        if title:
            params["title"] = title
        if year:
            params["year"] = year
        return await self.client._request("GET", endpoint, params=params)

    async def get_seasons(
            self,
            media_id: Optional[str] = None,
            title: Optional[str] = None,
            year: Optional[str] = None,
            season: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        获取剧集的季信息。
        对应接口: GET /api/v1/media/seasons
        """
        endpoint = "/api/v1/media/seasons"
        params = {}
        if media_id: params["mediaid"] = media_id
        if title: params["title"] = title
        if year: params["year"] = year
        if season is not None: params["season"] = season  # 允许第0季
        if not media_id and not title:
            raise ValueError("get_seasons方法必须提供media_id或title参数")
        return await self.client._request("GET", endpoint, params=params)

    async def get_season_episodes(
            self,
            source_id: Union[int, str],  # tmdbid (整数) 或其他来源ID (字符串)
            season_number: int,
            source: str = "tmdb"  # 例如："tmdb", "douban", "bangumi"
    ) -> List[Dict[str, Any]]:
        """
        从特定来源(如TMDB)获取特定季的剧集信息。
        TMDB示例: GET /api/v1/tmdb/{tmdbid}/{season}
        """
        # 根据来源调整端点（如有必要）
        if source.lower() == "tmdb":
            endpoint = f"/api/v1/tmdb/{source_id}/{season_number}"
        else:
            raise NotImplementedError(f"尚未实现'{source}'来源的季度剧集获取功能。")

        # 如需添加查询参数（例如TMDB的episode_group）
        params = {}
        return await self.client._request("GET", endpoint, params=params)
