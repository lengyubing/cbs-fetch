import logging
import sys
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from models import NewsItem, get_db, engine, Base
from scraper import scrape_cbs_news

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 确保数据库表存在
print("确保数据库表存在...")
Base.metadata.create_all(bind=engine)

# 手动创建一条测试新闻
def add_test_news():
    print("\n添加测试新闻数据...")
    db = next(get_db())
    try:
        test_news = NewsItem(
            title="测试新闻标题",
            summary="这是一条测试新闻摘要",
            url="https://example.com/test-news",
            image_url="https://example.com/test-image.jpg",
            published_at=datetime.utcnow()
        )
        
        db.add(test_news)
        db.commit()
        print(f"测试新闻添加成功，ID: {test_news.id}")
        return True
    except IntegrityError as e:
        print(f"添加测试新闻时出现完整性错误: {e}")
        db.rollback()
        return False
    except Exception as e:
        print(f"添加测试新闻时出错: {e}")
        db.rollback()
        return False
    finally:
        db.close()

# 检查数据库中的新闻数量
def check_news_count():
    print("\n检查数据库中的新闻数量...")
    db = next(get_db())
    try:
        count = db.query(NewsItem).count()
        print(f"数据库中共有 {count} 条新闻")
        
        if count > 0:
            news = db.query(NewsItem).order_by(NewsItem.id.desc()).limit(5).all()
            print("最近5条新闻:")
            for item in news:
                print(f"ID: {item.id}, 标题: {item.title}, URL: {item.url}")
        
        return count
    except Exception as e:
        print(f"查询数据库时出错: {e}")
        return 0
    finally:
        db.close()

# 运行爬虫并检查结果
def run_scraper():
    print("\n开始运行爬虫...")
    result = scrape_cbs_news()
    print(f"爬虫返回了 {len(result) if result else 0} 条新闻")
    
    if result:
        print("\n爬取到的前5条新闻标题:")
        for i, item in enumerate(result[:5], 1):
            print(f"{i}. {item.get('title', '无标题')}")
    
    return result

# 主函数
def main():
    print("===== 开始调试爬虫和数据库 =====")
    
    # 检查初始数据库状态
    initial_count = check_news_count()
    
    # 添加测试新闻
    test_added = add_test_news()
    
    # 再次检查数据库
    if test_added:
        after_test_count = check_news_count()
        if after_test_count <= initial_count:
            print("\n警告: 测试新闻似乎没有成功添加到数据库")
    
    # 运行爬虫
    run_scraper()
    
    # 最终检查数据库
    final_count = check_news_count()
    
    print("\n===== 调试总结 =====")
    print(f"初始新闻数量: {initial_count}")
    print(f"添加测试新闻: {'成功' if test_added else '失败'}")
    print(f"最终新闻数量: {final_count}")
    print(f"爬虫是否添加了新闻: {'是' if final_count > (initial_count + (1 if test_added else 0)) else '否'}")

if __name__ == "__main__":
    main()