from selenium import webdriver 
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException

from pathlib import Path

def get_browser():
    project_root_directory = Path(__file__).parent

    options = Options()
    options.add_experimental_option(
        "prefs", {
            "download.default_directory": str(project_root_directory / 'data'),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
    )
    options.add_argument(" - incognito")
    
    browser = webdriver.Chrome(
        executable_path=(project_root_directory / 'chromedriver').resolve(),
        chrome_options=options
    )

    return browser

def run_crawler(browser):
    timeout = 10
    page_url = "http://fortune.com/fortune500/list/"
    target_xpath = '''//*[@id="pageContent"]/div[3]/div/div/div[1]/div[1]/ul/li[1]/a/span[2]'''
    try:
        browser.get(page_url)
        WebDriverWait(
            browser, timeout
        ).until(
            EC.visibility_of_element_located((By.XPATH, target_xpath))
        )
    except TimeoutException:
        print("ERROR: Timeout waiting for GET webpage")
        return
    
    fortune_items = browser.find_elements_by_class_name('company-title')

    for item in fortune_items:
        print(item.text)
    

if __name__ == "__main__":
    browser = get_browser()
    try:
        run_crawler(browser)
        browser.quit()
    except Exception:
        browser.quit()
    