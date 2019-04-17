#!/usr/bin/python  

# -*- coding: utf-8 -*-
from twisted.internet import reactor
import scrapy
from scrapy import signals 
from scrapy.http import FormRequest, Request
from scrapy.crawler import CrawlerRunner
from multiprocessing import Process, Queue
from os import walk

class glb:
    fileName = "lhy"
    outputFolderName = "results"
    #absolutePath = "/var/www/html/"
    absolutePath = ""

class MySpider(scrapy.Spider):
    name = 'MySpider'
    
    start_urls = []
    with_subtitle = {}
    

    #html table rows
    #an item in rows is like (page number, row number, html object of the row)
    rows = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(MySpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(spider.spider_opend, signal=signals.spider_opened)
        return spider

    def start_requests(self):
        return [Request("http://www.ttmeiju.me/", callback = self.get_login)]


    def spider_opend(self, spider):
        self.initUrl()

    def spider_closed(self, spider, reason):
        html = open(glb.absolutePath + glb.outputFolderName + "/" + glb.fileName + ".html","w")

        html.writelines("<meta charset=\"utf-8\"> ")
        html.writelines("<html lang=\"en\">")
        html.writelines("<head>")
        html.writelines("<title>LHY_iS_Learning</title>")
        
        html.writelines("</head>")
        html.writelines("<table>")
        for row_no, tr in self.rows:
            html.writelines(tr)    
        html.writelines("</table>")    
        pass

    def get_login(self, response):
        return FormRequest.from_response(response,
                                         formdata={'password': 'pw',
                                                   'username': 'user'},
                                         callback=self.after_login)
    
    def after_login(self, response):
        for url in self.start_urls:
            yield self.make_requests_from_url(url)


    def parse(self, response):
        url = response.url
        showName = url.replace("http://www.ttmeiju.me/meiju/","").replace(".html","")
        
        # Season
        season = response.css("h3[class=curseason]::text").extract_first().strip()
        header_tr = "<tr><th colspan=6>"+showName + " " + season+"</th></tr>"
        self.rows.append((-1,header_tr))

        rows = response.css("#seedlist tr")
        for row_no in range(len(rows)):

            # for each row  
            # filter out irrelevent 
            cols = rows[row_no].css("td")
            # 0 -> checkbox
            # 1 -> title
            # 2 -> dowlnoad
            # 3 -> watch online
            # 4 -> baidu-code
            # 5 -> size
            # 6 -> quality
            # 7 -> subtitle
            # 8 -> publish time
            title = cols[1].css('a[href]::text').extract_first().strip()
            quality = cols[6].css('td::text').extract_first().strip()

            # pu qing
            if quality == u'\u666e\u6e05':
                continue

            # shu rou
            if self.with_subtitle[url]:
                if quality != u'\u719f\u8089':
                    continue
            else:
                if quality == u'\u719f\u8089':
                    continue

            tr = rows[row_no].extract()
            tr = tr.replace(cols[0].extract(), "")
            tr = tr.replace(cols[3].extract(), "")

            if tr.find("http://www.zimuku.la/") != -1:
                subtitle_url = "http://www.subhd.com/search0/"+title
                tr = tr.replace("http://www.zimuku.la/", subtitle_url)
                num_subtitle = get_subtitle(subtitle_url)
                if num_subtitle == 0:
                    tr = tr.replace(u'搜字幕', "No Subtitle Yet")
                elif num_subtitle == -1:
                    pass
                else:
                    tr = tr.replace(u'搜字幕', str(num_subtitle) + " Subtitles")

            tr = tr.replace("href=\"/", "href=\"http://www.ttmeiju.me/")
            tr = tr.replace("/Application/Home/View/Public/static/images/","../logo/")
            tr = tr.replace("<span class=\"loadspan\"><img width=\"20px;\" src=\"../logo/loading.gif\"></span>","")
            tr = tr.replace("style=\"display:none;\"","")
            


            self.rows.append((row_no,tr))


    def initUrl(self):
        with open('users/' + glb.fileName +'.txt', 'r') as infile:
            for line in infile.readlines():
                url, subtitle = line.split()
                self.start_urls.append(url)
                self.with_subtitle[url] = bool(int(subtitle))

def get_subtitle(url):
    import requests
    from bs4 import BeautifulSoup
    import UserAgent
    ua = UserAgent.UserAgent()
    try:
        r = requests.get(url, headers={
            'User-Agent':
                ua.random(),
            'Accept-Language':    'zh-tw',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection':'keep-alive',
            'Accept-Encoding':'gzip, deflate'
        })
        soup = BeautifulSoup(r.text, 'html.parser')
        return int(soup.find("small").find('b').text)
    except:
        return -1


def run_spider(spider):
    def f(q):
        try:
            runner = CrawlerRunner()
            deferred = runner.crawl(spider)
            deferred.addBoth(lambda _: reactor.stop())
            reactor.run()
            q.put(None)
        except Exception as e:
            q.put(e)

    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result

def main():
    for _,_,fileName in walk('users'):
        for fn in fileName:
            if fn == "README.md":
                continue
            glb.fileName = fn.split('.')[0]
            print("------------------------>" + glb.fileName)
            run_spider(MySpider)

if __name__ == "__main__":
    #get_subtitle("http://www.subhd.com/search0/Billions")
    main()