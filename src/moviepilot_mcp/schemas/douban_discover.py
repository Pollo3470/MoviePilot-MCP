import datetime
from typing import Optional, Dict, Literal
from pydantic import BaseModel, Field
from enum import Enum

from ..schemas import MediaType


class DoubanSort(str, Enum):
    """
    豆瓣排序方式枚举
    """
    U = 'U'  # 综合排序
    R = 'R'  # 首播时间
    T = 'T'  # 近期热度
    S = 'S'  # 高分优先


class DoubanCategory(str, Enum):
    """
    豆瓣风格枚举
    """
    COMEDY = '喜剧'
    LOVE = '爱情'
    ACTION = '动作'
    SCI_FI = '科幻'
    ANIMATION = '动画'
    SUSPENSE = '悬疑'
    CRIME = '犯罪'
    THRILLER = '惊悚'
    ADVENTURE = '冒险'
    MUSIC = '音乐'
    HISTORY = '历史'
    FANTASY = '奇幻'
    HORROR = '恐怖'
    WAR = '战争'
    BIOGRAPHY = '传记'
    MUSICAL = '歌舞'
    MARTIAL_ARTS = '武侠'
    EROTIC = '情色'
    DISASTER = '灾难'
    WESTERN = '西部'
    DOCUMENTARY = '纪录片'
    SHORT_FILM = '短片'


class DoubanZone(str, Enum):
    """
    豆瓣地区枚举
    """
    CHINESE = '华语'
    EURO_AMERICAN = '欧美'
    KOREAN = '韩国'
    JAPANESE = '日本'
    MAINLAND_CHINA = '中国大陆'
    USA = '美国'
    HONG_KONG = '中国香港'
    TAIWAN = '中国台湾'
    UK = '英国'
    FRANCE = '法国'
    GERMANY = '德国'
    ITALY = '意大利'
    SPAIN = '西班牙'
    INDIA = '印度'
    THAILAND = '泰国'
    RUSSIA = '俄罗斯'
    CANADA = '加拿大'
    AUSTRALIA = '澳大利亚'
    IRELAND = '爱尔兰'
    SWEDEN = '瑞典'
    BRAZIL = '巴西'
    DENMARK = '丹麦'


def get_available_years() -> list[str]:
    """
    动态生成可用的年份和年代选项列表
    """
    # 基础年代
    decade_list = [
        '2020年代',
        '2010年代',
        '2000年代',
        '90年代',
        '80年代',
        '70年代',
        '60年代',
    ]

    # 动态添加当前年份及往前5年
    current_year = datetime.date.today().year
    dynamic_years = []
    for i in range(6):
        year_str = str(current_year - i)
        dynamic_years.append(year_str)

    # 这里将动态年份放在前面
    return dynamic_years + decade_list


class DoubanDiscover(BaseModel):
    """
    豆瓣发现
    """
    media_type: MediaType = Field(default=MediaType.MOVIES, description="媒体类型")
    sort: DoubanSort = Field(default=DoubanSort.U, description="排序方式")
    category: Optional[DoubanCategory] = Field(default=None, description="风格")
    zone: Optional[DoubanZone] = Field(default=None, description="地区")
    year: Optional[Literal[*get_available_years()]] = Field(default=None,
                                                            description="年份或年代，为年份时仅包含该年份的媒体")

    @property
    def tags(self) -> str:
        """
        根据选择的风格、地区、年份生成用于 API 的 tags 参数。
        """
        tag_parts = [self.category.value if self.category else None,
                     self.zone.value if self.zone else None,
                     self.year]
        return ','.join(filter(None, tag_parts))  # filter(None, ...) 移除 None 或空字符串

    @property
    def api_params(self) -> Dict[str, str]:
        """
        生成用于调用 MediaCardListView API 的参数字典。
        """
        params = {'sort': self.sort.value}
        generated_tags = self.tags
        if generated_tags:
            params['tags'] = generated_tags
        return params

    @property
    def api_path(self) -> str:
        """
        生成用于调用 MediaCardListView API 的路径。
        """
        return f"discover/douban_{self.media_type.value}"
