from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class SearchService(Service):
    def __init__(self):
        # 檢查是否在 Docker 中運行
        if self.is_docker():
            # 在 Docker 運行，使用 ChromeDriverManager 安裝 ChromeDriver
            self.service = Service(executable_path=ChromeDriverManager().install())
        else:
            # 在本地運行，使用本地的 ChromeDriver
            self.service = Service(executable_path='bin\chromedriver.exe')

    def is_docker(self):
        try:
            with open('/proc/1/cgroup', 'rt') as f:
                return 'docker' in f.read()
        except IOError:
            return False
        
    def get_chrome_options(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--disable-gpu") 
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        return chrome_options

    def google_search(self, query):
        chrome_options = self.get_chrome_options()

        # 啟動 ChromeDriver
        with webdriver.Chrome(options=chrome_options, service=self.service) as driver:
            url = f"https://www.google.com/search?q={query}"
            driver.get(url)
            
            # 等待頁面元素加載（這裡以搜尋結果的第一個元素為例）
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.g'))
                )
            except Exception as e:
                print(f"Error waiting for page to load: {e}")
                return "Error loading page"

            # 獲取頁面源碼
            html = driver.page_source

        # 使用 BeautifulSoup 解析頁面
        soup = BeautifulSoup(html, 'html.parser')
        search_results = soup.select('.g')  # 查找每個搜尋結果

        # 提取前 5 條結果的標題和摘要
        search = "\n\n".join([
            f"搜尋結果 {idx+1}：\n"
            f"{result.select_one('h3').text if result.select_one('h3') else '無標題'}\n"
            f"{result.select_one('.VwiC3b').text if result.select_one('.VwiC3b') else '無摘要'}"
            for idx, result in enumerate(search_results[:5])  # 限制只顯示前 5 條
        ])

        return search