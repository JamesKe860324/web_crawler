import requests,json,os,time
from pprint import pprint
from bs4 import BeautifulSoup
from urllib import parse

from requests.models import Response

listData = []

url = 'https://www.bookwormzz.com/zh/'

my_headers = {
    'user-agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}
def getMainLinks():
    response = requests.get(url,headers = my_headers)
    soup = BeautifulSoup(response.text,'lxml')
    elems = soup.select('a[data-ajax="false"]')
    for a in elems:
        listData.append({
            'title' : a.get_text(), # 或是a.text
            'link' : url+parse.unquote(a['href'])+"#book_toc" # 或是a.get('href')
        })
        
def getSubLinks(): #我這裡直接從listData把資料寫進去，而不是存進json後叫出來
    for i in range(len(listData)):
        if 'sub' not in listData[i]:
            listData[i]['sub'] = []
        response = requests.get(listData[i]['link'],headers = my_headers)
        soup = BeautifulSoup(response.text,'lxml')
        elems = soup.select("div[data-role='content'] div[data-theme='b'] a[rel='external']")
        for a in elems:
            listData[i]['sub'].append({
                'subTitle' : parse.unquote(a.text),
                'subLink' : url + a['href']
            })
    # pprint(listData)
def writeText():
    folderPath = "jinyong_requests_txt_test"
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

    for i in range(len(listData)):
        for j in range(len(listData[i]['sub'])):
            response = requests.get(listData[i]['sub'][j]['subLink'],headers = my_headers)
            soup = BeautifulSoup(response.text,'lxml')
            elem = soup.select_one("div#html > div")
            strContent = elem.text
            strContent = strContent.replace("\n",'')
            strContent = strContent.replace("\r",'')
            strContent = strContent.replace(" ",'')
            strContent = strContent.replace("　",'')

            fileName = f"{listData[i]['title']}_{listData[i]['sub'][j]['subTitle']}.txt"
            
            fp = open(f"{folderPath}/{fileName}",'w',encoding='utf-8')
            fp.write(strContent)
            fp.close()

def saveJson():
    fp = open("jinyong_requests.json","w",encoding="utf-8")
    fp.write(json.dumps(listData,ensure_ascii=False))
    fp.close()

if __name__ == "__main__":
    time1 = time.time()
    getMainLinks()
    getSubLinks()
    writeText()
    saveJson()
    print(f"總花費時間: {time.time()-time1}")