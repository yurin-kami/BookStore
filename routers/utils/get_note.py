#encoding:utf-8
import random
from lxml import etree
import aiohttp
import asyncio
from db_rw import BookManager


class LightNote():
    def __init__(self) -> None:
        with open("routers/utils/lightnote_url.txt", "r", encoding="utf-8") as f:
            self.ids = f.readlines()
        self.page_urls = [f"https://www.wenku8.net/book/{id.strip()}.htm" 
        for id in self.ids]

        self.download_url = [f"https://dl.wenku8.com/down.php?type=utf8&node={random.randint(0,1)}&id={id.strip()}" 
        for id in self.ids]

        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
            "Cookie": "__51vcke__1xtyjOqSZ75DRXC0=22aeb0e4-7cc3-5499-8d24-8f3639a73222; __51vuft__1xtyjOqSZ75DRXC0=1744620561951; cf_clearance=ujqM3VgzFhQute6GzWAG1An3hF2xQC_PwEk_We5ozTU-1744682253-1.2.1.1-sHGc7oW4gCpIa.jIKrUvYWfflpaKqBVxh7XT01Cyf2rFyvGwQMsxKYYq602iLovoPHKhuDL.aBUmF6f1iKq9nUWYmptfDNfk6Azb9_CFjg53RSawEIdwu66_VlUeVvtVHUrkTuOGIqXHfjSP_1S5sDhAWNppcDdgIxlIWDNTeKpw_I6I3ryB9pILHMWuekiKgP40lQUgUegOkXiZX0Y5irgqmmo6Ok_d_DxPJGlDVdELq4NmcbqESrmj__khl2eIkwnIHbkAfWQrQlI3cLCPxfxEmGBxClJDI_VjC3B9LIbrdKkvha9cf1ZzxvTPayGFIFZVoMi1UzDFVu_UcZvfn0Q5GVYoFqKtMMp3jfrBlP8; Hm_lvt_acfbfe93830e0272a88e1cc73d4d6d0f=1744712828; Hm_lvt_d72896ddbf8d27c750e3b365ea2fc902=1744594749,1744617691,1744770224; HMACCOUNT=C7E5F6AD667AC788; _clck=1cjch7o%7C2%7Cfv4%7C0%7C1930; PHPSESSID=15978a539b9c21b882c48824bedf2c5a; jieqiUserInfo=jieqiUserId%3D738650%2CjieqiUserName%3Dyu9yu%2CjieqiUserGroup%3D3%2CjieqiUserVip%3D0%2CjieqiUserName_un%3Dyu9yu%2CjieqiUserHonor_un%3D%26%23x666E%3B%26%23x901A%3B%26%23x4F1A%3B%26%23x5458%3B%2CjieqiUserGroupName_un%3D%26%23x666E%3B%26%23x901A%3B%26%23x4F1A%3B%26%23x5458%3B%2CjieqiUserLogin%3D1745029994%2CjieqiUserPassword%3D6fe839fce1c947ea47d428e3ada191db; jieqiVisitInfo=jieqiUserLogin%3D1745029994%2CjieqiUserId%3D738650; jieqiVisitId=article_articleviews%3D3103; Hm_lpvt_d72896ddbf8d27c750e3b365ea2fc902=1745029989; __vtins__1xtyjOqSZ75DRXC0=%7B%22sid%22%3A%20%220e2110d1-c7e3-574c-9777-a3a1f3adaf92%22%2C%20%22vd%22%3A%201%2C%20%22stt%22%3A%200%2C%20%22dr%22%3A%200%2C%20%22expires%22%3A%201745031788798%2C%20%22ct%22%3A%201745029988798%7D; __51uvsct__1xtyjOqSZ75DRXC0=7"
            }
    async def get_page(self) -> dict:
        """获取页面内容并解析返回字典格式的值列表"""
        book_covers = []
        book_authors = []
        book_names = []
        book_synopsis = []  # 添加简介列表
        book_tags = []  # 添加标签列表
        
        async with aiohttp.ClientSession(headers=self.header) as session:
            tasks = []
            for url in self.page_urls:
                tasks.append(self.fetch_page(session, url))
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤掉异常和None值并处理结果
            for result in results:
                if isinstance(result, Exception):
                    print(f"任务执行出错: {str(result)}")
                    continue
                if result:
                    book_covers.append(result['cover'])
                    book_authors.append(result['author'])
                    book_names.append(result['name'])
                    book_synopsis.append(result.get('synopsis', ''))  # 获取简介，如果没有则为空字符串
                    book_tags.append(result.get('tags', ''))  # 获取标签，如果没有则为空字符串

        return {
            'ids': [id.strip() for id in self.ids],
            'covers': book_covers,
            'authors': book_authors,
            'names': book_names,
            'synopsis': book_synopsis,  # 添加简介到返回值
            'tags': book_tags  # 添加标签到返回值
        }

    async def fetch_page(self, session, url, max_retries=3):
        """获取单个页面内容并解析，失败时最多重试3次"""
        retries = 0
        while retries < max_retries:
            try:
                async with session.get(url, timeout=60) as response:
                    if not response.ok:
                        raise aiohttp.ClientError(f"HTTP状态码错误: {response.status}")
                    
                    # 获取和解码页面内容
                    content = await response.read()
                    text = content.decode('gbk', errors='ignore')
                    # print(text)
                    # 解析HTML并提取数据
                    tree = etree.HTML(text)
                    
                    # 获取封面图片地址
                    cover = tree.xpath('//img[contains(@src, "/image/") and contains(@src, ".jpg")]/@src')
                    cover_url = cover[0] if cover else ''
                    # print(cover)
                    
                    # 获取作者
                    author = tree.xpath('//td[contains(text(), "小说作者：")]/text()')
                    author_name = author[0].replace('小说作者：', '').strip() if author else ''
                    # print(author_name)
                    
                    # 获取书名
                    name = tree.xpath('//span[contains(@style, "font-size:16px")]/b/text()')
                    book_name = name[0].strip() if name else ''
                    # print(book_name)
                    
                    # 获取作品Tags
                    tags_element = tree.xpath('//span[@class="hottext" and contains(text(), "作品Tags：")]/b/text()')
                    tags = tags_element[0].replace('作品Tags：', '').strip() if tags_element else ''
                    # 如果上面的xpath没有找到，尝试另一种定位方式
                    if not tags:
                        tags_element = tree.xpath('//span[contains(@style, "font-size:13px")]/b[contains(text(), "作品Tags：")]/text()')
                        tags = tags_element[0].replace('作品Tags：', '').strip() if tags_element else ''
                    # print(tags)

                    # 获取内容简介
                    synopsis_container = tree.xpath('//span[@class="hottext" and contains(text(), "内容简介：")]/following-sibling::span[1]')

                    if synopsis_container:
                        # 获取所有文本节点，包括<br>标签分隔的文本
                        synopsis_texts = synopsis_container[0].xpath('.//text()')
                        # 过滤空白文本并连接
                        synopsis = ''.join([text.strip() for text in synopsis_texts if text.strip()])
                    else:
                        synopsis = ''
                    
                    # print(f"成功解析页面: {url}")
                    return {
                        'cover': cover_url,
                        'author': author_name,
                        'name': book_name,
                        'synopsis': synopsis,  # 添加简介到返回结果
                        'tags': tags  # 添加标签到返回结果
                    }
                    
            except (aiohttp.ClientError, UnicodeDecodeError) as e:
                print(f"页面内容获取失败: {url}, 错误: {str(e)}, 正在重试 {retries + 1}/{max_retries}")
            except Exception as e:
                print(f"页面解析失败: {url}, 错误: {str(e)}, 正在重试 {retries + 1}/{max_retries}")
            
            retries += 1
            if retries < max_retries:
                await asyncio.sleep(2 * retries)
                
        return None

    async def get_note(self) -> dict:
        """获取小说内容字典"""
        async with aiohttp.ClientSession(headers=self.header) as session:
            tasks = []
            for url in self.download_url:
                tasks.append(self.fetch_note(session, url))
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # 过滤掉异常和None值并返回结果
            return {"book_txt":[n for n in results if n is not None and not isinstance(n, Exception)]}

    async def fetch_note(self, session, url, max_retries=3):
        """获取单个小说内容,失败时最多重试3次"""
        retries = 0
        while retries < max_retries:
            try:
                async with session.get(url, timeout=60, allow_redirects=False) as response:
                    # 如果是重定向响应
                    if response.status in [301, 302, 303, 307, 308,429]:
                        redirect_url = response.headers.get('Location')
                        if redirect_url:
                            # print(f"正在重定向到: {redirect_url}")
                            # 访问重定向后的URL
                            async with session.get(redirect_url, timeout=30) as redirect_response:
                                if redirect_response.ok or redirect_response.status == 429:
                                    content = await redirect_response.read()
                                    text = content.decode('utf-8', errors='ignore')
                                    if len(text) > 400:
                                        # print(f"成功下载小说: {url}")
                                        return text
                                    else:
                                        print(f"下载内容过短: {url}, 长度: {len(text)}, 正在重试 {retries + 1}/{max_retries}")
                                else:
                                    print(f"重定向后请求失败: {redirect_response.status}")
                        else:
                            print(f"未找到重定向URL: {url}")
                    
                    # 如果是正常响应
                    elif response.ok:
                        content = await response.read()
                        text = content.decode('utf-8', errors='ignore')
                        if len(text) > 100:
                            # print(f"成功下载小说: {url}")
                            return text
                        else:
                            print(f"下载内容过短: {url}, 长度: {len(text)}, 正在重试 {retries + 1}/{max_retries}")
                    else:
                        print(f"HTTP状态码错误: {response.status}, URL: {url}, 正在重试 {retries + 1}/{max_retries}")
                        
            except Exception as e:
                print(f"下载小说失败: {url}, 错误: {str(e)}, 正在重试 {retries + 1}/{max_retries}")
            
            retries += 1
            if retries < max_retries:
                await asyncio.sleep(2 * retries)
        
        print(f"已达到最大重试次数 {max_retries}，下载失败: {url}")
        return None

    async def save_to_db(self, max_retries=3):
        """保存数据到数据库，失败时自动重试"""
        retries = 0
        while retries < max_retries:
            try:
                # 获取页面信息和小说内容
                if retries == 0:  # 只在第一次尝试时获取数据
                    page_info = await self.get_page()
                    notes = await self.get_note()
                
                # 创建BookManager实例并保存数据
                book_manager = BookManager()
                if book_manager.insert_books(page_info, notes):
                    print("数据成功保存到数据库")
                    return True
                else:
                    print("数据保存失败，准备重试")
                    
            except Exception as e:
                if "MySQL server has gone away" in str(e) or "软件中止了一个已建立的连接" in str(e):
                    print(f"数据库连接断开，正在重试 {retries + 1}/{max_retries}")
                    await asyncio.sleep(2 * (retries + 1))  # 指数退避
                else:
                    print(f"保存数据时发生错误: {str(e)}")
                    return False
            
            retries += 1
            
        print(f"已达到最大重试次数 {max_retries}，数据保存失败")
        return False

async def test_save_data():
    """测试爬取并保存数据"""
    try:
        ln = LightNote()
        if await ln.save_to_db():
            print("数据保存测试完成")
        else:
            print("数据保存测试失败")
    except Exception as e:
        print(f"数据保存测试失败: {str(e)}")

async def test_update_books():
    """测试爬取数据并更新已有书籍信息"""
    try:
        ln = LightNote()
        # 获取页面信息
        page_info = await ln.get_page()
        
        if not page_info or not page_info['ids']:
            print("未获取到任何书籍信息，无法进行更新")
            return False
        
        # 创建BookManager实例
        book_manager = BookManager()
        
        # 获取所有书籍ID和名称
        ids = page_info.get('ids', [])
        names = page_info.get('names', [])
        authors = page_info.get('authors', [])
        covers = page_info.get('covers', [])
        synopsis = page_info.get('synopsis', [])
        tags = page_info.get('tags', [])
        
        # 计算有效数据长度
        valid_count = min(len(ids), len(names))
        if valid_count == 0:
            print("没有有效的书籍数据可更新")
            return False
        
        update_count = 0
        insert_count = 0
        
        for i in range(valid_count):
            book_id = ids[i].strip()
            book_name = names[i]
            
            # 检查必要字段是否为空
            if not book_id or not book_name:
                print(f"第 {i+1} 条数据不完整，跳过")
                continue
            
            # 准备更新数据
            update_data = {}
            
            # 只更新有值的字段
            if i < len(authors) and authors[i]:
                update_data['book_author'] = authors[i]
            
            if i < len(covers) and covers[i]:
                update_data['book_cover'] = covers[i]
            
            if i < len(synopsis) and synopsis[i]:
                update_data['book_synopsis'] = synopsis[i]
            
            if i < len(tags) and tags[i]:
                update_data['book_tags'] = tags[i]
            
            # 查询数据库中是否存在该书籍
            existing_book = book_manager.get_book_by_id(book_id)
            
            if existing_book:
                # 如果书籍存在，执行更新
                if update_data:
                    if book_manager.update_book(existing_book.book_name, **update_data):
                        update_count += 1
                        print(f"成功更新书籍: {book_name}")
                    else:
                        print(f"更新书籍失败: {book_name}")
            else:
                # 如果书籍不存在，尝试插入新书籍
                try:
                    # 构建新书籍数据
                    book_data = {
                        'ids': [book_id],
                        'names': [book_name],
                        'authors': [update_data.get('book_author', '')],
                        'covers': [update_data.get('book_cover', '')],
                        'synopsis': [update_data.get('book_synopsis', '')],
                        'tags': [update_data.get('book_tags', '')]
                    }
                    
                    # 获取书籍内容
                    book_txt_url = f"https://dl.wenku8.com/down.php?type=utf8&node={random.randint(0,1)}&id={book_id}"
                    async with aiohttp.ClientSession(headers=ln.header) as session:
                        book_txt = await ln.fetch_note(session, book_txt_url)
                    
                    notes = {"book_txt": [book_txt] if book_txt else []}
                    
                    # 插入新书籍
                    if book_manager.insert_books(book_data, notes):
                        insert_count += 1
                        print(f"成功插入新书籍: {book_name}")
                    else:
                        print(f"插入新书籍失败: {book_name}")
                except Exception as e:
                    print(f"插入新书籍时出错: {book_name}, 错误: {str(e)}")
        
        print(f"更新完成，共更新 {update_count} 本书籍，新增 {insert_count} 本书籍")
        return update_count > 0 or insert_count > 0
    
    except Exception as e:
        print(f"更新书籍测试失败: {str(e)}")
        return False

# 添加一个可选的更新书籍内容的方法
async def test_update_book_content():
    """测试爬取并更新书籍内容"""
    try:
        ln = LightNote()
        # 获取小说内容
        notes = await ln.get_note()
        
        if not notes or not notes['book_txt']:
            print("未获取到任何书籍内容，无法进行更新")
            return False
        
        # 获取书籍ID列表
        ids = [id.strip() for id in ln.ids]
        book_txts = notes['book_txt']
        
        # 计算有效数据长度
        valid_count = min(len(ids), len(book_txts))
        if valid_count == 0:
            print("没有有效的书籍内容可更新")
            return False
        
        # 创建BookManager实例
        book_manager = BookManager()
        
        update_count = 0
        for i in range(valid_count):
            book_id = ids[i]
            book_txt = book_txts[i]
            
            # 检查必要字段是否为空
            if not book_id or not book_txt:
                print(f"第 {i+1} 条数据不完整，跳过")
                continue
            
            # 查询数据库中是否存在该书籍
            existing_book = book_manager.get_book_by_id(book_id)
            if not existing_book:
                print(f"书籍ID {book_id} 不存在，跳过更新")
                continue
            
            # 更新书籍内容
            if book_manager.update_book(existing_book.book_name, book_txt=book_txt):
                update_count += 1
                print(f"成功更新书籍内容: {existing_book.book_name}")
            else:
                print(f"更新书籍内容失败: {existing_book.book_name}")
        
        print(f"更新完成，共更新 {update_count} 本书籍内容")
        return update_count > 0
    
    except Exception as e:
        print(f"更新书籍内容测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    # 添加新的测试选项
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "update":
        # 运行更新测试
        asyncio.run(test_update_books())
    elif len(sys.argv) > 1 and sys.argv[1] == "update_content":
        # 运行更新内容测试
        asyncio.run(test_update_book_content())
    else:
        # 默认运行保存测试
        asyncio.run(test_save_data())
