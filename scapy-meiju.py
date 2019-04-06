#!/usr/bin/python  

# -*- coding: utf-8 -*-
import scrapy
from scrapy import signals 

class LatestSpider(scrapy.Spider):
    name = "latest" 
    start_urls = [
        "http://www.ttmeiju.me/meiju/Billions.html",
        "http://www.ttmeiju.me/latest-1.html",
        "http://www.ttmeiju.me/latest-2.html",
        "http://www.ttmeiju.me/latest-3.html"
    ]

    #blacklist of the tv shows
    blacklist =[]
    #html table rows
    #an item in rows is like (page number, row number, html object of the row)
    rows = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(LatestSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(spider.spider_opend, signal=signals.spider_opened)
        return spider

    def spider_opend(self, spider):
        #self.initBlacklist()
        pass

    def spider_closed(self, spider, reason):
        html = open("latest.html","w")

        html.writelines("<html lang=\"en\">")
        html.writelines("<head>")
        html.writelines("<title>LHY_iS_Learning</title>")
        
        html.writelines("</head>")
        html.writelines("<table>")
        for page_no,row_no, tr in self.rows:
            html.writelines(tr)    
        html.writelines("</table>")    
        pass

    def parse(self, response):
        url = response.url
        page_no = url.replace("http://www.ttmeiju.me/latest-","").replace(".html","")
        page_no = int(page_no)
        #date
        dateString = response.css(".active::text")[1].extract().encode("gbk")
        header_tr = "<tr><th colspan=6>"+str(dateString)+"</th></tr>"
        self.rows.append((page_no,-1,header_tr))
        rows = response.css(".latesttable tr")
        for row_no in range(1,len(rows)):
            title_u = rows[row_no].css("td")[1].css("a::attr(title)").extract_first()
            title = title_u.encode("gbk")

            if self.inBlacklist(title):
                continue


            tr = rows[row_no].extract()
            tr = tr.replace("/Application/Home/View/Public/static/images/","")
            tr = tr.replace("href=\"/", "href=\"http://www.ttmeiju.me/")
            #added 2017-7-31
            tr = tr.replace("<span class=\"loadspan\"><img width=\"20px;\" src=\"loading.gif\"></span>","")
            tr = tr.replace("style=\"display:none;\"","")
            #end added 2017-7-31

            #if you want to filter out tv shows without subtitles,
            #uncomment this.
            #u'\u65e0\u5b57\u5e55' = "wu zi mu" = no subtitles
            if u'\u65e0\u5b57\u5e55' in tr:
                continue

            #if you want to filter out tv shows with subtitles,
            #uncomment this.
            #u'\u5185\u5d4c\u53cc\u8bed\u5b57\u5e55' = "nei qian shuang yu zimu"
#            if u'\u5185\u5d4c\u53cc\u8bed\u5b57\u5e55'.encode("gbk") in tr:
#                continue

            #if you want to filter out tv shows with solution lower than 720p,
            #uncomment this
            #u'\u666e\u6e05' = u"pu qing"
            if u'\u666e\u6e05' in tr:
                continue

            self.rows.append((page_no,row_no,tr))


    def initBlacklist(self):
        fh = open('blacklist.txt')
        self.blacklist = fh.readlines() 
        fh.close()
        for i in range(0,len(self.blacklist)):
            self.blacklist[i] = self.blacklist[i].replace("\n","")

    def inBlacklist(self,title):
        for b in self.blacklist:
            if b in title:
                return True
        return False

    def compareRow(self,a,b):
        a_p, a_r, a_row = a
        b_p, b_r, b_row = b
        return a_p * 1000 + a_r - b_p *1000 + b_r