# MoviePilot MCP 服务器

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

这是一个 **模型上下文协议 (MCP - Model Context Protocol)** 服务器实现，用于连接大型语言模型 (LLM)
与 [MoviePilot](https://github.com/jxxghp/MoviePilot) 媒体库自动化管理服务器。

## 目标

本项目旨在让用户能够通过自然语言与他们的 MoviePilot 实例进行交互，从而实现以下功能：

* **搜索和发现** 电影、电视剧及相关信息。
* **查询** 媒体详情、季集信息、演员阵容和推荐。
* **查找** 可用的下载资源 (种子)。
* **管理** 媒体订阅（添加、查看、更新、删除、启用/禁用）。
* **控制** 下载任务（添加、查看状态、暂停、恢复、删除）。
* **获取** 媒体库状态（最近添加、正在播放、检查存在性）。

通过将 MoviePilot 的功能暴露给 LLM，用户可以在支持 MCP 的聊天应用（如 Cherry Studio 或集成了 MCP 的客户端）中，用对话的方式轻松管理媒体库。

## 使用方式

### 1. 使用 Docker 运行 streamable http 服务端

本项目支持使用 Docker 进行部署。您可以从 Docker Hub 拉取预构建的镜像。

**Docker Hub 镜像:** `pollo3470/moviepilot-mcp`

#### a. 使用 `docker run`

1. **拉取镜像:**
   ```bash
   docker pull pollo3470/moviepilot-mcp:latest
   ```

2. **准备 `.env` 文件:**
   在您希望运行 Docker 的目录下创建一个 `.env` 文件，填入必要的配置信息。
   ```dotenv
   # .env
   MOVIEPILOT_BASE_URL=http://your-moviepilot-ip:3000  # 你的 MoviePilot 地址
   MOVIEPILOT_USERNAME=your_moviepilot_username  # 你的 MoviePilot 用户名 (用于密码认证)
   MOVIEPILOT_PASSWORD=your_moviepilot_password  # 你的 MoviePilot 密码 (用于密码认证)
   MCP_API_KEY=your_strong_api_key # 请设置一个强随机的API密钥，用于保护MCP服务器的访问。未设置时会自动生成一个随机密钥并打印到日志。
   # 可选配置
   # LOG_LEVEL=INFO
   ```

3. **运行容器:**
   ```bash
   docker run -d \
     --name moviepilot-mcp \
     -p 8000:8000 \
     --env-file ./.env \
     --restart unless-stopped \
     pollo3470/moviepilot-mcp:latest
   ```
   参数说明:
    * `-d`: 后台运行容器。
    * `--name moviepilot-mcp`: 给容器命名。
    * `-p 8000:8000`: 将主机的 8000 端口映射到容器的 8000 端口。
    * `--env-file ./.env`: 从当前目录下的 `.env` 文件加载环境变量。您也可以使用多个 `-e` 参数单独指定环境变量，例如
      `-e MOVIEPILOT_BASE_URL="http://localhost:3000" -e MCP_API_KEY="your_secret_key"`。
    * `--restart unless-stopped`: 容器退出时自动重启，除非手动停止。

#### b. 使用 `docker-compose`

参考本项目根目录下 `docker-compose.yml` 文件，创建一个docker-compose.yml文件。

1. **准备 `.env` 文件:**
   与 `docker-compose.yml` 同级，创建一个 `.env` 文件，并填入必要的配置信息，如上文 `docker run` 部分所述。*
   *确保 `MCP_API_KEY` 已设置。**

2. **运行:**
   在docker-compose.yml文件所在目录下执行：
   ```bash
   docker-compose up -d
   ```
   此命令会拉取最新镜像（如果本地没有或有更新）并启动服务。

   要停止服务，请运行：
   ```bash
   docker-compose down
   ```

启动后，streamable http 的 MCP 服务将在 `http://localhost:8000/mcp` (或您配置的主机和端口) 上可用。请确保在客户端请求时，在
HTTP Header 中包含 `Authorization` 并填入您在 `.env` 文件中设置的 `MCP_API_KEY`。

### 2. Stdio模式

在支持 MCP 的应用(如Cline)中添加以下配置。

```json
{
  "mcpServers": {
    "moviepilot": {
      "command": "uvx",
      "args": [
        "moviepilot-mcp"
      ],
      "env": {
        "MOVIEPILOT_BASE_URL": "MoviePilot 服务器的URL",
        "MOVIEPILOT_USERNAME": "你的 MoviePilot 用户名",
        "MOVIEPILOT_PASSWORD": "你的 MoviePilot 密码"
      }
    }
  }
}
```

## 核心功能

基于 MoviePilot 的 API，本 MCP 服务器计划（或已）暴露以下核心功能作为 MCP Tools：

### 1. 搜索与发现

* **搜索媒体:** 根据标题/关键词查找电影、电视剧或人物。
    * *MCP Tool:* `search_media_or_person`
    * *示例:* "搜索电影《星际穿越》", "找找演员 '基努·里维斯'"
* **探索:** 探索来自豆瓣、TMDB的电影、电视剧。
    * *MCP Tool:* `discover_douban_media`, `discover_tmdb_media`
    * *示例:* "推荐一些豆瓣高分科幻片", "看看TMDB上正在热映的电影"
* **获取TMDb新作:** 获取TMDb即将上映的电影或最新播出的电视剧。
    * *MCP Tool:* `get_upcoming_or_newly_released_media`
    * *示例:* "最近有什么新上映的电影吗？", "有哪些最近开播的电视剧？"

### 2. 获取详情

* **媒体详情:** 查询电影或剧集的详细信息（简介、评分、ID 等）。
    * *MCP Tool:* `get_media_details`
    * *示例:* "告诉我《沙丘2》的详细资料"
* **季集信息:** 查询剧集的季列表或特定季的集信息。
    * *MCP Tool:* `get_season_episodes`
    * *示例:* "《老友记》有几季？", "看看《怪奇物语》第4季每一集的标题"

### 3. 订阅管理

* **添加订阅:** 新增电影或电视剧的自动下载/监控。
    * *MCP Tool:* `add_subscribe`
    * *示例:* "订阅电影《沙丘2》", "订阅电视剧《黑暗荣耀》第一季，排除预告片"
* **查看订阅:** 列出所有当前订阅或特定订阅的详情。
    * *MCP Tool:* `list_subscribes` (列出所有), `get_subscribe` (获取单个)
    * *示例:* "我现在有哪些订阅？", "我订阅了《奥本海默》吗？ (使用 get_subscribe, id_type='tmdb', id_value='奥本海默的TMDB
      ID')", "查看订阅ID为5的详情 (使用 get_subscribe, id_type='subscribe', id_value='5')"
* **更新订阅:** 修改现有订阅的设置（如过滤规则）。
    * *MCP Tool:* `update_subscribe`
    * *示例:* "把我《最后生还者》的订阅改成只下载特效字幕组的版本 (需要提供完整的订阅信息，包括ID)"
* **删除订阅:** 取消订阅。
    * *MCP Tool:* `delete_subscribe`
    * *示例:* "取消我的《沙丘2》订阅 (使用 delete_subscribe, id_type='tmdb', id_value='沙丘2的TMDB ID')", "
      删除订阅ID为5的订阅 (使用 delete_subscribe, id_type='subscribe', id_value='5')"
* **启用/禁用订阅:** 暂停或恢复订阅的自动搜索。
    * *MCP Tool:* `set_subscribe_status`
    * *示例:* "暂停订阅ID为3的订阅", "启用订阅ID为3的订阅"

### 4. 资源查找

* **精确搜索资源:** 根据 TMDB ID 或豆瓣 ID 查找可下载的种子。
    * *API:* `GET /api/v1/search/media/{mediaid}`
    * *示例:* "帮我找《奥本海默》的下载资源", "搜索《最后生还者》第一季所有集的下载"
* **模糊搜索资源:** 根据关键词搜索种子。
    * *API:* `GET /api/v1/search/title`
    * *示例:* "搜索标题里有 '4K HDR 蜘蛛侠' 的资源"

### 5. 下载任务管理

* **添加下载:** 下载一个具体的种子。
    * *API:* `POST /api/v1/download/`
    * *示例:* "下载刚才找到的那个《奥本海默》4K种子"
* **查看下载:** 列出当前正在进行的下载任务。
    * *API:* `GET /api/v1/download/`
    * *示例:* "看看现在有哪些任务在下载？进度怎么样？"
* **控制下载:** 暂停、恢复或删除下载任务。
    * *API:* `GET /api/v1/download/stop/{hash}`, `GET /api/v1/download/start/{hash}`, `DELETE /api/v1/download/{hash}`
    * *示例:* "暂停《沙丘2》的下载", "恢复下载《奥本海默》", "把那个下载失败的任务删掉"

### 6. 状态与历史查询

* **媒体库状态:** 查看媒体服务器最近添加或正在播放的内容。
    * *API:* `GET /api/v1/mediaserver/latest`, `GET /api/v1/mediaserver/playing`
    * *示例:* "我Jellyfin库里最近加了什么？", "现在有人在用Plex看电影吗？"
* **检查存在性:** 查询某个媒体是否已在库中。
    * *API:* `GET /api/v1/mediaserver/exists`
    * *示例:* "我库里有《星际穿越》了吗？", "《老友记》第一季全集都在吗？"
* **下载历史:** (可选) 查看过去的下载记录。
    * *API:* `GET /api/v1/history/download`
    * *示例:* "我上周下载了哪些电影？"

## 开发状态

* 当前状态: 逐步接入MoviePilot功能
* 未来计划: 提供MCP SSE部署方式

## 安全提示

* **环境安全:** 本服务器需要存储MP账密，请确保你的环境安全。
* **账号安全:** 建议建立一个专用的 MoviePilot 账号用于此 MCP 服务器，避免使用管理员账号。

## 开发指引

**先决条件:**

* Python 3.12+
* uv 包管理器
* 一个正在运行并可访问的 MoviePilot 服务器实例

**步骤:**

1. **克隆仓库:**
   ```bash
   git clone https://github.com/Pollo3470/MoviePilot-MCP
   cd MoviePilot-MCP
   ```
2. **配置:**
   创建 `.env` 文件 (可以从 `.env.example` 复制) 并填入必要的配置信息：
    ```dotenv
    # .env Example
    MOVIEPILOT_BASE_URL=http://your-moviepilot-ip:3000  # 你的 MoviePilot 地址
    MOVIEPILOT_USERNAME=your_moviepilot_username  # 你的 MoviePilot 用户名 (用于密码认证)
    MOVIEPILOT_PASSWORD=your_moviepilot_password  # 你的 MoviePilot 密码 (用于密码认证)
    MCP_API_KEY=your_strong_api_key # 请设置一个强随机的API密钥，用于保护MCP服务器的访问
    ```
3. **创建环境:**
   ```bash
   uv sync
   ```

## 贡献

欢迎贡献！如果你发现 Bug 或有功能建议，请提交 Issue。如果你想贡献代码，请 Fork 仓库并发起 Pull Request。

## 致谢

感谢 [MoviePilot](https://github.com/jxxghp/MoviePilot) 项目。本项目是基于MoviePilot的API构建的，没有MoviePilot的出色工作，这个MCP服务器将无法实现。

## 许可证

本项目采用 [MIT License](LICENSE) 授权。