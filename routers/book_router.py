from fastapi import APIRouter, HTTPException
from utils.db_rw import BookManager
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

router = APIRouter()
book_manager = BookManager()

class Book(BaseModel):
    title: str
    author: str
    bookname: str
    book_id: str
    tags: List[str]

class BookIdRequest(BaseModel):
    book_id: str

@router.post("/all_book/tags")
async def get_books_by_tags(book: Book):
    """
    根据标签列表查询书籍
    
    参数:
    - tags: 标签列表，可以包含一个或多个标签
    
    返回:
    - 包含匹配所有标签的书籍列表
    """
    # 确保标签列表不为空
    if not book.tags:
        raise HTTPException(status_code=400, detail="标签列表不能为空")
    
    # 调用数据库方法查询书籍
    books = book_manager.get_book_by_tags(book.tags)
    
    if not books:
        raise HTTPException(status_code=404, detail="未找到包含所有指定标签的书籍")
    
    # 将多本书籍转换为列表返回
    books_list = []
    for book_item in books:
        books_list.append({
            "book_id": book_item.book_id,
            "book_name": book_item.book_name,
            "book_author": book_item.book_author,
            "book_cover": book_item.book_cover,
            "book_tags": book_item.book_tags,
            "book_synopsis": book_item.book_synopsis
        })
    
    return {"books": books_list}

@router.get("/book/tags")
async def get_all_tags():
    """
    获取所有书籍标签
    
    返回:
    - 所有唯一标签的列表
    """
    tags = book_manager.get_all_tags()
    return {"tags": tags}

@router.get("/all_books/{page}")
async def get_books(page: int):
    """
    获取指定页码的书籍列表
    
    参数:
    - page: 页码，从1开始
    
    返回:
    - 包含书籍列表和分页信息的字典
    """
    result = book_manager.get_one_page(page)
    
    # 将 SQLAlchemy 对象转换为字典
    books_list = []
    for book in result["books"]:
        books_list.append({
            # "id": book.id,
            "book_author": book.book_author,
            "book_name": book.book_name,
            "book_cover": book.book_cover,
            "book_id": book.book_id,
            "book_tags": book.book_tags,  # 添加标签字段
            "book_synopsis": book.book_synopsis
        })
    
    return {
        "books": books_list,
    }

@router.post("/book/search/name")
async def search_book_by_name(book: Book):
    print(book.bookname)
    """
    根据书名搜索书籍
    
    参数:
    - bookname: 书籍名称
    
    返回:
    - 书籍信息列表
    """
    books = book_manager.get_book_by_name(book.bookname)
    if not books:
        raise HTTPException(status_code=404, detail="未找到相关书籍")
    
    # 将多本书籍转换为列表返回
    books_list = []
    for book in books:
        books_list.append({
            "book_id": book.book_id,
            "book_name": book.book_name,
            "book_author": book.book_author,
            "book_cover": book.book_cover,
            "book_tags": book.book_tags,  # 添加标签字段
            "book_synopsis": book.book_synopsis
        })
    
    return {"books": books_list}

@router.post("/book/search/author")
async def search_books_by_author(book: Book):
    print(book.author)
    """
    根据作者搜索书籍
    
    参数:
    - author: 作者名
    
    返回:
    - 包含该作者所有书籍的列表
    """
    books = book_manager.get_book_by_author(book.author)
    if not books:
        raise HTTPException(status_code=404, detail="未找到该作者的书籍")
    
    # 将多本书籍转换为列表返回
    books_list = []
    for book in books:
        books_list.append({
            "book_id": book.book_id,
            "book_name": book.book_name,
            "book_author": book.book_author,
            "book_cover": book.book_cover,
            "book_tags": book.book_tags,  # 添加标签字段
            "book_synopsis": book.book_synopsis
        })
    
    return {"books": books_list}

# @router.post("/book/detail")
# async def get_book_detail(request: BookIdRequest):
#     """
#     根据书籍ID获取书籍详细信息
    
#     参数:
#     - book_id: 书籍ID
    
#     返回:
#     - 书籍的完整信息
#     """
#     if not request.book_id:
#         raise HTTPException(status_code=400, detail="书籍ID不能为空")
    
#     book = book_manager.get_book_by_id(request.book_id)
#     if not book:
#         raise HTTPException(status_code=404, detail="未找到该书籍")
    
#     # 返回书籍的完整信息
#     return {
#         "book_id": book.book_id,
#         "book_name": book.book_name,
#         "book_author": book.book_author,
#         "book_cover": book.book_cover,
#         "book_tags": book.book_tags,
#         "book_synopsis": book.book_synopsis,
#         "book_txt": book.book_txt  # 包含书籍全文
#     }

@router.post("/book/detail")
async def get_book_detail_by_id(book: Book):
    """
    根据书籍ID获取书籍详细信息
    
    参数:
    - book_id: 书籍ID（路径参数）
    
    返回:
    - 书籍的完整信息
    """
    if not book.book_id:
        raise HTTPException(status_code=400, detail="书籍ID不能为空")
    
    book = book_manager.get_book_by_id(book.book_id)
    if not book.book_id:
        raise HTTPException(status_code=404, detail="未找到该书籍")
    
    # 返回书籍的完整信息
    return {
        "book_id": book.book_id,
        "book_name": book.book_name,
        "book_author": book.book_author,
        "book_cover": book.book_cover,
        "book_tags": book.book_tags,
        "book_synopsis": book.book_synopsis,
        "book_txt": book.book_txt  # 包含书籍全文
    }

@router.post("/book/content")
async def get_book_content(book: Book):
    """
    获取书籍正文内容
    
    参数:
    - book_id: 书籍ID
    
    返回:
    - 书籍的正文内容
    """
    if not book.book_id:
        raise HTTPException(status_code=400, detail="书籍ID不能为空")
    
    book_data = book_manager.get_book_by_id(book.book_id)
    # print(book_data.book_txt)
    if not book_data:
        raise HTTPException(status_code=404, detail="未找到该书籍")
    
    # 返回书籍正文
    return {
        "book_id": book_data.book_id,
        "book_name": book_data.book_name,
        "book_txt": book_data.book_txt
    }
