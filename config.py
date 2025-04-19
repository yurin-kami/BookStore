# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'kami',
    'database': 'book_store',
    'charset': 'utf8mb4',
    'pool_size': 20,
    'max_overflow': 2,
    'pool_recycle': 25200,  # 连接存活时间延长到2小时
    'pool_pre_ping': True,  # 自动检测连接状态
    'pool_timeout': 6000,  # 连接池获取超时时间
    'connect_timeout': 6000,  # 连接超时时间
    'read_timeout': 6000,  # 读取超时时间
    'write_timeout': 6000,  # 写入超时时间
    'max_allowed_packet': 128 * 1024 * 1024,  # 最大数据包大小设为128MB
    'local_infile': True  # 允许本地文件操作
}