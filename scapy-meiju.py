#!/usr/bin/python  

# -*- coding: utf-8 -*-
import scrapy
from scrapy import signals 

class LatestSpider(scrapy.Spider):
    name = "latest" 
    start_urls = []
    with_subtitle = {}
    

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
        self.initUrl()

    def spider_closed(self, spider, reason):
        html = open("lhy.html","w")

        html.writelines("<html lang=\"en\">")
        html.writelines("<head>")
        html.writelines("<title>LHY_iS_Learning</title>")
        
        html.writelines("</head>")
        html.writelines("<table>")
        for row_no, tr in self.rows:
            html.writelines(tr)    
        html.writelines("</table>")    
        pass

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

            # 普清
            if quality == u'\u666e\u6e05':
                continue

            # 熟肉
            if self.with_subtitle[url]:
                if quality != u'\u719f\u8089':
                    continue
            else:
                if quality == u'\u719f\u8089':
                    continue

            tr = rows[row_no].extract()
            tr = tr.replace(cols[0].extract(), "")
            tr = tr.replace(cols[3].extract(), "")
            tr = tr.replace("/Application/Home/View/Public/static/images/","")
            tr = tr.replace("href=\"/", "href=\"http://www.ttmeiju.me/")
            tr = tr.replace("<span class=\"loadspan\"><img width=\"20px;\" src=\"loading.gif\"></span>","")
            tr = tr.replace("style=\"display:none;\"","")


            self.rows.append((row_no,tr))


    def initUrl(self):
        with open('lhy.txt', 'r') as infile:
            for line in infile.readlines():
                url, subtitle = line.split()
                self.start_urls.append(url)
                self.with_subtitle[url] = bool(int(subtitle))
                

