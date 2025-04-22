import argparse
from typing import List, Dict, Any, Optional, Literal

from fastmcp import FastMCP

from moviepilot_mcp.apis import media, suscribe, recommend, discover
from moviepilot_mcp.schemas.subscribe import Subscribe
from moviepilot_mcp.schemas.douban_discover import DoubanDiscover
from moviepilot_mcp.schemas.tmdb_discover import TMDBDiscover

mcp = FastMCP(
    name="MoviePilot MCP Server",
    instructions="本服务器提供Movie Pilot媒体库管理相关工具，包括推荐、探索、搜索、订阅和下载等功能。",
)

mediaApi = media.MediaAPI()
subscribeApi = suscribe.SubscribeAPI()
recommendApi = recommend.RecommendAPI()
discoverApi = discover.DiscoverAPI()


@mcp.tool()
async def search_media_or_person(
        type_name: Literal["media", "person"],
        name: str,
) -> List[Dict[str, Any]]:
    """
    根据名称搜索相关的媒体/演员信息
    Args:
        type_name: 类型 (media/person)
        name: 名称 (模糊搜索)

    Returns: 媒体信息列表

    """
    return await mediaApi.search_media(name, type_name)


@mcp.tool()
async def get_media_details(
        id_type: Literal["tmdb", "douban"],
        id_value: str,
        media_type: Literal["电影", "电视剧"],
        title: Optional[str] = None,
        year: Optional[int] = None,
):
    """
    获取媒体详细信息
    Args:
        id_type: ID类型 (tmdb/douban)
        id_value: ID值
        media_type: 媒体类型 (电影/电视剧)
        title: 媒体标题
        year: 年份

    Returns: 媒体详细信息

    """
    media_id = f"{id_type}:{id_value}"
    return await mediaApi.get_media_details(
        media_id=media_id,
        type_name=media_type,
        title=title,
        year=year,
    )


@mcp.tool()
async def discover_douban_media(
        filters: DoubanDiscover,
        page: int = 1,
) -> List[Dict[str, Any]]:
    """
    基于过滤条件探索豆瓣电影/电视剧

    Args:
        filters: 过滤条件
        page: 页码

    Returns:
        媒体信息列表。
    """
    return await discoverApi.discover_douban(filters, page)


@mcp.tool()
async def discover_tmdb_media(
        filters: TMDBDiscover,
        page: int = 1
) -> List[Dict[str, Any]]:
    """
    基于过滤条件探索TMDB电影/电视剧

    Args:
        filters: 过滤条件
        page: 页码

    Returns:
        媒体信息列表
    """
    return await discoverApi.discover_tmdb(filters, page)


@mcp.tool()
async def get_season_episodes(
        source_id: str,
        season_number: int,
        source: Literal["tmdb"] = "tmdb",
) -> List[Dict[str, Any]]:
    """
    获取剧集的对应季的分集信息
    Args:
        source_id: 媒体ID (tmdbid)
        season_number: 季号
        source: 数据源 ("tmdb")

    Returns: 分集信息列表

    """
    # TODO: 添加douban数据源支持
    return await mediaApi.get_season_episodes(source_id, season_number, source)


@mcp.tool()
async def add_subscribe(
        subscribe_data: Subscribe
):
    """
    添加新的媒体订阅
    订阅数据需要至少包含tmdbid、doubanid或bangumiid中的一个
    Args:
        subscribe_data: 订阅数据

    """
    return await subscribeApi.add_subscribe(subscribe_data)


@mcp.tool()
async def list_subscribes() -> List[Dict[str, Any]]:
    """
    列出用户所有媒体订阅

    Returns:
        订阅信息列表
    """
    return await subscribeApi.list_subscribes()


@mcp.tool()
async def get_subscribe(
        id_type: Literal["subscribe", "tmdb", "douban"],
        id_value: str,
        season: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    获取订阅信息。可以通过订阅ID或媒体ID（tmdb/douban）进行查询。

    Args:
        id_type: ID类型 ("subscribe", "tmdb", "douban")
        id_value: 订阅ID 或 媒体ID值
        season: 季号 (可选, 仅当 id_type 为 "tmdb" 或 "douban" 时有效)

    Returns:
        订阅详细信息，如果未找到则返回 None。
    """
    if id_type == "subscribe":
        try:
            subscribe_id = int(id_value)
            return await subscribeApi.get_subscribe_details(subscribe_id)
        except ValueError:
            raise ValueError("当 id_type 为 'subscribe' 时，id 必须是整数。")
    else:
        media_id = f"{id_type}:{id_value}"
        return await subscribeApi.get_subscribe_by_media_id(media_id, season)


@mcp.tool()
async def update_subscribe(
        subscribe_data: Subscribe
) -> Dict[str, Any]:
    """
    更新现有订阅。请求体中必须包含 'id' 字段。

    Args:
        subscribe_data: 包含订阅ID ('id') 和其他要更新字段的订阅对象。

    Returns:
        更新后的订阅信息。
    """
    if not subscribe_data.id:
        raise ValueError("更新订阅时，subscribe_data 必须包含 'id' 字段。")
    return await subscribeApi.update_subscribe(subscribe_data)


@mcp.tool()
async def delete_subscribe(
        id_type: Literal["subscribe", "tmdb", "douban"],
        id_value: str,
        season: Optional[int] = None
) -> Dict[str, Any]:
    """
    删除订阅。可以通过订阅ID或媒体ID（tmdb/douban）进行删除。

    Args:
        id_type: ID类型 ("subscribe", "tmdb", "douban")
        id_value: 订阅ID 或 媒体ID值 (例如 123)
        season: 季号 (可选, 仅当 id_type 为 "tmdb" 或 "douban" 时有效)

    Returns:
        删除操作的结果信息。
    """
    if id_type == "subscribe":
        try:
            subscribe_id = int(id_value)
            return await subscribeApi.delete_subscribe_by_id(subscribe_id)
        except ValueError:
            raise ValueError("当 id_type 为 'subscribe' 时，id 必须是整数。")
    else:
        media_id = f"{id_type}:{id_value}"
        return await subscribeApi.delete_subscribe_by_media_id(media_id, season)


@mcp.tool()
async def set_subscribe_status(
        subscribe_id: int,
        enable: bool
) -> Dict[str, Any]:
    """
    启用或禁用指定的订阅。

    Args:
        subscribe_id: 要操作的订阅ID。
        enable: True 表示启用，False 表示禁用。

    Returns:
        操作结果信息。
    """
    return await subscribeApi.set_subscribe_status(subscribe_id, enable)


@mcp.tool()
async def get_upcoming_or_newly_released_media(
        media_type: Literal["movie", "tv"] = "movie"
) -> List[Dict[str, Any]]:
    """
    获取 TMDb 上即将上映的电影或最新发布的剧集列表 (按日期倒序)。
    Args:
        media_type: 媒体类型 ('movie' 或 'tv')

    Returns:
        即将上映/最新发布媒体信息列表
    """
    return await recommendApi.get_upcoming_or_newly_released(media_type)


def main():
    parser = argparse.ArgumentParser(description="MoviePilot MCP Server")
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport method (stdio or sse)",
    )

    args = parser.parse_args()

    if args.transport == "sse":
        mcp.run("sse")
    else:
        mcp.run("stdio")


if __name__ == "__main__":
    main()
