from datetime import datetime
from time import sleep
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By


class taobao(object):

    def __init__(self):
        self.data_list = list()


    def login(self, user, pwd):

        # 配置chrome 防止出现滑块验证
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("prefs",
                                        {"credentials_enable_service": False, "profile.password_manager_enabled": False})
        driver = webdriver.Chrome(options=options)
        with open('util/stealth.min.js') as f:
            script = f.read()
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script})
        sleep(2)
        driver.maximize_window()  # 窗口最大化，防止元素重叠无法点击

        driver.get("http://www.taobao.com/")
        sleep(10)
        # 获取登录按钮并点击
        login_button1 = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[2]/div[2]/div[5]/div/div[2]/div[1]/a[1]')
        login_button1.click()

        # 点击登录按钮，会跳转至登录页面需要重定位活跃窗口
        driver.switch_to.window(driver.window_handles[-1])
        driver.implicitly_wait(15)  # 等待网页加载

        # 获取用户名、密码input以及登录button
        username_input = driver.find_element(By.XPATH, '/html/body/div/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div[2]/input')
        password_input = driver.find_element(By.XPATH, '/html/body/div/div[2]/div[3]/div/div/div/div[2]/div/form/div[2]/div[2]/input')
        login_button2 = driver.find_element(By.XPATH,  '/html/body/div/div[2]/div[3]/div/div/div/div[2]/div/form/div[4]/button')

        # 输入用户名密码并单击登录按钮
        username = user
        password = pwd
        for char in username:
            username_input.send_keys(char)
            sleep(0.5)
        sleep(1)
        for char in password:
            password_input.send_keys(char)
            sleep(0.5)
        sleep(1)
        login_button2.click()
        print("登录完成！")
        driver.implicitly_wait(15)
        goods = '单反相机'
        if driver.find_element(By.XPATH, '//*[@id="q"]'):
            driver.find_element(By.XPATH, '//*[@id="q"]').send_keys(goods)
            sleep(1)
            driver.find_element(By.XPATH, '//*[@id="J_TSearchForm"]/div[1]/button').click()
        # 切换页面
        # driver.switch_to.window(driver.window_handles[-1])
        driver.implicitly_wait(15)
        totalpage= ''
        while True:
            try:
                self.parse_data(driver)
                driver.implicitly_wait(15)
                # 'class="J_Ajax num icon-tag"'
                nextpage = driver.find_element(By.XPATH, '//a[contains(@class, "J_Ajax") and contains(@class, "num") and contains(@class, "icon-tag")]')
                print(nextpage.get_attribute("href"))
                # 判断是否尾页，尾页的下一页button，class类为“pagination-disabled pagination-next”，非尾页的下一页button，class类为“pagination-next”
                if nextpage.get_attribute("href").strip() != '#':  # 若不为“pagination-next”则尾页，跳出死循环
                    break
                else:
                    driver.find_element(By.XPATH, '//*[@id="mainsrp-pager"]/div/div/div/ul/li[@class="item next"]/a').click()
                    sleep(3)
            except:
                break

        # 下一页
        # driver.find_element(By.XPATH, '//*[@id="mainsrp-pager"]/div/div/div/ul/li[8]/a').click()
        print("页面抓取完毕")
        df = pd.DataFrame(self.data_list)
        # 数据存到当前excel目录
        today = datetime.now().strftime("%Y-%m-%d")
        excel_path = './excel/{}_{}.xlsx'.format(goods, today)
        df.to_excel(excel_path, index=False)
        # 关闭浏览器
        driver.close()

    def parse_data(self, driver):
        div_list = driver.find_elements(By.XPATH, '//*[@id="mainsrp-itemlist"]/div/div/div[1]/div')
        data_df = []
        for div in div_list:
            items = {}
            try:
                name_str = div.find_element(By.XPATH, './/a[@class="J_ClickStat"]').text
                items["name"] = ''.join(name_str)
                # 处理价格间的空格
                price_text = div.find_element(By.XPATH, './/div[@class="price g_price g_price-highlight"]/strong').text
                items["price"] = ''.join(price_text).strip()
                # 处理批发量的空格回车制表符
                items["pay_nums"] = div.find_element(By.XPATH, './/div[@class="deal-cnt"]').text
                # 店铺名称
                items["shop_name"] = div.find_element(By.XPATH,
                                                      './/a[@class="shopname J_MouseEneterLeave J_ShopInfo"]/span[2]').text
                # 店家地址
                items["shop_addr"] = div.find_element(By.XPATH, './/div[@class="location"]').text
                # 获取商品购买链接
                url_str = div.find_element(By.XPATH, './/a[@class="J_ClickStat"]').get_attribute("href")
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


if __name__ == '__main__':
    user = '15678852442'
    pwd = 'zjl1452.911'
    zjl = taobao()
    zjl.login(user, pwd)
