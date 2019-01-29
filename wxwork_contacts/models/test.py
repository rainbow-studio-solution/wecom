import os
import requests
import time
from lxml import etree
from threading import Thread

keyWord = input(f"{'Please input the keywords that you want to download :'}")
class Spider():
    #初始化参数
    def __init__(self):
        self.headers = {#headers是请求头，"User-Agent"、"Accept"等字段可通过谷歌Chrome浏览器查找！
        "User-Agent": "Mozilla/5.0(WindowsNT6.1;rv:2.0.1)Gecko/20100101Firefox/4.0.1",
        }
        self.proxies = {#代理ip，当网站限制ip访问时，需要切换访问ip
		"http": "http://61.178.238.122:63000",
	    }
        #filePath是自定义的，本次程序运行后创建的文件夹路径，存放各种需要下载的对象。
        self.filePath = ('/users/zhaoluyang/小Python程序集合/桌面壁纸/'+ keyWord + '/')

    def creat_File(self):
        #新建本地的文件夹路径，用于存储网页、图片等数据！
        filePath = self.filePath
        if not os.path.exists(filePath):
            os.makedirs(filePath)

    def get_pageNum(self):
        #用来获取搜索关键词得到的结果总页面数,用totalPagenum记录。由于数字是夹在形如：1,985 Wallpapers found for “dog”的string中，
        #所以需要用个小函数，提取字符串中的数字保存到列表numlist中，再逐个拼接成完整数字。。。
        total = ""
        url = ("https://alpha.wallhaven.cc/search?q={}&categories=111&purity=100&sorting=relevance&order=desc").format(keyWord)
        html = requests.get(url,headers = self.headers,proxies = self.proxies)
        selector = etree.HTML(html.text)
        pageInfo = selector.xpath('//header[@class="listing-header"]/h1[1]/text()')
        string = str(pageInfo[0])
        numlist = list(filter(str.isdigit,string))
        for item in numlist:
            total += item
        totalPagenum = int(total)
        return totalPagenum

    def main_fuction(self):
        #count是总图片数，times是总页面数
        self.creat_File()
        count = self.get_pageNum()
        print("We have found:{} images!".format(count))
        times = int(count/24 + 1)
        j = 1
        start = time.time()
        for i in range(times):
            pic_Urls = self.getLinks(i+1)
            start2 = time.time()
            threads = []
            for item in pic_Urls:
                t = Thread(target = self.download, args = [item,j])
                t.start()
                threads.append(t)
                j += 1
            for t in threads:
                t.join()
            end2 = time.time()
            print('This page cost：',end2 - start2,'s')
        end = time.time()
        print('Total cost:',end - start,'s')

    def getLinks(self,number):
        #此函数可以获取给定numvber的页面中所有图片的链接，用List形式返回
        url = ("https://alpha.wallhaven.cc/search?q={}&categories=111&purity=100&sorting=relevance&order=desc&page={}").format(keyWord,number)
        try:
            html = requests.get(url,headers = self.headers,proxies = self.proxies)
            selector = etree.HTML(html.text)
            pic_Linklist = selector.xpath('//a[@class="jsAnchor thumb-tags-toggle tagged"]/@href')
        except Exception as e:
            print(repr(e))
        return pic_Linklist

    def download(self,url,count):
        #此函数用于图片下载。其中参数url是形如：https://alpha.wallhaven.cc/wallpaper/616442/thumbTags的网址
        #616442是图片编号，我们需要用strip()得到此编号，然后构造html，html是图片的最终直接下载网址。
        string = url.strip('/thumbTags').strip('https://alpha.wallhaven.cc/wallpaper/')
        html = 'http://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-' + string + '.jpg'
        pic_path = (self.filePath + keyWord + str(count) + '.jpg' )
        try:
            start = time.time()
            pic = requests.get(html,headers = self.headers)
            f = open(pic_path,'wb')
            f.write(pic.content)
            f.close()
            end = time.time()
            print(f"Image:{count} has been downloaded,cost:",end - start,'s')

        except Exception as e:
            print(repr(e))

spider = Spider()
spider.main_fuction()