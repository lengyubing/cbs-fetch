from scraper import scrape_cbs_news
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

print('开始抓取新闻...')
try:
    result = scrape_cbs_news()
    print(f'抓取完成，获取到 {len(result) if result else 0} 条新闻')
    
    if result:
        print('\n抓取到的新闻标题:')
        for i, item in enumerate(result, 1):
            print(f"{i}. {item.get('title', '无标题')}")
    else:
        print('没有抓取到任何新闻')
        
except Exception as e:
    logger.error(f"抓取过程中出错: {e}", exc_info=True)
    print(f"抓取过程中出错: {e}")