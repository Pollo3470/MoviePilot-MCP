from typing import Optional, Dict, Any, List
from ..movie_pilot_client import MoviePilotClient, default_client


class MediaServerAPI:
    """媒体库相关接口"""

    def __init__(self, client: MoviePilotClient = default_client):
        self.client = client

    async def check_media_exists_local(
            self,
            mtype: Optional[str] = None,
            tmdbid: Optional[int] = None,
            title: Optional[str] = None,
            year: Optional[str] = None,
            season: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        检查媒体是否存在于本地媒体库
        """
        endpoint = "/api/v1/mediaserver/exists"
        params = {}
        if mtype: params["mtype"] = mtype
        if tmdbid: params["tmdbid"] = tmdbid
        if title: params["title"] = title
        if year: params["year"] = year
        if season is not None: params["season"] = season
        if not tmdbid and not title:
            raise ValueError("Either tmdbid or title must be provided for exists check.")
        return await self.client._request("GET", endpoint, params=params)
