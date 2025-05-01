# BookStore 在线书籍管理系统

## 项目介绍

BookStore 是一个基于 FastAPI 和 SQLAlchemy 开发的在线书籍管理系统，提供书籍的浏览、搜索、用户注册登录等功能。系统采用前后端分离架构，后端使用 FastAPI 提供 RESTful API 接口，前端可以通过这些接口获取数据并展示。

### 主要功能

- **用户管理**：用户注册、登录功能
- **书籍浏览**：分页展示书籍列表
- **书籍搜索**：支持按书名、作者、标签搜索
- **书籍详情**：查看书籍详细信息和内容
- **数据爬取**：自动爬取并更新书籍信息

### 技术栈

- **后端框架**：FastAPI
- **数据库**：MySQL
- **ORM**：SQLAlchemy
- **网络请求**：aiohttp (异步HTTP客户端)
- **HTML解析**：lxml
- **密码加密**：bcrypt
- **认证**：基于 base64 的简单令牌认证

## 安装与使用

### 环境要求

- Python 3.8+
- MySQL 5.7+

### 安装步骤

1. **克隆仓库**

```bash
git clone [ttps://github.com/yurin-kami/BookStore.git]
cd BookStore
```

2. **创建并激活虚拟环境**

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **配置数据库**

编辑 `config.py` 文件，修改数据库连接信息：

```python
# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'your_password',
    'database': 'book_store',
    'charset': 'utf8mb4',
    # 其他配置...
}
```

5. **创建数据库**

在 MySQL 中创建 `book_store` 数据库：

```sql
CREATE DATABASE book_store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

6. **启动服务**

```bash
cd routers
python main.py
```

服务将在 http://localhost:8082 启动。

### API 接口

- **用户相关**
  - POST `/register` - 用户注册
  - POST `/login` - 用户登录

- **书籍相关**
  - GET `/all_books/{page}` - 获取指定页码的书籍列表
  - POST `/book/search/name` - 按书名搜索书籍
  - POST `/book/search/author` - 按作者搜索书籍
  - POST `/all_book/tags` - 按标签搜索书籍
  - GET `/book/tags` - 获取所有书籍标签
  - POST `/book/content` - 获取书籍内容

### 数据爬取

系统提供了自动爬取书籍数据的功能，可以通过以下命令运行：

```bash
cd routers/utils
python get_note.py
```

更新现有书籍数据：

```bash
python get_note.py update
```

## 项目结构

```
BookStore/
├── config.py                 # 配置文件
├── requirements.txt          # 项目依赖
├── README.md                 # 项目说明
└── routers/                  # 路由模块
    ├── main.py               # 主程序入口
    ├── book_router.py        # 书籍相关路由
    ├── user_router.py        # 用户相关路由
    └── utils/                # 工具模块
        ├── db_rw.py          # 数据库读写操作
        ├── get_note.py       # 数据爬取脚本
        └── lightnote_url.txt # 爬取URL列表
```

## 许可证

[MIT License](LICENSE)
