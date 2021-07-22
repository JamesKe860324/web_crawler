from sys import path
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait  #WebDriverWait通常會配合EC一起使用
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json,os,pprint as pp,time  #pprint可以讓版面可讀性變高
from urllib import parse


options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--incognito')
options.add_argument('--disable-popup-blocking')  #不會有跳出視窗干擾
driver = webdriver.Chrome(options = options)

listData = []

url = "https://www.bookwormzz.com/zh/"

def visit():
    driver.get(url)
    
def getMainLinks():
    a_elms = driver.find_elements(By.CSS_SELECTOR,'a[data-ajax="false"]')
    for a in a_elms:
        listData.append({ 
            "title":a.get_attribute("innerText"),
            "link":parse.unquote(a.get_attribute('href'))+"#book_toc"#parse.unquote可以將href裡的百分比轉換成文字，ascii不支援特殊字符、中文，有些裝置只認得ascii碼
        })

def getSubLinks():
    for i in range(len(listData)):
        if "sub" not in listData:
            listData[i]["sub"] = []
        
        driver.get(listData[i]["link"]) # 讓browser走訪list裡dict中的link屬性值

        try:
            WebDriverWait(driver,3).until(       # 讓browser等待3秒若是3秒內指定等待的內容未出現，則進一步執行code，也可寫exception來接拋出的異常
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,'a[rel="external"][class="ui-link"]')
                )
            )
            
            a_elms = driver.find_elements(By.CSS_SELECTOR,'a[rel="external"][class="ui-link"]')
            for a in a_elms:
                listData[i]["sub"].append({
                    "sub_title":a.get_attribute("innerText"),
                    "sub_link":parse.unquote(a.get_attribute("href"))
                })

        except TimeoutException as e:     # except接出現的異常
            continue

def close():
    driver.quit

def saveJson():
    fp = open("jinyong.json","w",encoding="utf-8")
    fp.write(json.dumps(listData,ensure_ascii=False))
    fp.close()

def writeAndSaveAsText():
    listContent = []
    
    fp = open("jinyong.json","r",encoding="utf-8")
    strJson = fp.read()
    fp.close()

    folderPath="jinyong_txt"      # 在建立檔案或是資料夾前通常都會先判斷存不存在，利用os.path.exists()判斷該條件是否在此路徑下，要注意的是                                       
    if not os.path.exists(folderPath):    #他只能判斷該名稱在不在當前路徑
        os.makedirs(folderPath)

    listResult = json.loads(strJson)
    for i in range(len(listResult)):
        for j in range(len(listResult[i]["sub"])):
            driver.get(listResult[i]["sub"][j]["sub_link"])
            div = driver.find_element(By.CSS_SELECTOR,"div#html > div")
            Content = div.get_attribute("innerText")
            Content = Content.replace(" ","")
            Content = Content.replace("\n","")
            Content = Content.replace("\r","")
        
            fileName = f'{listResult[i]["title"]}_{listResult[i]["sub"][j]["sub_title"]}.txt' #在寫入的時候就會直接以txt檔寫入
            fp = open(f"{folderPath}/{fileName}","w",encoding="utf-8")  #打開folderPath裡面的fileName相當於在剛剛建的folderPath資料夾中建一個fileName的txt檔
            fp.write(Content)
            fp.close()

if __name__ == "__main__":
    time1 = time.time()  #程式到這行所執行的時間
    visit()
    # getMainLinks()
    # getSubLinks()
    # saveJson()
    # writeAndSaveAsText()
    # close()
    # print(f"it takes {time.time()-time1}")