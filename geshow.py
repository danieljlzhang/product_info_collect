from lxml import etree
import pandas as pd
import tkinter
from pyppeteer import launch
import asyncio, random
from datetime import datetime
import sqlalchemy
import pymysql


class Collecton(object):

    def __init__(self):
        self.data_list = list()

    def screen_size(self):
        tk = tkinter.Tk()
        width = tk.winfo_screenwidth()
        height = tk.winfo_screenheight()
        tk.quit()
        return width, height

    def input_time_random(self):
        return random.randint(100, 200)

    async def main(self):
        browser = await launch(headless=False, userDataDir="./config",
                               args=['--disable-infobars', '--no-sandbox', '--start-maximized'])

        page = await browser.newPage()
        width, height = self.screen_size()
        await page.setViewport({'width': width, 'height': height})
        # 设置基本信息
        url = 'https://www.geshow.com/'
        product = '面膜'
        # 登录网站
        await page.goto(url)
        # 反屏蔽绕过WebDriver检测
        await page.evaluateOnNewDocument(
            '''() =>{ Object.defineProperties(navigator, { webdriver: { get: () => false } }) }''')
        await asyncio.sleep(10)
        # 找到输入框输入商品信息
        await page.type('#main-search > div > div.search-box > div.input-box.g-flex-str > input', product,
                        {'delay': self.input_time_random() - 50})
        await asyncio.sleep(3)
        # 点击搜索
        await page.click('#main-search > div > div.search-box > div.input-box.g-flex-str > a')
        await asyncio.sleep(5)
        # 获取html源代码
        content = await page.content()
        html = etree.HTML(content)
        # 获取页码
        a_elems = html.xpath('//div[@id="paging-box"]/a')
        page_nums = len(a_elems) - 2
        print(page_nums)
        for i in range(page_nums):
            await asyncio.sleep(2)
            content = await page.content()
            html = etree.HTML(content)
            self.parse_html(html)
            # 翻页
            selector = '#onsale > div > div.main-box.g-flex-betn > div.right-box > #paging-box  > a:nth-child({})'.format(
                i + 3)
            print(selector)
            await page.click(selector)

        df = pd.DataFrame(self.data_list)
        # 数据存到当前excel目录
        today = datetime.today().strftime("%Y-%m-%d")
        excel_path = './excel/{}_{}.xlsx'.format(product, today)
        df.to_excel(excel_path, index=False)
        # 数据存到mysql数据库中
        engine = sqlalchemy.create_engine("mysql+pymysql://root:apexsoft@192.168.10.101:3306/test?charset=utf8")
        df.to_sql(name="geshow", con=engine, if_exists="replace", index=True)
        print("数据插入完成~")
        # 关闭浏览器
        await asyncio.sleep(15)
        await browser.close()

    def parse_html(self, html):
        a_list = html.xpath('//*[@id="pro-excel-show"]/div')
        domain = 'https://www.geshow.com'
        data_df = []
        for a in a_list:
            items = {}
            items["name"] = a.xpath('.//a[@class="pro-desc overflow-clamp2"]/text()')[0]
            items["price"] = a.xpath('.//span[@class="price"]/text()')[0]
            items["url"] = domain + a.xpath('.//a[@class="pro-desc overflow-clamp2"]/@href')[0]
            items["etl_date"] = datetime.today().strftime("%Y-%m-%d")
            data_df.append(items)
            self.data_list.append(items)
        print(data_df)

    def run(self):
        asyncio.get_event_loop().run_until_complete(self.main())


if __name__ == '__main__':
    col = Collecton()
    col.run()
