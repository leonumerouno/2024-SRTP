from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
class HtmlDownloader(object):
    def download(self, url):
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument("--headless")
        s = Service('chromedriver.exe')

        driver = webdriver.Chrome(service=s, options=options)
        sleep(1)
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        driver.get(url)
        sleep(1)

        page_source = driver.page_source
        title = driver.title

        return page_source,title
    def download_edit_history(self, url):
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument('--headless=old --no-sandbox')
        options.add_argument("--log-level=INFO")
        s = Service('chromedriver.exe')

        driver = webdriver.Chrome(service=s, options=options)
        sleep(5)
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        driver.get(url)
        driver.refresh()

        sleep(5)

        page_source = driver.page_source
        sleep(5)

        return page_source

    def download_user(self, url):
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # options.add_argument('--headless')
        s = Service('chromedriver.exe')

        driver = webdriver.Chrome(service=s, options=options)
        driver.get(url)
        sleep(1)

        wait = WebDriverWait(driver, 5)  # 设置等待时长
        confirm_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR,"body > div.body-wrapper > div.content-wrapper > div.main-content > div.nav-tab > ul > li:nth-child(2)")
            )
        )
        confirm_btn.click()

        sleep(3)
        page_source = driver.page_source

        return page_source