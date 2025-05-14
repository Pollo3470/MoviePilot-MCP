FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# 设置工作目录
WORKDIR /app

# 启用字节码编译
ENV UV_COMPILE_BYTECODE=1

# 从缓存复制而不是链接，因为它是挂载的卷
ENV UV_LINK_MODE=copy

# 复制项目依赖描述文件
COPY pyproject.toml uv.lock ./

# 安装项目的依赖项（不包括项目本身和开发依赖）
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# 复制应用程序代码
COPY . /app

# 安装项目本身（不包括开发依赖）
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

ENV PYTHONUNBUFFERED=1

# 将可执行文件路径添加到 PATH
ENV PATH="/app/.venv/bin:$PATH"

# 暴露应用程序运行的端口
EXPOSE 8000

# 重置入口点，不调用 `uv`
ENTRYPOINT []

# 定义容器启动时运行的命令
CMD ["python", "-m", "moviepilot_mcp.remote_server"]
