from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn
import logging
import os
import json
from pathlib import Path

from models import NewsItem, Base, get_db, engine
from scraper import scrape_cbs_news

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="CBS News Scraper API", description="API for scraping and serving CBS World News")

# 创建静态文件目录
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建调度器
scheduler = BackgroundScheduler()

# 定义API路由
@app.get("/", response_class=HTMLResponse)
async def root():
    # 重定向到静态HTML页面
    return RedirectResponse(url="/static/index.html")

@app.get("/news")
async def get_news(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """获取新闻列表"""
    news = db.query(NewsItem).order_by(NewsItem.published_at.desc()).offset(skip).limit(limit).all()
    # 将ORM对象转换为字典
    return [item.to_dict() for item in news]

@app.get("/news/{news_id}")
async def get_news_item(news_id: int, db: Session = Depends(get_db)):
    """获取单条新闻"""
    news_item = db.query(NewsItem).filter(NewsItem.id == news_id).first()
    if news_item is None:
        raise HTTPException(status_code=404, detail="News item not found")
    return news_item.to_dict()

@app.post("/scrape-now")
async def scrape_now(background_tasks: BackgroundTasks):
    """手动触发抓取任务"""
    background_tasks.add_task(scrape_cbs_news)
    return {"message": "Scraping task started"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )

# 启动时运行一次抓取
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application")
    # 启动时立即抓取一次
    scrape_cbs_news()
    
    # 设置定时任务，每小时抓取一次
    scheduler.add_job(scrape_cbs_news, 'interval', hours=1)
    scheduler.start()
    logger.info("Scheduled scraping job every hour")

# 关闭时停止调度器
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the application")
    scheduler.shutdown()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)