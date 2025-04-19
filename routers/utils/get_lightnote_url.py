# -*- coding: utf-8 -*-
import re
import asyncio,time
from aiohttp import ClientSession

class GetLightNote:
    def __init__(self):
        self.url = [f"https://www.wenku8.net/book/{id}.htm" for id in range(1,9999)]
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.26",
            "Cookie": "_clck=1cjch7o%7C2%7Cfv2%7C0%7C1930; jieqiVisitId=article_articleviews%3D691%7C1508; Hm_lvt_d72896ddbf8d27c750e3b365ea2fc902=1744594749,1744617691; HMACCOUNT=EFEF2E287DE7E24E; PHPSESSID=6f0614032633dc52f8122941a0060491; jieqiUserInfo=jieqiUserId%3D738650%2CjieqiUserName%3Dyu9yu%2CjieqiUserGroup%3D3%2CjieqiUserVip%3D0%2CjieqiUserName_un%3Dyu9yu%2CjieqiUserHonor_un%3D%26%23x666E%3B%26%23x901A%3B%26%23x4F1A%3B%26%23x5458%3B%2CjieqiUserGroupName_un%3D%26%23x666E%3B%26%23x901A%3B%26%23x4F1A%3B%26%23x5458%3B%2CjieqiUserLogin%3D1744617709%2CjieqiUserPassword%3D6fe839fce1c947ea47d428e3ada191db; jieqiVisitInfo=jieqiUserLogin%3D1744617709%2CjieqiUserId%3D738650; cf_clearance=YiG23QxnaNklXbB4CcqTrOCwb9cw4eA9Y2PnzThF8Dk-1744618252-1.2.1.1-7aZz2_UJ18eQZA5FBqfqgmvwLYKSA5dmgJjKgXTvemUqM3jogkGNqMltAW4IFEwh0l.80fnMyk4Na5UhvzeOmGsKOYLqACkWYIzRSqdnyFRWjsBR0o0zzFw3CvSeuapUvnXTdad1.z0Gs60HO6ugt1GqstzUmH.ntKOb6Zgz3pwZKT9qTmskpoEeiRb.bv1dLXYcBPsBwGvFma8WQZ8FOtosrSFsonZWMAkNcDsI87vch2ewONa3548xkjRteKlIvrZRdZhMObvYAb2YHIzVgcyuV6cRAsDIi22DsTLkcDjvh3EzM1Y.E2.Gx3sE8NAMqoD6WJ4_yQQ_40vNhfcoDWw2ExGw1.OLq31uzJk322A; _clsk=16k2dj4%7C1744618235647%7C2%7C1%7Cp.clarity.ms%2Fcollect; Hm_lpvt_d72896ddbf8d27c750e3b365ea2fc902=1744618282"
        }
    async def get_url(self, url):
        try:
            async with ClientSession() as session:
                async with session.get(url=url, headers=self.header) as res:
                    if 200 <= res.status <= 302 or res.status == 429:
                        # 尝试使用 GBK 编码读取内容
                        html = await res.read()
                        html = html.decode('gbk', errors='ignore')
                        if '<title>出现错误</title>' in html:
                            return None
                        print(f"找到有效链接: {url}")
                        return url
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            return None

    async def main(self):
        # 分批处理，每批50个请求
        batch_size = 50
        valid_urls = []
        total_batches = len(self.url) // batch_size + 1
        current_batch = 0
        
        for i in range(0, len(self.url), batch_size):
            current_batch += 1
            batch = self.url[i:i+batch_size]
            tasks = [self.get_url(url) for url in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 直接添加有效的URL
            valid_urls.extend([url for url in batch_results if url])
            print(f"批次 {current_batch}/{total_batches} 完成，当前找到 {len(valid_urls)} 个有效链接")
            await asyncio.sleep(0.5)  # 增加等待时间，避免请求过快
            
        return valid_urls
    def write_file(self):
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(self.main())
        with open("lightnote_url.txt", "a", encoding="utf-8") as f:
            for url in res:
                if url and isinstance(url, str):  # 确保url是字符串类型
                    try:
                        id_match = re.findall(r"book/(\d+)\.htm", url)
                        if id_match:
                            f.write(f"{id_match[0]}\n")
                    except Exception as e:
                        print(f"Error processing URL {url}: {str(e)}")
if __name__ == '__main__':
    start = time.time()
    GetLightNote().write_file()
    end = time.time()
    print("耗时",end-start,"s")