# 擷取104銀行關鍵字前10頁的職稱、職稱連結、公司名字、公司連結、薪資、位置、
# 工作經歷要求、學歷要求，寫進DB裡
from base64 import encode
from pymysql import connections
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json,os,time,pymysql
from pprint import pprint 
from time import sleep

options = webdriver.ChromeOptions()
options.add_argument('--incognito')
options.add_argument('--start-maximized')
options.add_argument('--disable-popup-bolcking')
browser = webdriver.Chrome(options = options)
# options.binary_location = 'r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"'
# 可手動指定chorome.exe位置?，抑或是webdriver.Chrome中的參數可設定路徑
url = 'https://www.104.com.tw/jobs/main/'

keyword = "python"

connection = pymysql.connect(
    host ='localhost',
    user = '',
    password = '',
    database = '104_informations',
    charset = 'utf8mb4',
    cursorclass = pymysql.cursors.DictCursor
)

cursor = connection.cursor()

listData = []

def visit():
    browser.get(url)
  
def search():
    searchInput = browser.find_element(By.CSS_SELECTOR,"input[type='text']")
    searchInput.send_keys(keyword)
    searchButton = browser.find_element(By.CSS_SELECTOR,'button.btn.js-formCheck').click()
    sleep(1)

def filterFuc():
    try:
        WebDriverWait(browser,3).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,"input#area-cat")
            )
        )
        browser.find_element(By.CSS_SELECTOR,"input#area-cat").click()
        sleep(1)
        browser.find_element(By.CSS_SELECTOR,'input#e104menu2011_m_cb_0_0').click()
        sleep(1)
        browser.find_element(By.CSS_SELECTOR,'input#e104menu2011_m_cb_0_1').click()
        sleep(1)
        browser.find_element(By.CSS_SELECTOR,'input.e104menu2011_but').click()
        browser.find_element(By.CSS_SELECTOR,"button[type='submit']").click()
        sleep(0.5)
        browser.find_elements(By.CSS_SELECTOR,'span.js-txt')[1].click()

    except TimeoutException as e:
        print('等不到篩選器，3秒後關閉瀏覽器')
        sleep(3)
        browser.close()
    
def getMainLinks():
    for i in range(1,16):
        selectPage = Select(browser.find_element(By.CSS_SELECTOR,'select.page-select.gtm-paging-top'))
        selectPage.select_by_value(f"{i}")
        sleep(1)
        # WebDriverWait(browser,3).until(
        #     EC.presence_of_element_located(
        #         (By.CSS_SELECTOR,"a.js-job-link")
        #     )
        # ) 
        jobDetails = browser.find_elements(By.CSS_SELECTOR,"a.js-job-link")
        for elems in jobDetails:
            jobName = elems.get_attribute('innerText')
            jobLink = elems.get_attribute('href')    
            listData.append({
                'jobName' : jobName,
                'jobLink' : jobLink
            })

def getSubLinks():
    for i in range(len(listData)):
        if 'companyName''companyLink''salary''location''jobRequirements''acadamicRequirements' not in listData:
            browser.get(listData[i]['jobLink'])
            companyDetails = browser.find_elements(By.CSS_SELECTOR,'a[target="_blank"][rel="noopener"]')[0]
            companyName = companyDetails.get_attribute('innerText')
            companyLink = companyDetails.get_attribute('href')
            WebDriverWait(browser,3).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,'p.t3.mb-0.mr-2')
                )
            ) 
            salary = (browser.find_element(By.CSS_SELECTOR,'p.t3.mb-0.mr-2')).get_attribute('innerText')
            location = (browser.find_elements(By.CSS_SELECTOR,'div.col.p-0.job-description-table__data > p')[1]).get_attribute('innerText')
            jobRequirements = (browser.find_elements(By.CSS_SELECTOR,'p.t3.mb-0[data-v-a1bba18e][data-v-865e422e]')[0]).get_attribute('innerText')
            acadamicRequirements = (browser.find_elements(By.CSS_SELECTOR,'p.t3.mb-0[data-v-a1bba18e][data-v-865e422e]')[1]).get_attribute('innerText')
            listData[i]['companyName'] = companyName
            listData[i]['companyLink'] = companyLink
            listData[i]['salary'] = salary
            listData[i]['location'] = location
            listData[i]['jobRequirements'] = jobRequirements
            listData[i]['acadamicRequirements'] = acadamicRequirements
            # listData[i].append() 上面的方法改這個不行，因為append只有list能用，listData[i]是dict
            # listData[i]['salary']這種方法為直接在listData[i]中給予屬性和屬性值

def close():
    browser.close()

def saveJson():
    # fp = open("104job.json","w",encoding="utf-8")
    # fp.write(json.dumps(listData,ensure_ascii=False))
    # fp.close()
    with open('104job.json','w',encoding='utf-8') as fp:
        fp.write(json.dumps(listData,ensure_ascii=False))

def savaDB():
    try:
        # fp = open("104job.json","r",encoding='utf-8')
        # strJson = fp.read()
        # fp.close()
        with open('104job.json','r',encoding='utf-8') as fp:
            strJson = fp.read()
        listResult = json.loads(strJson)
        sql = 'insert into python_jobs(jobName,jobLink,companyName,companyLink,salary,location,jobRequirements,acadamicRequirements) values (%s,%s,%s,%s,%s,%s,%s,%s)'
        for obj in listResult:
            cursor.execute(
                sql,
                (obj['jobName'],obj['jobLink'],obj['companyName'],obj['companyLink'],obj['salary'],obj['location'],obj['jobRequirements'],obj['acadamicRequirements'])
            )
        connection.commit()
    except Exception as e:
        connection.rollback()
        print(f'SQL執行失敗:{e}')
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    time1 = time.time()
    visit()
    search()
    filterFuc()
    getMainLinks()
    getSubLinks()
    saveJson()
    savaDB()
    close()
    print(f"總花費時間: {time.time()-time1}")
  
