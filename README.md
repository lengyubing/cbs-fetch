# CBS News Scraper API

这是一个使用FastAPI构建的新闻抓取服务，定期从CBS新闻网站的世界新闻版块抓取新闻，并通过API提供这些新闻。

## 功能

- 定期抓取CBS世界新闻
- 存储新闻到数据库
- 提供REST API访问新闻数据
- 支持直接部署到Render.com

## 技术栈

- FastAPI: Web框架
- SQLAlchemy: ORM
- BeautifulSoup4: 网页解析
- APScheduler: 定时任务

## 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 运行服务
uvicorn main:app --reload
```

## API端点

- `GET /`: API状态检查
- `GET /news`: 获取新闻列表
- `GET /news/{news_id}`: 获取单条新闻详情
- `POST /scrape-now`: 手动触发抓取任务

## 部署到Render.com

1. 在Render.com创建一个新的Web Service
2. 连接到你的GitHub仓库
3. 选择「Python」作为环境
4. 设置构建命令: `pip install -r requirements.txt`
5. 设置启动命令: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. 设置以下环境变量:
   - `PORT`: 8000
   - `DATABASE_URL`: 你的数据库URL（如果使用Render的PostgreSQL服务）
   - `PYTHON_VERSION`: 3.11.0
7. 点击「Create Web Service」

或者，你可以直接使用项目中的`render.yaml`配置文件进行部署，Render.com会自动识别并应用配置。

## 数据库迁移

如果你想在生产环境中使用PostgreSQL而不是SQLite:

1. 在Render.com创建一个PostgreSQL数据库
2. 获取数据库连接URL
3. 在Web Service的环境变量中设置`DATABASE_URL`

## 许可证

MIT