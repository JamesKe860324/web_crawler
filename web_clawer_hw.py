import json,time,os,requests
from bs4 import BeautifulSoup
from pprint import pprint
from urllib import parse
import re
import socket
import random
url = 'https://www.gutenberg.org/browse/languages/zh'

listData = []

my_headers = {
    'user-agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}

def getLinks():
    response = requests.get(url,headers = my_headers) # 經由回傳的response物件可以取得許多網頁的資訊
    soup = BeautifulSoup(response.text,'lxml') # 將網頁內容交給beautifulsoup做分析
    elms = soup.select('div.container li.pgdbetext a')
    for elm in elms:
        listData.append({
            'title' : elm.text,
            'link' : "https://www.gutenberg.org/" + elm['href'] 
        })

def visitLink():
    for elm in range(len(listData)):
        urlNum = (listData[elm]['link']).split('ebooks/')[1]
        linkurl = f"https://www.gutenberg.org/files/{urlNum}/{urlNum}-0.txt"
        if 'sub_link' not in listData[elm]:  # 確認沒有的話其實這行不用寫
            listData[elm]['sub_link'] = linkurl
     
def saveJson():
    fp = open('gutenberg.json','w',encoding='utf-8')
    fp.write(json.dumps(listData,ensure_ascii=False))
    fp.close()

def writeToTxt():
    folderPath = "gutenberg_test"
    if not os.path.exists(folderPath):
        os.mkdir(folderPath)
    
    fp = open('gutenberg.json','r',encoding='utf-8')
    strJson = fp.read()
    fp.close()

    listResult = json.loads(strJson) # 不把它從json轉回物件也行，直接用listData就好
    for i in range(len(listResult)):
        try:
            time.sleep(random.randint(1,2))
            response = requests.get(listResult[i]['sub_link'])
        except socket.error as e:
            print(e)     
            
        response.encoding = 'utf-8' # response.encoding得到的結果是ISO-8859-1，不改的話回傳中文會是亂碼，無法用regex
        soup = BeautifulSoup(response.text,'lxml')
        elm = soup.select_one('body')
        startStrContent = elm.text
        regex = r'[\u4E00-\u9FFF，。：「」；、？！『』《》]+'
        finalStrContent = re.findall(regex,startStrContent)
        fileName = f"{listResult[i]['title']}.txt"
        fileName = fileName.replace("\r"," ")
        fileName = fileName.replace("/"," ")
        fp = open(f'{folderPath}\{fileName}','w',encoding = 'utf-8')
        fp.write("".join(finalStrContent)) # 將內容裡的[]去掉
        fp.close()



if __name__ == "__main__":
    time1 = time.time()
    getLinks()
    visitLink()
    saveJson()
    writeToTxt()
    print(f"總花費時間 : {time.time()-time1}")
    