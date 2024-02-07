from lxml import etree
import pandas as pd
import tkinter
from pyppeteer import launch
import asyncio, random
from datetime import datetime
import sqlalchemy


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
        url = 'https://www.yiwugo.com/'
        product = 'iPhone 14 Pro手机壳'
        # 登录网站
        await page.goto(url)
        # 反屏蔽绕过WebDriver检测
        await page.evaluateOnNewDocument(
            '''() =>{ Object.defineProperties(navigator, { webdriver: { get: () => false } }) }''')
        await asyncio.sleep(10)
        # 找到输入框输入商品信息
        await page.type('#searchform > div.search-index > #inputkey', product,
                        {'delay': self.input_time_random() - 50})
        await asyncio.sleep(3)
        # 点击搜索
        await page.click('#searchform > div.search-index > span.search-button')
        await asyncio.sleep(5)
        # 获取html源代码
        content = await page.content()
        html = etree.HTML(content)
        # 获取页码
        a_elems = html.xpath('//div[@id="newframe"]//div[@class="page_right"]/ul/a')
        a_page = len(a_elems) - 1
        a_xpath = '//div[@id="newframe"]//div[@class="page_right"]/ul/a[{}]/text()'.format(a_page)
        print(a_xpath)
        page_nums = html.xpath(a_xpath)[0]
        # page_nums = html.xpath('//div[@id="newframe"]//div[@class="page_right"]/ul/a[5]/text()')[0]
        # page_nums = 2
        print(page_nums)
        for i in range(int(page_nums)):
            await asyncio.sleep(6)
            content = await page.content()
            url = page.url
            print(i, url)
            html = etree.HTML(content)
            self.parse_html(html)
            if i == (int(page_nums) - 1):
                break
            # 翻页
            selector = '#newframe > div > div > div.bord_list_page.mb10px > div.page_right > ul > a.page_next_yes'

            # print(selector)

            await page.click(selector)

        df = pd.DataFrame(self.data_list)
        # 数据存到当前excel目录
        today = datetime.today().strftime("%Y-%m-%d")
        excel_path = './excel/{}_{}.xlsx'.format(product, today)
        df.to_excel(excel_path, index=False)
        # 数据存到mysql数据库中
        # engine = sqlalchemy.create_engine("mysql+pymysql://root:apexsoft@192.168.10.101:3306/test?charset=utf8")
        # df.to_sql(name="geshow", con=engine, if_exists="replace", index=True)
        # print("数据插入完成~")
        # 关闭浏览器
        await asyncio.sleep(15)
        await browser.close()

    def parse_html(self, html):
        div_list = html.xpath('//*[@id="newframe"]/div/div/div[@class="bcfff"]/div[3]/div')
        # '//*[@id="newframe"]/div/div[2]/div[@class="bcfff"]/div[3]/div'
        # '//*[@id="newframe"]/div/div/div[2]/div[3]/div'
        data_df = []
        domain = 'https://www.yiwugo.com'
        for div in div_list:
            items = {}
            try:

                items["name"] = div.xpath('.//a[@class="productloc"]/@title')[0]
                # 处理价格间的空格
                price_text = div.xpath('.//ul/li[@class="mt5px search13_price"]/span[@class="pri-left"]/em//text()')
                items["price"] = ''.join(price_text).strip()
                # 处理批发量的空格回车制表符
                wholesale_list = div.xpath('.//span[@class="pri-right"]/span/text()')
                wholesale = [item.strip().replace("\n", "").replace("\t", "").replace(" ", "") for item in
                             wholesale_list]
                wholesale_num = ''.join(wholesale)
                # 处理已销售数量的空格回车制表符
                sales_list = div.xpath('.//span[@class="xiaoliang"]/text()')
                sales = [item.strip().replace("\n", "").replace("\t", "") for item in sales_list]
                sales_count = ''.join(sales)

                items["wholesale_nums"] = wholesale_num + sales_count
                # 获取发货时间
                if div.xpath('.//li[@class="product13_company"]/a/@title'):
                    items["delivery_time"] = div.xpath('.//li[@class="product13_company"]/a/@title')[0]
                else:
                    items["delivery_time"] = '无'
                # 获取店铺名字
                items["shop_name"] = div.xpath('.//font[@class="wid140"]/a/text()')[0]
                # 获取店铺地址
                items["shop_addr"] = div.xpath('.//li[@class="shshopname"]/text()')[0]
                # 获取商品购买链接
                items["url"] = domain + div.xpath('.//p[@class="imgsize"]/span/a[@class="productloc"]/@href')[0]
                # 获取采集日期
                items["etl_date"] = datetime.today().strftime("%Y-%m-%d")
                data_df.append(items)
                self.data_list.append(items)

            except Exception as e:
                print(e)

        print(data_df)

    def run(self):
        asyncio.get_event_loop().run_until_complete(self.main())


if __name__ == '__main__':
    col = Collecton()
    col.run()
