from sqlalchemy import create_engine, Column, Integer, VARCHAR
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# 导入配置
from config import DB_CONFIG

# 创建数据库引擎
engine = create_engine(
    f'mysql+pymysql://{DB_CONFIG["user"]}:{DB_CONFIG["password"]}@{DB_CONFIG["host"]}/{DB_CONFIG["database"]}?charset={DB_CONFIG["charset"]}',
    pool_size=DB_CONFIG['pool_size'],
    max_overflow=DB_CONFIG['max_overflow'],
    pool_recycle=DB_CONFIG['pool_recycle'],
    pool_pre_ping=DB_CONFIG['pool_pre_ping'],
    pool_timeout=DB_CONFIG['pool_timeout'],
    connect_args={
        'connect_timeout': DB_CONFIG['connect_timeout'],
        'read_timeout': DB_CONFIG['read_timeout'],
        'write_timeout': DB_CONFIG['write_timeout'],
        'max_allowed_packet': DB_CONFIG['max_allowed_packet'],
        'local_infile': DB_CONFIG['local_infile']
    }
)
Base = declarative_base()

# 定义用户表模型
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(50), nullable=True)
    password = Column(VARCHAR(64), nullable=True)
    email = Column(VARCHAR(60), unique=True, nullable=True)

# 定义书籍表模型
class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    book_author = Column(VARCHAR(64), nullable=True)
    book_name = Column(VARCHAR(512), nullable=True, unique=True)  # 添加唯一约束
    book_cover = Column(VARCHAR(128), nullable=True)
    book_tags = Column(VARCHAR(128), nullable=True)
    book_id = Column(VARCHAR(10), nullable=True, unique=True)  # 添加唯一约束
    book_synopsis = Column(MEDIUMTEXT, nullable=True)
    book_txt = Column(MEDIUMTEXT, nullable=True)

# 创建所有表
Base.metadata.create_all(engine)

# 创建会话工厂
Session = sessionmaker(bind=engine)

class UserManager:
    """用户管理类，处理用户的增删查改操作"""
    
    def __init__(self):
        self.Session = Session

    def create_user(self, name: str, password: str, email: str) -> bool:
        """创建新用户"""
        session = self.Session()
        try:
            # 创建新用户
            user = User(name=name, password=password, email=email)
            session.add(user)
            session.commit()
            print(f"创建用户成功: {name}")
            return True

        except Exception as e:
            session.rollback()
            print(f"创建用户失败: {str(e)}")
            return False

        finally:
            session.close()

    def get_user_by_email(self, email: str) -> User:
        """根据邮箱查询用户"""
        session = self.Session()
        try:
            return session.query(User).filter_by(email=email).first()
        finally:
            session.close()
    def get_user_by_name(self, name: str) -> User:
        """根据用户名查询用户"""
        session = self.Session()
        try:
            return session.query(User).filter_by(name=name).first()
        finally:
            session.close()

    def get_all_users(self) -> list:
        """获取所有用户信息"""
        session = self.Session()
        try:
            return session.query(User).all()
        finally:
            session.close()

    def delete_user(self, email: str) -> bool:
        """删除指定邮箱的用户"""
        session = self.Session()
        try:
            user = session.query(User).filter_by(email=email).first()
            if user:
                session.delete(user)
                session.commit()
                print(f"删除用户成功: {user.name}")
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"删除用户失败: {str(e)}")
            return False
        finally:
            session.close()

    def update_user(self, email: str, **kwargs) -> bool:
        """更新用户信息"""
        session = self.Session()
        try:
            user = session.query(User).filter_by(email=email).first()
            if user:
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                session.commit()
                print(f"更新用户信息成功: {user.name}")
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"更新用户信息失败: {str(e)}")
            return False
        finally:
            session.close()

class BookManager:
    """书籍管理类，处理书籍的增删查改操作"""
    
    def __init__(self):
        self.Session = Session

    def insert_books(self, page_info: dict, notes: dict) -> bool:
        """插入书籍信息和内容到数据库"""
        session = self.Session()
        try:
            # 数据校验
            if not page_info or not notes:
                print("输入数据为空，无法插入")
                return False
                
            if 'ids' not in page_info or 'names' not in page_info or 'book_txt' not in notes:
                print("必要字段缺失，无法插入")
                return False
                
            # 获取所有数据列表
            ids = page_info.get('ids', [])
            names = page_info.get('names', [])
            authors = page_info.get('authors', [])
            covers = page_info.get('covers', [])
            synopsis = page_info.get('synopsis', [])  # 获取简介列表
            tags = page_info.get('tags', [])  # 获取标签列表
            book_txts = notes.get('book_txt', [])
            
            # 计算有效数据长度
            valid_count = min(len(ids), len(names), len(book_txts))
            if valid_count == 0:
                print("没有有效的书籍数据可插入")
                return False
                
            # 开始事务，禁用自动刷新
            with session.no_autoflush:
                for i in range(valid_count):
                    book_id = ids[i]
                    book_name = names[i]
                    book_author = authors[i] if i < len(authors) else None
                    book_cover = covers[i] if i < len(covers) else None
                    book_synopsis = synopsis[i] if i < len(synopsis) else None  # 获取简介
                    book_tag = tags[i] if i < len(tags) else None  # 获取标签
                    book_txt = book_txts[i]
                    
                    # 检查必要字段是否为空
                    if not book_id or not book_name or not book_txt:
                        print(f"第 {i+1} 条数据不完整，跳过")
                        continue
                    
                    # 检查是否已存在相同的 book_id 或 book_name
                    existing_book = session.query(Book).filter(
                        (Book.book_id == book_id) | (Book.book_name == book_name)
                    ).first()
                    
                    if existing_book:
                        if existing_book.book_id == book_id:
                            print(f"书籍ID {book_id} 已存在，跳过")
                        else:
                            print(f"书籍名称 {book_name} 已存在，跳过")
                        continue

                    # 创建新书籍记录
                    book = Book(
                        book_id=book_id,
                        book_author=book_author,
                        book_name=book_name,
                        book_cover=book_cover,
                        book_synopsis=book_synopsis,  # 添加简介
                        book_tags=book_tag,  # 添加标签
                        book_txt=book_txt
                    )
                    session.add(book)
                    print(f"添加书籍: {book_name}")

                # 提交事务
                session.commit()
                print("数据库事务提交成功")
                return True

        except Exception as e:
            # 发生错误时回滚事务
            session.rollback()
            print(f"数据库事务错误，已回滚: {str(e)}")
            return False

        finally:
            # 关闭会话
            session.close()

    def get_book_by_name(self, book_name: str) -> list:
        """根据书籍名称查询书籍信息"""
        session = self.Session()
        try:
            # 使用LIKE进行模糊匹配，支持部分书名查询
            return session.query(Book).filter(Book.book_name.like(f"%{book_name}%")).all()
        finally:
            session.close()

    def get_all_books(self) -> list:
        """获取所有书籍信息"""
        session = self.Session()
        try:
            return session.query(Book).all()
        finally:
            session.close()
            
    def get_one_page(self, page: int, page_size: int = 9) -> list:
        """获取指定页码的书籍列表
        
        Args:
            page: 页码，从1开始
            page_size: 每页显示的书籍数量，默认为9
            
        Returns:
            包含书籍对象的列表和总页数
        """
        session = self.Session()
        try:
            # 计算总记录数和总页数
            total_count = session.query(Book).count()
            total_pages = (total_count + page_size - 1) // page_size  # 向上取整
            
            # 如果请求的页码超出范围，返回最后一页
            if page < 1:
                page = 1
            elif page > total_pages and total_pages > 0:
                page = total_pages
                
            # 计算偏移量
            offset = (page - 1) * page_size
            
            # 查询指定页的数据
            books = session.query(Book).order_by(Book.id).offset(offset).limit(page_size).all()
            
            return {
                "books": books,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
                "total_count": total_count
            }
        finally:
            session.close()

    def delete_book(self, book_name: str) -> bool:
        """删除指定名称的书籍"""
        session = self.Session()
        try:
            book = session.query(Book).filter_by(book_name=book_name).first()
            if book:
                session.delete(book)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"删除书籍失败: {str(e)}")
            return False
        finally:
            session.close()

    def update_book(self, book_name: str, **kwargs) -> bool:
        """更新书籍信息"""
        session = self.Session()
        try:
            book = session.query(Book).filter_by(book_name=book_name).first()
            if book:
                for key, value in kwargs.items():
                    if hasattr(book, key):
                        setattr(book, key, value)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"更新书籍失败: {str(e)}")
            return False
        finally:
            session.close()
            
    def get_book_by_id(self, book_id: str) -> Book:
        """根据书籍ID查询书籍信息
        
        Args:
            book_id: 书籍ID
            
        Returns:
            Book对象，如果未找到则返回None
        """
        session = self.Session()
        try:
            return session.query(Book).filter_by(book_id=book_id).first()
        finally:
            session.close()
            
    def get_book_by_author(self, author: str) -> list:
        """根据作者名查询书籍列表
        
        Args:
            author: 作者名
            
        Returns:
            包含Book对象的列表
        """
        session = self.Session()
        try:
            # 使用LIKE进行模糊匹配，支持部分作者名查询
            return session.query(Book).filter(Book.book_author.like(f"%{author}%")).all()
        finally:
            session.close()

    def get_book_by_tags(self, tags: list) -> list:
        """根据标签列表查询书籍
        
        Args:
            tags: 标签列表，可以包含一个或多个标签
            
        Returns:
            包含Book对象的列表
        """
        session = self.Session()
        try:
            # 如果标签列表为空，返回空列表
            if not tags:
                return []
                
            # 构建查询 - 先获取所有书籍
            all_books = session.query(Book).filter(
                Book.book_tags.isnot(None), 
                Book.book_tags != ''
            ).all()
            
            # 过滤匹配所有指定标签的书籍
            matched_books = []
            for book in all_books:
                if book.book_tags:
                    # 将书籍标签拆分为列表
                    book_tag_list = book.book_tags.split()
                    
                    # 检查是否包含所有指定的标签
                    match = True
                    for tag in tags:
                        if tag and tag.strip():  # 确保标签不为空
                            # 检查标签是否在书籍标签列表中（精确匹配）
                            if tag.strip() not in book_tag_list:
                                match = False
                                break
                    
                    if match:
                        matched_books.append(book)
            
            return matched_books
        except Exception as e:
            print(f"通过标签查询书籍失败: {str(e)}")
            return []
        finally:
            session.close()
    
    def get_all_tags(self) -> list:
        """获取所有书籍的标签列表（去重）
        
        Returns:
            包含所有唯一标签的列表
        """
        session = self.Session()
        try:
            # 获取所有非空标签
            books_with_tags = session.query(Book.book_tags).filter(
                Book.book_tags.isnot(None), 
                Book.book_tags != ''
            ).all()
            
            # 提取所有标签并去重
            all_tags = set()
            for book_tags in books_with_tags:
                if book_tags[0]:  # 确保标签不为None
                    # 假设标签以空格分隔
                    tags = book_tags[0].split()
                    all_tags.update(tags)
            
            return sorted(list(all_tags))  # 返回排序后的标签列表
        except Exception as e:
            print(f"获取所有标签失败: {str(e)}")
            return []
        finally:
            session.close()