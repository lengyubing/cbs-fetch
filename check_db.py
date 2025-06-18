import sqlite3
import os

# 打印当前工作目录
print(f"当前工作目录: {os.getcwd()}")

# 检查数据库文件是否存在
db_path = 'news.db'
if os.path.exists(db_path):
    print(f"数据库文件存在: {db_path}")
    print(f"文件大小: {os.path.getsize(db_path)} 字节")
else:
    print(f"数据库文件不存在: {db_path}")
    exit(1)

try:
    # 连接到数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    if not tables:
        print("数据库中没有表")
    else:
        print(f"数据库中的表: {[table[0] for table in tables]}")
        
        # 检查每个表的内容
        for table in tables:
            table_name = table[0]
            print(f"\n表 '{table_name}' 的内容:")
            
            # 获取表中的行数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"总行数: {count}")
            
            if count > 0:
                # 获取表结构
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                print(f"列名: {column_names}")
                
                # 获取前5行数据
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cursor.fetchall()
                for row in rows:
                    print(row)
            else:
                print("表中没有数据")
    
    conn.close()
    
except sqlite3.Error as e:
    print(f"数据库错误: {e}")
except Exception as e:
    print(f"发生错误: {e}")