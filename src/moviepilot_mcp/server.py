import argparse
from typing import List, Dict, Any, Optional

from fastmcp import FastMCP

from moviepilot_mcp.apis import media, suscribe
from moviepilot_mcp.schemas.subscribe import Subscribe

mcp = FastMCP("MoviePilot MCP Server")
mediaApi = media.MediaAPI()
subscribeApi = suscribe.SubscribeAPI()


@mcp.tool()
async def search_media(
        title: str,
) -> List[Dict[str, Any]]:
    """
    根据媒体名称搜索相关的电影/电视剧信息
    Args:
        title: 媒体名称 (模糊搜索)

    Returns: 媒体信息列表

    """
    return await mediaApi.search_media(title, 'media')


@mcp.tool()
async def search_person(
        name: str,
) -> List[Dict[str, Any]]:
    """
    根据演员名称搜索相关的演员信息
    Args:
        name: 演员名称 (模糊搜索)

    Returns: 演员信息列表

    """
    return await mediaApi.search_media(name, 'person')


@mcp.tool()
async def get_media_details(
        tmdb_id: str,
        douban_id: str,
        type_name: str,
        title: Optional[str] = None,
        year: Optional[int] = None,
):
    """
    获取媒体详细信息
    Args:
        tmdb_id: The Movie Database ID
        douban_id: 豆瓣 ID
        type_name: 媒体类型（电影/电视剧）
        title: 媒体标题
        year: 年份

    Returns: 媒体详细信息

    """
    media_id = None
    if tmdb_id:
        media_id = f"tmdb:{tmdb_id}"
    elif douban_id:
        media_id = f"douban:{douban_id}"
    return await mediaApi.get_media_details(
        media_id=media_id,
        type_name=type_name,
        title=title,
        year=year,
    )


@mcp.tool()
async def get_season_episodes(
        source_id: str,
        season_number: int,
        source: str = "tmdb"
) -> List[Dict[str, Any]]:
    """
    获取剧集的对应季的分集信息
    Args:
        source_id: 媒体ID (tmdbid)
        season_number: 季号
        source: 数据源 ("tmdb")

    Returns: 分集信息列表

    """
    return await mediaApi.get_season_episodes(source_id, season_number, source)


@mcp.tool()
async def add_subscribe(
        subscribe_data: Subscribe
):
    """
    添加新的媒体订阅
    Args:
        subscribe_data:

    """
    return await subscribeApi.add_subscribe(subscribe_data)


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
