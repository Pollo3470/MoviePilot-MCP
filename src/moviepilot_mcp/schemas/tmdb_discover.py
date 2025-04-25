from typing import Optional, Dict, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum
import datetime

from pydantic_core.core_schema import ValidationInfo

from ..schemas import MediaType


class TmdbMovieSort(str, Enum):
    """TMDB 电影排序选项"""
    POPULARITY_DESC = 'popularity.desc'  #: 热度降序
    POPULARITY_ASC = 'popularity.asc'  #: 热度升序
    RELEASE_DATE_DESC = 'release_date.desc'  #: 上映日期降序
    RELEASE_DATE_ASC = 'release_date.asc'  #: 上映日期升序
    VOTE_AVERAGE_DESC = 'vote_average.desc'  #: 评分降序
    VOTE_AVERAGE_ASC = 'vote_average.asc'  #: 评分升序


class TmdbTvSort(str, Enum):
    """TMDB 电视剧排序选项"""
    POPULARITY_DESC = 'popularity.desc'  #: 热度降序
    POPULARITY_ASC = 'popularity.asc'  #: 热度升序
    FIRST_AIR_DATE_DESC = 'first_air_date.desc'  #: 首播日期降序
    FIRST_AIR_DATE_ASC = 'first_air_date.asc'  #: 首播日期升序
    VOTE_AVERAGE_DESC = 'vote_average.desc'  #: 评分降序
    VOTE_AVERAGE_ASC = 'vote_average.asc'  #: 评分升序


class TmdbMovieGenre(str, Enum):
    """TMDB 电影风格/类型 ID"""
    ACTION = '28'  #: 动作
    ADVENTURE = '12'  #: 冒险
    ANIMATION = '16'  #: 动画
    COMEDY = '35'  #: 喜剧
    CRIME = '80'  #: 犯罪
    DOCUMENTARY = '99'  #: 纪录片
    DRAMA = '18'  #: 剧情
    FAMILY = '10751'  #: 家庭
    FANTASY = '14'  #: 奇幻
    HISTORY = '36'  #: 历史
    HORROR = '27'  #: 恐怖
    MUSIC = '10402'  #: 音乐
    MYSTERY = '9648'  #: 悬疑
    ROMANCE = '10749'  #: 爱情
    SCIENCE_FICTION = '878'  #: 科幻
    TV_MOVIE = '10770'  #: 电视电影
    THRILLER = '53'  #: 惊悚
    WAR = '10752'  #: 战争
    WESTERN = '37'  #: 西部


class TmdbTvGenre(str, Enum):
    """TMDB 电视剧风格/类型 ID"""
    ACTION_ADVENTURE = '10759'  #: 动作冒险
    ANIMATION = '16'  #: 动画
    COMEDY = '35'  #: 喜剧
    CRIME = '80'  #: 犯罪
    DOCUMENTARY = '99'  #: 纪录片
    DRAMA = '18'  #: 剧情
    FAMILY = '10751'  #: 家庭
    KIDS = '10762'  #: 儿童
    MYSTERY = '9648'  #: 悬疑
    NEWS = '10763'  #: 新闻
    REALITY = '10764'  #: 真人秀
    SCI_FI_FANTASY = '10765'  #: 科幻奇幻
    SOAP = '10766'  #: 肥皂剧
    TALK = '10767'  #: 脱口秀/谈话 (Vue 文件中为 '戏剧')
    WAR_POLITICS = '10768'  #: 战争政治
    WESTERN = '37'  #: 西部


class TmdbLanguage(str, Enum):
    """TMDB 主要语言代码"""
    ZH = 'zh'  #: 中文
    EN = 'en'  #: 英语
    JA = 'ja'  #: 日语
    KO = 'ko'  #: 韩语
    FR = 'fr'  #: 法语
    DE = 'de'  #: 德语
    ES = 'es'  #: 西班牙语
    IT = 'it'  #: 意大利语
    RU = 'ru'  #: 俄语
    PT = 'pt'  #: 葡萄牙语
    AR = 'ar'  #: 阿拉伯语
    HI = 'hi'  #: 印地语
    TH = 'th'  #: 泰语


class TMDBDiscover(BaseModel):
    """
    TMDB 发现
    """
    media_type: MediaType = Field(default=MediaType.MOVIES, description="媒体类型，电影或电视剧")
    sort_by: Union[TmdbMovieSort, TmdbTvSort] = Field(default=TmdbMovieSort.POPULARITY_DESC, description="排序方式")
    with_genres: Optional[Union[TmdbMovieGenre, TmdbTvGenre, str]] = Field(default=None,
                                                                           description="风格")
    with_original_language: Optional[TmdbLanguage] = Field(default=None, description="语言")
    with_keywords: Optional[str] = Field(default=None, description="包含的关键字 ID，逗号分隔")
    with_watch_providers: Optional[str] = Field(default=None, description="包含的观看提供商 ID，逗号分隔")
    vote_average_gte: float = Field(default=0, alias='vote_average', ge=0, le=10, description="最低平均评分")
    vote_count_gte: int = Field(default=10, alias='vote_count', ge=0, description="最少投票数")
    release_date: Optional[datetime.date] = Field(default=None, description="上映日期")

    @field_validator('sort_by')
    def validate_sort_by(cls, v: Union[TmdbMovieSort, TmdbTvSort], info: ValidationInfo):
        """根据 media_type 验证并设置正确的排序枚举或默认值。"""
        media_type = info.data.get('media_type', MediaType.MOVIES)
        if media_type == MediaType.MOVIES:
            try:
                return TmdbMovieSort(v)
            except ValueError:
                return TmdbMovieSort.POPULARITY_DESC  # 如果值无效，设为电影默认值
        elif media_type == MediaType.TVS:
            try:
                return TmdbTvSort(v)
            except ValueError:
                # 检查是否是有效的电影排序值，如果是，则重置为电视剧默认值
                if v in TmdbMovieSort._value2member_map_:
                    return TmdbTvSort.POPULARITY_DESC
                return TmdbTvSort.POPULARITY_DESC  # 如果值无效，设为电视剧默认值
        return v  # 理论上不会执行到这里

    @field_validator('with_genres')
    def validate_with_genres(cls, v: Optional[Union[TmdbMovieGenre, TmdbTvGenre, str]], info: ValidationInfo):
        """根据 media_type 验证并设置正确的风格枚举或 None。"""
        media_type = info.data.get('media_type', MediaType.MOVIES)
        if not v:  # 处理空字符串或 None 的情况
            return None
        if media_type == MediaType.MOVIES:
            try:
                return TmdbMovieGenre(v)
            except ValueError:
                return None  # 无效值，重置为 None
        elif media_type == MediaType.TVS:
            try:
                return TmdbTvGenre(v)
            except ValueError:
                # 检查是否是有效的电影风格值，如果是，则重置
                if v in TmdbMovieGenre._value2member_map_:
                    return None
                return None  # 无效值，重置为 None
        return None

    @property
    def api_path(self) -> str:
        """生成用于调用 MediaCardListView API 的路径。"""
        return f"discover/tmdb_{self.media_type.value}"

    @property
    def api_params(self) -> Dict[str, Union[str, int, float]]:
        """
        生成用于调用后端TMDB discover API的参数字典
        """
        # 排除值为 None 的字段以及 media_type 字段
        params = self.model_dump(
            by_alias=True,  # 使用 vote_average 和 vote_count 等别名
            exclude={'media_type'},  # API 参数通常不需要 media_type
            exclude_none=True  # 移除值为 None 的字段
        )

        # 特殊处理：如果 vote_average_gte 为 0，通常不需要发送给 API
        if params.get('vote_average') == 0:
            params.pop('vote_average', None)

        # 将枚举值转换为它们的实际值 (字符串)
        if 'sort_by' in params and isinstance(params['sort_by'], Enum):
            params['sort_by'] = params['sort_by'].value
        if 'with_genres' in params and isinstance(params['with_genres'], Enum):
            params['with_genres'] = params['with_genres'].value
        if 'with_original_language' in params and isinstance(params['with_original_language'], Enum):
            params['with_original_language'] = params['with_original_language'].value

        # 格式化日期字段为 YYYY-MM-DD 字符串
        if isinstance(params["release_date"], datetime.date):
            params["release_date"] = params["release_date"].isoformat()

        return params
