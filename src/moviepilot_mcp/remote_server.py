from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from moviepilot_mcp.server import mcp
from moviepilot_mcp.auth import ApiKeyAuth


class ApiKeyAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, auth_header: str = "X-API-Key"):
        super().__init__(app)
        self.auth_header = auth_header
        self.api_key_auth = ApiKeyAuth()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        api_key = request.headers.get(self.auth_header)
        if not self.api_key_auth.verify_api_key(api_key):
            return JSONResponse(
                {"detail": f"缺少或无效的API密钥，请在请求头 {self.auth_header} 中提供有效的密钥"},
                status_code=401,
            )
        response = await call_next(request)
        return response


http_app = mcp.http_app(middleware=ApiKeyAuthMiddleware)
