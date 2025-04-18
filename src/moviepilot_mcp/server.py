import argparse
from typing import List, Dict, Any, Optional, Literal

from fastmcp import FastMCP

from moviepilot_mcp.apis import media, suscribe,recommend
from moviepilot_mcp.schemas.subscribe import Subscribe

mcp = FastMCP(
    name="MoviePilot MCP Server",
    instructions="本服务器提供Movie Pilot媒体库管理相关工具，包括推荐、探索、搜索、订阅和下载等功能。",
)

mediaApi = media.MediaAPI()
subscribeApi = suscribe.SubscribeAPI()
recommendApi = recommend.RecommendAPI()


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
async def get_trending_media(
        media_type: Literal["movie", "tv"] = "movie"
) -> List[Dict[str, Any]]:
    """
    获取 TMDb 上的流行趋势电影或电视剧列表。
    Args:
        media_type: 媒体类型 ('movie' 或 'tv')

    Returns:
        流行媒体信息列表
    """
    return await recommendApi.get_trending(media_type)


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
