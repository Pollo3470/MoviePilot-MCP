from typing import Optional, Dict, Any, List

from ..movie_pilot_client import MoviePilotClient, default_client
from ..schemas.subscribe import Subscribe


class SubscribeAPI:
    """处理与媒体订阅相关的API调用。"""

    def __init__(self, client: MoviePilotClient = default_client):
        self.client = client

    async def add_subscribe(
            self,
            subscribe_data: Subscribe
    ) -> Dict[str, Any]:
        """
        添加新的媒体订阅。
        对应接口: POST /api/v1/subscribe/
        需要请求体符合Subscribe模式。
        """
        endpoint = "/api/v1/subscribe/"
        if not subscribe_data.name or not subscribe_data.type:
            raise ValueError("订阅数据必须至少包含 name 和 type 字段。")
        data_dict = subscribe_data.model_dump(exclude_unset=True)
        return await self.client._request("POST", endpoint, json_data=data_dict)

    async def list_subscribes(self) -> List[Dict[str, Any]]:
        """
        列出所有当前订阅。
        对应接口: GET /api/v1/subscribe/
        """
        endpoint = "/api/v1/subscribe/"
        return await self.client._request("GET", endpoint)

    async def get_subscribe_details(self, subscribe_id: int) -> Dict[str, Any]:
        """
        通过ID获取特定订阅的详细信息。
        对应接口: GET /api/v1/subscribe/{subscribe_id}
        """
        endpoint = f"/api/v1/subscribe/{subscribe_id}"
        return await self.client._request("GET", endpoint)

    async def update_subscribe(
            self,
            subscribe_data: Subscribe
    ) -> Dict[str, Any]:
        """
        更新现有订阅。
        对应接口: PUT /api/v1/subscribe/
        需要请求体符合Subscribe模式，并包含'id'字段。
        """
        endpoint = "/api/v1/subscribe/"
        if not subscribe_data.id:
            raise ValueError("更新订阅时需要提供订阅ID('id')。")
        data_dict = subscribe_data.model_dump(exclude_unset=True)
        return await self.client._request("PUT", endpoint, json_data=data_dict)

    async def delete_subscribe_by_id(self, subscribe_id: int) -> Dict[str, Any]:
        """
        通过ID删除订阅。
        对应接口: DELETE /api/v1/subscribe/{subscribe_id}
        """
        endpoint = f"/api/v1/subscribe/{subscribe_id}"
        return await self.client._request("DELETE", endpoint)

    async def delete_subscribe_by_media_id(
            self,
            media_id: str,
            season: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        通过媒体ID（例如"tmdb:123"）删除订阅。
        对应接口: DELETE /api/v1/subscribe/media/{mediaid}
        """
        endpoint = f"/api/v1/subscribe/media/{media_id}"
        params = {}
        if season is not None:
            params["season"] = season
        return await self.client._request("DELETE", endpoint, params=params)

    async def get_subscribe_by_media_id(
            self,
            media_id: str,
            season: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        检查媒体项目（可选择季）是否已订阅。
        对应接口: GET /api/v1/subscribe/media/{mediaid}
        如果找到订阅则返回订阅详情，如果未找到可能返回None或抛出404错误。
        """
        endpoint = f"/api/v1/subscribe/media/{media_id}"
        params = {}
        if season is not None:
            params["season"] = season
        return await self.client._request("GET", endpoint, params=params)

    async def set_subscribe_status(
            self,
            subscribe_id: int,
            enable: bool
    ) -> Dict[str, Any]:
        """
        启用或禁用订阅。
        对应接口: PUT /api/v1/subscribe/status/{subid}
        """
        endpoint = f"/api/v1/subscribe/status/{subscribe_id}"
        # 根据API预期确定状态字符串（可能需要调整）
        state_str = "enable" if enable else "disable"
        params = {"state": state_str}
        return await self.client._request("PUT", endpoint, params=params)
