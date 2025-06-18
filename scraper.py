import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models import NewsItem, get_db

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# CBS新闻世界版块URL
CBS_NEWS_URL = "https://www.cbsnews.com/world/"

def scrape_cbs_news():
    """抓取CBS新闻世界版块的新闻"""
    logger.info(f"开始抓取CBS新闻: {CBS_NEWS_URL}")
    
    try:
        # 获取网页内容
        response = requests.get(CBS_NEWS_URL, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        response.raise_for_status()
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找新闻项
        news_items = []
        articles = soup.select('article')
        
        for article in articles:
            try:
                # 提取标题
                title_element = article.select_one('h4')
                if not title_element:
                    continue
                title = title_element.text.strip()
                
                # 提取摘要
                summary_element = article.select_one('p')
                summary = summary_element.text.strip() if summary_element else ""
                
                # 提取链接
                link_element = article.select_one('a')
                if not link_element or not link_element.has_attr('href'):
                    continue
                    
                url = link_element['href']
                if not url.startswith('http'):
                    url = f"https://www.cbsnews.com{url}"
                
                # 提取图片URL
                img_element = article.select_one('img')
                image_url = img_element['src'] if img_element and img_element.has_attr('src') else None
                
                # 创建新闻项
                news_item = {
                    "title": title,
                    "summary": summary,
                    "url": url,
                    "image_url": image_url,
                    "published_at": datetime.utcnow()  # 实际应用中应该从文章中提取发布时间
                }
                
                news_items.append(news_item)
            except Exception as e:
                logger.error(f"解析文章时出错: {e}")
                continue
        
        # 保存到数据库
        save_news_items(news_items)
        
        logger.info(f"成功抓取 {len(news_items)} 条新闻")
        return news_items
    
    except Exception as e:
        logger.error(f"抓取新闻时出错: {e}")
        return []

def save_news_items(news_items):
    """将新闻项保存到数据库"""
    db = next(get_db())
    
    try:
        saved_count = 0
        for item in news_items:
            # 检查是否已存在相同URL的新闻
            url = item["url"]
            logger.info(f"处理新闻: {item['title'][:30]}..., URL: {url}")
            
            existing_news = db.query(NewsItem).filter(NewsItem.url == url).first()
            
            if existing_news:
                logger.info(f"新闻已存在，跳过: {url}")
                continue
                
            try:
                news_item = NewsItem(
                    title=item["title"],
                    summary=item["summary"],
                    url=url,
                    image_url=item["image_url"],
                    published_at=item["published_at"]
                )
                
                db.add(news_item)
                db.flush()  # 尝试立即写入数据库但不提交事务
                saved_count += 1
                logger.info(f"新闻已添加到会话: ID={news_item.id}, 标题={item['title'][:30]}...")
            except Exception as item_error:
                logger.error(f"添加单条新闻时出错: {item_error}, 新闻标题: {item['title'][:30]}...")
                # 继续处理其他新闻，不中断整个过程
        
        if saved_count > 0:
            db.commit()
            logger.info(f"成功保存 {saved_count} 条新闻到数据库")
        else:
            logger.info("没有新的新闻需要保存")
            
    except IntegrityError as e:
        logger.error(f"保存新闻时出现完整性错误: {e}")
        db.rollback()
    except Exception as e:
        logger.error(f"保存新闻时出错: {e}")
        db.rollback()
    finally:
        db.close()