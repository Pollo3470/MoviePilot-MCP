import asyncio
import logging
import os
from typing import Optional, Dict, Any

import httpx
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()


class MoviePilotError(Exception):
    """MoviePilot API 错误的自定义异常。"""
    pass


class AuthenticationError(MoviePilotError):
    """认证失败时引发的异常。"""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class MoviePilotClient:
    """
    MoviePilot API 异步客户端
    自动维护 JWT Token 认证机制
    """

    def __init__(
            self,
            base_url: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            timeout: float = 30.0,
    ):
        self.base_url = base_url or os.getenv("MOVIEPILOT_BASE_URL")
        self._username = username or os.getenv("MOVIEPILOT_USERNAME")
        self._password = password or os.getenv("MOVIEPILOT_PASSWORD")
        self._token: Optional[str] = None
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=timeout)
        self._auth_lock = asyncio.Lock()

        if not self.base_url:
            raise ValueError("MoviePilot URL未提供。请在 .env 文件中设置 MOVIEPILOT_BASE_URL。")
        if not self._username or not self._password:
            raise ValueError(
                "未提供用户名和密码，无法进行自动登录。"
                "请在 .env 文件中设置 MOVIEPILOT_USERNAME 和 MOVIEPILOT_PASSWORD。"
            )

    async def login(self) -> None:
        """通过账密获取JWT Token"""

        login_endpoint = "/api/v1/login/access-token"
        login_data = {
            "username": self._username,
            "password": self._password,
            # TODO: 支持OTP
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            logger.info(f"调用 {self.base_url}{login_endpoint} 获取 JWT Token")
            response = await self._client.post(
                login_endpoint, data=login_data, headers=headers
            )
            response.raise_for_status()  # 抛出4xx/5xx错误异常

            token_data = response.json()
            self._token = token_data.get("access_token")
            if not self._token:
                raise AuthenticationError("登录成功但未收到访问令牌。")
            logger.info("登录成功，获取到令牌。")
            # 可选择存储用户信息: token_data.get('user_name')等

        except httpx.HTTPStatusError as e:
            error_detail = "未知错误"
            try:
                error_detail = e.response.json()
            except Exception:
                error_detail = e.response.text
            error_message = f"Movie Pilot登录失败: {e.response.status_code} - {error_detail}"
            logger.error(error_message)
            raise AuthenticationError(error_message) from e
        except httpx.RequestError as e:
            error_message = f"登录时遇到网络连接异常: {e}"
            logger.error(error_message)
            raise AuthenticationError(error_message) from e
        except Exception as e:
            error_message = f"登录时发生意外错误: {e}"
            logger.error(error_message)
            raise AuthenticationError(error_message) from e

    async def _get_auth_headers(self) -> Dict[str, str]:
        """如果已登录，返回授权头信息。"""
        if not self._token:
            async with self._auth_lock:
                if not self._token:
                    logger.info("未登录，尝试登录以获取Token。")
                    await self.login()
        return {"Authorization": f"Bearer {self._token}"}

    async def _request(
            self,
            method: str,
            endpoint: str,
            params: Optional[Dict[str, Any]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            data: Optional[Dict[str, Any]] = None,  # 表单数据
            requires_auth: bool = True,
            retry: int = 1,
    ) -> Any:
        """向API发送已认证的请求。"""
        headers = self._client.headers.copy()
        if requires_auth:
            headers.update(await self._get_auth_headers())

        url = f"{self.base_url}{endpoint}"  # 构建完整URL用于日志记录/错误
        logger.debug(f"请求: {method} {url} 参数: {params} JSON数据: {json_data}")

        try:
            response = await self._client.request(
                method,
                endpoint,  # 使用相对路径供客户端
                params=params,
                json=json_data,
                data=data,
                headers=headers,
            )
            response.raise_for_status()
            # 处理响应可能为空或非JSON的情况
            if response.status_code == 204 or not response.content:
                return None
            try:
                return response.json()
            except ValueError:  # 包括JSONDecodeError
                logger.warning(f"收到非JSON响应，请求 {method} {endpoint}: {response.text[:100]}...")
                return response.text  # 或者抛出错误，取决于预期行为

        except httpx.HTTPStatusError as e:
            error_detail = "未知错误"
            try:
                error_detail = e.response.json()
            except Exception:
                error_detail = e.response.text
            logger.error(f"API 请求失败 ({method} {url}): {e.response.status_code} - {error_detail}")
            if e.response.status_code in (401, 403):
                self._token = None  # 使令牌失效
                if retry > 0:
                    logger.info("认证失败或Token过期，尝试重新请求。")
                    return await self._request(
                        method,
                        endpoint,
                        params=params,
                        json_data=json_data,
                        data=data,
                        requires_auth=requires_auth,
                        retry=retry - 1,
                    )
                raise AuthenticationError(f"认证失败或token过期: {e.response.status_code}",
                                          e.response.status_code) from e
            raise MoviePilotError(f"API错误 ({e.response.status_code}): {error_detail}") from e
        except httpx.RequestError as e:
            logger.error(f"API请求过程中发生网络错误 ({method} {url}): {e}")
            raise MoviePilotError(f"网络错误: {e}") from e
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"API请求过程中发生意外错误 ({method} {url}): {e}")
            raise MoviePilotError(f"发生了一个意外错误: {e}") from e

    async def close(self) -> None:
        """关闭底层HTTP客户端。"""
        await self._client.aclose()

    async def __aenter__(self):
        # 可选的异步设置，例如确保客户端已就绪
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


default_client = MoviePilotClient()

async def main():
    async with MoviePilotClient() as client:
        try:
            # API调用示例
            response = await client._request("GET", "/api/v1/user/")
            print(response)
        except MoviePilotError as e:
            logger.error(f"MoviePilot错误: {e}")
        except Exception as e:
            logger.error(f"意外错误: {e}")
