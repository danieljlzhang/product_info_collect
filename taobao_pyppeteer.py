from lxml import etree
import pandas as pd
import tkinter
from pyppeteer import launch
import asyncio, random
from datetime import datetime
import re
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
        url = 'https://www.taobao.com/'
        product = '电视盒子'
        # 登录网站
        await page.goto(url)
        # 反屏蔽绕过WebDriver检测
        await page.evaluateOnNewDocument(
            '''() =>{ Object.defineProperties(navigator, { webdriver: { get: () => false } }) }''')
        # await page.evaluateOnNewDocument('''() => {
        #         window.navigator.chrome = { runtime: {}, };
        #     }''')
        # await page.evaluateOnNewDocument('''() => {
        #         Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        #     }''')
        # await page.evaluateOnNewDocument('''() => {
        #         Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], });
        #     }''')
        await asyncio.sleep(10)
        # # 点击登录淘宝
        # await page.click('#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-sign > a.h')
        # await asyncio.sleep(3)
        # # 点击扫码登录
        # await page.click('#login > div.corner-icon-view.view-type-qrcode > i')
        # await asyncio.sleep(10)

        # # 输入账号
        # await page.type('#fm-login-id', '15678852442',
        #                 {'delay': self.input_time_random() - 50})
        # await asyncio.sleep(3)
        # # 输入密码
        # await page.type('#fm-login-password', 'zjl1452.911',
        #                 {'delay': self.input_time_random() - 50})
        # await asyncio.sleep(5)
        # 存储登录界面源代码
        # login_html = await page.content()
        # with open('./html/taobao.html', 'w', encoding='utf-8') as f:
        #     f.write(login_html)
        # 截图
        # await page.screenshot(path='./pic/taobao.png')
        # 滑动滑块
        # frame = page.frames.find(lambda f: f.name == 'baxia-dialog-content')
        # for frame in page.frames:
        #     if frame.name == 'baxia-dialog-content':
        #         await frame.hover("#nc_1_n1z")
        #         await page.mouse.down()
        #         await page.mouse.move(1200, 0, {'delay': 5000, 'steps': 50})
        #         await asyncio.sleep(3)
        #         await page.mouse.up()
        #         await asyncio.sleep(120)
        # 登录
        # await page.click('#login-form > div.fm-btn > button')
        # await asyncio.sleep(3)

        # 找到输入框输入商品信息
        await page.type('#J_TSearchForm > div.search-suggest-combobox > #q', product,
                        {'delay': self.input_time_random() - 50})
        await asyncio.sleep(3)
        # 点击搜索
        await page.click('#J_TSearchForm > div.search-button > button')
        await asyncio.sleep(5)
        # 获取html源代码
        content = await page.content()
        # print(content)
        html = etree.HTML(content)
        # 获取页码
        page_text = html.xpath('//*[@id="mainsrp-pager"]/div/div/div/div[@class="total"]/text()')[0]
        page_num = re.findall('\d+', page_text)[0]
        print(page_num)
        # a_xpath = '//div[@id="newframe"]//div[@class="page_right"]/ul/a[{}]/text()'.format(a_page)
        # page_nums = html.xpath(a_xpath)[0]
        page_nums = 2
        print(page_nums)
        for i in range(page_nums):
            await asyncio.sleep(8)
            content = await page.content()
            url = page.url
            print(i, url)
            html = etree.HTML(content)
            self.parse_html(html)
            if i == (page_nums - 1):
                break
            # 翻页
            selector = '#mainsrp-pager > div > div > div > ul > li.item.next > a'
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
        div_list = html.xpath('//*[@id="mainsrp-itemlist"]/div/div/div[@class="items"]/div')
        data_df = []
        for div in div_list:
            items = {}
            try:

                name_list = div.xpath('.//a[@class="J_ClickStat"]/text()')
                name_str = [item.strip() for item in name_list]
                items["name"] = ''.join(name_str)
                # 处理价格间的空格
                price_text = div.xpath('.//div[@class="price g_price g_price-highlight"]/strong/text()')[0]
                items["price"] = ''.join(price_text).strip()
                # 处理批发量的空格回车制表符
                items["pay_nums"] = div.xpath('.//div[@class="deal-cnt"]/text()')[0]
                # 店铺名称
                items["shop_name"] = div.xpath('.//a[@class="shopname J_MouseEneterLeave J_ShopInfo"]/span[2]/text()')[0]
                # 店家地址
                items["shop_addr"] = div.xpath('.//div[@class="location"]/text()')[0]
                # 获取商品购买链接
                url_str = div.xpath('.//a[@class="J_ClickStat"]/@href')[0]
                if url_str.startswith('http'):
                    items["url"] = url_str
                else:
                    items["url"] = "https:" + url_str
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
