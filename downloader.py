import urllib.error
from urllib.request import urlopen
import sys, re, os, time, queue, threading, json
urlCounter = 0
# Function definition is here
def addHistoryUrl(postUrl):
    if postUrl not in historyUrl:
        print("store %s to history" % postUrl)
        historyUrltoAdd.append(postUrl)
        urlPool.put(postUrl)
def download(link, postId, increament):
    img = urlopen(link+".jpg")
    localFile = open('%s/%s(%s).jpg' % (folderName, postId, increament), 'wb')
    localFile.write(img.read())
    localFile.close()
def createFolder(folderName):    
    if not os.path.isdir(folderName):
        print("%s created" % folderName)
        os.makedirs(folderName)
def startThreads():
    lock = threading.Lock()
    for i in range(5):
        t = threading.Thread(target=downloadThread, args=(i, lock))
        t.start()
        threads.append(t)
def getUrls(url):
    global urlCounter
    try:
        resPage = urlopen(url)
        jsonData = json.loads(resPage.read().decode().translate(non_bmp_map))
        lastUrl = jsonData[len(jsonData)-1]['id']
        for post in jsonData:
            urlCounter += 1
            if post['pinned'] is False:
                if re.search("圖", post['title']):
                    if post['gender'] is 'M':
                        if re.search("女", post['title']):
                                addHistoryUrl(str(post['id']))
                    else:
                        addHistoryUrl(str(post['id']))
    except urllib.error.URLError as e:
        print(e)
        print("Connection error, please check you internet")

    if urlCounter==30:
        print("goto next page")
        nextPage = "https://www.dcard.tw/_api/forums/sex/posts?popular=true&before="+str(lastUrl)
        getUrls(nextPage)
        startThreads()
    elif urlCounter==60:
        print("get url stop")
        for i in range(5):
            urlPool.put(None)
        for t in threads:
            t.join()
#download thread
def downloadThread(index, lock):
    while True:
        imgLink = []
        increament = 0
        postId = urlPool.get()
        urlPool.task_done()
        if postId is None:            
            print("close thread %s" % index)
            break
        lock.acquire()
        print("start to download image from %s" % postId)
        lock.release()
        post = urlopen("https://www.dcard.tw/_api/posts/"+postId)        
        postJson = json.loads(post.read().decode().translate(non_bmp_map))
        comment = urlopen("https://www.dcard.tw/_api/posts/"+postId+"/comments?popular=true")
        commentJsons = json.loads(comment.read().decode().translate(non_bmp_map))
        imgLink = (re.findall("(http:\/\/[i.]*imgur.com\/\w+)", postJson['content']))
        for commentJson in commentJsons:
            imgsInComment = re.findall("(http:\/\/[i.]*imgur.com\/\w+)", commentJson['content'])
            if imgsInComment:
                for imgInComment in imgsInComment:
                    imgLink.append(imgInComment)
        for link in imgLink:            
            increament+=1
            download(link, postId, increament)
#main thread
#if no historys.txt then create                
if not os.path.exists('historys.txt'):
    print("create historys.txt")
    open('historys.txt', 'w').close()
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
historyUrl = {}
historyUrltoAdd = []
urlPool = queue.Queue()
threads = []
file = open('historys.txt', 'r+')
historyUrl = file.read().splitlines()
file.close()
folderName = time.strftime("%Y%m%d")
createFolder(folderName)
hotUrl = "https://www.dcard.tw/_api/forums/sex/posts?popular=true"
getUrls(hotUrl)
file = open('historys.txt', 'a+')
for item in historyUrltoAdd:
  file.write("%s\n" % item)
urlPool.join()  
file.close()
print("===complete===")
