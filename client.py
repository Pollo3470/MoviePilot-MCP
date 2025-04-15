import asyncio
import logging
import os
from typing import Optional, Dict, Any

import httpx
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class MoviePilotError(Exception):
    """Custom exception for MoviePilot API errors."""
    pass


class AuthenticationError(MoviePilotError):
    """Exception raised for authentication failures."""

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
            response.raise_for_status()  # Raise exception for 4xx/5xx errors

            token_data = response.json()
            self._token = token_data.get("access_token")
            if not self._token:
                raise AuthenticationError("Login successful but no access token received.")
            logger.info("Login successful, token obtained.")
            # Optionally store user info: token_data.get('user_name'), etc.

        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
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
        """Returns authorization headers if logged in."""
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
        """Makes an authenticated request to the API."""
        headers = self._client.headers.copy()
        if requires_auth:
            headers.update(await self._get_auth_headers())

        url = f"{self.base_url}{endpoint}"  # Construct full URL for logging/errors
        logger.debug(f"Request: {method} {url} Params: {params} JSON: {json_data}")

        try:
            response = await self._client.request(
                method,
                endpoint,  # Use relative endpoint for client
                params=params,
                json=json_data,
                data=data,
                headers=headers,
            )
            response.raise_for_status()
            # Handle cases where response might be empty or not JSON
            if response.status_code == 204 or not response.content:
                return None
            try:
                return response.json()
            except ValueError:  # Includes JSONDecodeError
                logger.warning(f"Non-JSON response received for {method} {endpoint}: {response.text[:100]}...")
                return response.text  # Or raise an error, depending on expected behavior

        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_detail = e.response.json()
            except Exception:
                error_detail = e.response.text
            logger.error(f"API 请求失败 ({method} {url}): {e.response.status_code} - {error_detail}")
            if e.response.status_code in (401, 403):
                self._token = None  # Invalidate token
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
            raise MoviePilotError(f"API Error ({e.response.status_code}): {error_detail}") from e
        except httpx.RequestError as e:
            logger.error(f"Network error during API request ({method} {url}): {e}")
            raise MoviePilotError(f"Network error: {e}") from e
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during API request ({method} {url}): {e}")
            raise MoviePilotError(f"An unexpected error occurred: {e}") from e

    async def close(self) -> None:
        """Closes the underlying HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        # Optionally perform async setup, like ensuring client is ready
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


async def main():
    async with MoviePilotClient() as client:
        try:
            # Example API call
            response = await client._request("GET", "/api/v1/user/")
            print(response)
        except MoviePilotError as e:
            logger.error(f"MoviePilot error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
