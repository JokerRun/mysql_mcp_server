# 1. 基础镜像：Python 3.12 + uv
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS uv

# 2. 基本设置
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# 3. 复制所有项目文件
ADD . /app

# 4. 创建虚拟环境并安装依赖
RUN uv venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -r requirements.txt \
    && uv pip install -e .

# 5. 启动服务
ENTRYPOINT ["uv", "run", "mysql_mcp_server"] 