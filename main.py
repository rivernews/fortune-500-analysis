from selenium import webdriver 
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException
)

import time

from pathlib import Path
import json

PROJECT_ROOT_DIRECTORY = Path(__file__).parent

def get_browser():
    global PROJECT_ROOT_DIRECTORY

    options = Options()
    options.add_experimental_option(
        "prefs", {
            "download.default_directory": str(PROJECT_ROOT_DIRECTORY / 'data'),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
    )
    options.add_argument("--incognito")
    
    browser = webdriver.Chrome(
        executable_path=(PROJECT_ROOT_DIRECTORY / 'chromedriver').resolve(),
        chrome_options=options
    )

    return browser

def get_company_title_doms(browser):
    return browser.find_elements_by_class_name('company-title')

def get_company_title_cache_file_directory():
    global PROJECT_ROOT_DIRECTORY
    return PROJECT_ROOT_DIRECTORY / 'data' / 'company-titles.json'

def save_data(data, file_name=None):
    if file_name == None:
        data_directory = get_company_title_cache_file_directory()
    else:
        global PROJECT_ROOT_DIRECTORY
        data_directory = PROJECT_ROOT_DIRECTORY / 'data' / file_name
    
    if file_name == None:
        print("INFO: Saving data...")
    else:
        print(f"INFO: Saving data into {file_name}...")

    with data_directory.open(mode='w') as f:
        json.dump(data, f, sort_keys=True, indent=4)

def load_data():
    data_directory = get_company_title_cache_file_directory()
    with data_directory.open(mode='r') as f:
        return json.load(f)

def access_webpage(browser, page_url, target_xpath='', timeout=10):
    try:
        browser.get(page_url)
        WebDriverWait(
            browser, timeout
        ).until(
            EC.visibility_of_element_located((By.XPATH, target_xpath))
        )
        return True
    except TimeoutException:
        print("ERROR: Timeout waiting for GET webpage")
        return False

def run_crawler(browser, get_rank_amount=None):
    access_webpage(
        browser,
        page_url="http://fortune.com/fortune500/list/",
        target_xpath='''//*[@id="pageContent"]/div[3]/div/div/div[1]/div[1]/ul/li[1]/a/span[2]'''
    )
    
    fortune_items = [None]
    eager_fetch_fortune_items = []

    wait_load_time_interval = 6
    while True:
        print("INFO: Fetching company titles...")
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(wait_load_time_interval)
        eager_fetch_fortune_items = get_company_title_doms(browser)

        if len(eager_fetch_fortune_items) <= len(fortune_items) or (get_rank_amount!=None and len(fortune_items) >= get_rank_amount):
            print(f"INFO: No new title found within {wait_load_time_interval} seconds of interval and limit amount of {get_rank_amount}. Will now finish.")
            break
        else:
            fortune_items = eager_fetch_fortune_items
            print(f"INFO: Got new company titles, total {len(fortune_items)} titles.")
            print("INFO: Preapre for serializing data for saving data...")
            fortune_items = [ {
                'fortune500Rank': index + 1,
                'companyTitle': item.text
            } for index, item in enumerate(fortune_items)]

            save_data({
                "items": fortune_items
            })
    
    print("INFO: Finish fetching company list.")

def fetch_fortune_company_list(get_rank_amount=None):
    browser = get_browser()
    run_crawler(browser, get_rank_amount)
    browser.quit()

class GlassdoorCrawler:

    query_url = '''https://www.glassdoor.com/Reviews/company-reviews.htm?suggestCount=10&suggestChosen=false&clickSource=searchBtn&typedKeyword=%s&sc.keyword=%s&locT=C&locId=&jobType='''

    def __init__(self, *args, **kwargs):
        self.browser = get_browser()

        self.data = load_data()

        self.sample_data_list = self.data.get("items", [])[:]
        self.fetch_exceptions = []
        for index, sample_data in enumerate(self.sample_data_list):
            company_title = sample_data.get("companyTitle", None)
            if company_title == None:
                print("ERROR: sample_data is None")
                return
            
            page_url = f"{self.query_url.replace('%s', company_title)}"

            try:
                result = access_webpage(
                    self.browser,
                    timeout=1,
                    page_url=page_url,
                    target_xpath='''//*[@id="MainCol"]/div[1]/div[2]/div[2]/span/div/span[1]/span[1]'''
                )

                # handle when only single result
                if not result:
                    try:
                        rating_dom = self.browser.find_element_by_class_name('ratingNum')
                        print("INFO: Detected single query result page")
                        rating_doms = [rating_dom]
                    except NoSuchElementException as error_message:
                        self.fetch_exceptions.append({
                            'companyTitle': company_title,
                            'exceptionType': "NoSuchElementException",
                            'exceptionMessage': f'{error_message}',
                            'accessURL': page_url,
                            'index': index
                        })
                        self.save_rating_data()

                else:
                    rating_doms = self.browser.find_elements_by_class_name('bigRating')

                # find first non-empty rating
                for dom in rating_doms:
                    if dom.text != '':
                        print(f"INFO: ({index + 1}/{len(self.sample_data_list)}) Got glassdoor rating {dom.text} for {company_title}")
                        try:
                            self.sample_data_list[index]['glassdoorRating'] = float(dom.text)
                        except ValueError:
                            print(f"ERROR: Can't store rating value, dom.text is `{dom.text}`")
                        break
                
                # save intermediate results
                if index % 5 == 2:
                    self.save_rating_data()
            except Exception as error_message:
                self.fetch_exceptions.append({
                    'companyTitle': company_title,
                    'exceptionType': "Exception",
                    'exceptionMessage': f'{error_message}',
                    'accessURL': page_url,
                    'index': index
                })
                self.save_rating_data()

        self.save_rating_data()

        self.browser.quit()
        return
    
    def save_rating_data(self):
        save_data({
            'items': self.sample_data_list,
            'exceptions': self.fetch_exceptions
        }, 'sample-company-ratings.json')

if __name__ == "__main__":
    fetch_fortune_company_list()
    gd = GlassdoorCrawler()
    