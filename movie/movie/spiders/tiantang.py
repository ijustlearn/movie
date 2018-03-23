import scrapy
import re

import singleton as singleton
from scrapy.mail import MailSender

from movie.items import ProMovieItem, ProMovieDownAddressItem
from movie.mysql.pipelines import MoviePipeline
from movie.settings import IS_INC
from movie.utils.commoneUtils import CommoneUtils
from scrapy import Request
from scrapy import  log
import datetime

class Dy2018MovieScrapy(scrapy.Spider):
    name = 'dy2018'
    baseUrl = "https://www.dy2018.com"
    allowed_domains  = ["dy2018.com"]
    is_inc = 'true'
    scrapy_date = datetime.datetime.now()  #从哪天抓取数据默认当天
    # start_urls = [
    #     # "https://www.dy2018.com/i/99150.html"
    #     "https://www.dy2018.com/html/gndy/dyzz/"
    # ]
    def __init__(self,is_inc='true' ,*args,**kwargs):
        super(Dy2018MovieScrapy, self).__init__(*args, **kwargs)
        self.is_inc = is_inc
        if is_inc == 'false':
            print("全量抓取电影")
        else:
            print("增量抓取电影")
    def closed(self,reason):
        #爬取完成后进行邮件通知
        mailer = MailSender.from_settings(self.settings)
        body = '''本次爬取状态:{}\r\n本次爬取电影数量:{}\r\n本次爬取电影列表:{}'''.format(reason,self.crawler.stats.get_value('movie_count'),
                                                                    self.crawler.stats.get_value('movie_list'))
        subject = '天堂网电影爬取通知'
        mailer.send(to=["477915244@qq.com"], subject=subject, body=body)
    def start_requests(self):
        self.crawler.stats.set_value('movie_list', [])
        self.crawler.stats.set_value('movie_count', 0)
        yield Request("https://www.dy2018.com/html/gndy/dyzz/", callback=self.parse0)
    def parse0(self, response):

        isNeedFollow = True
        movieList = response.css('.co_content8 > ul  table  ')
        for movieTable in movieList:
            infoStr =  movieTable.css('font[color="#8F8C89"]::text').extract_first() # 日期：2018-03-11 点击：77534
            tmpStrlist1 = infoStr.split(" ")
            tmpStrlist2 = tmpStrlist1[0].split("：")
            updateDate = datetime.datetime.strptime(tmpStrlist2[1],'%Y-%m-%d')

            #如果是当前日期或者是全量则进行解析
            if self.scrapy_date.date() <= updateDate.date() or  self.is_inc == 'false':
                movielink = movieTable.css('a::attr(href)').extract_first()
                currentUrl = self.baseUrl+movielink
                yield Request(currentUrl,callback=self.parse1)
            else:
                isNeedFollow = False #遇到与今天日期不符的日期是则证明有以前的更新数据，将跟进设置为false
        #如果是全量或者增量需要爬取下一页则进入下一页进行爬取
        if isNeedFollow or self.is_inc == 'false':
            otherlinkList = response.css('.co_content8 > div a')
            for otherlink in otherlinkList:
                isNextPage = otherlink.css('::text').extract_first()=='下一页'
                if isNextPage:
                    yield Request(self.baseUrl+otherlink.css('::attr(href)').extract_first(), callback=self.parse0)

    def parse1(self, response):
        infos = response.css("#Zoom>p") #电影描述列表
        downAdrressesUrl = response.css("#Zoom>table") #电影下载地址元素列表
        if len(infos) == 0 or len(infos) == downAdrressesUrl : #如果获取不到相应的元素则直接退出
            return
        movieItem = ProMovieItem()
        movieId =  CommoneUtils.getTableId()
        movieItem['id'] = movieId
        movieItem['source'] = self.name
        movieItem['sourcePageUrl'] = response.url
        #存入发布日期
        try:
            updateTimeStr  = response.css('div.co_content8 span.updatetime::text').extract_first() #发布时间：2018-03-11
            tmpList = updateTimeStr.split("：")
            updateDate = datetime.datetime.strptime(tmpList[1], '%Y-%m-%d')
            movieItem['updateDate']=updateDate.timestamp()
        except Exception as e :
            movieItem['updateDate'] = datetime.datetime.now().timestamp()
            log.msg("电影地址:{}发布日期解析不到默认使用当前日期".format(response.url))

        pList =  infos.xpath('text()').extract()
        movieDescr = ""
        beginDescr = False
        movieItem['movieImgUrl'] = infos[0].xpath("//img/@src").extract_first()
        for p in pList:
            nameMatch = re.match('◎译　　名(.*)', p)
            realNameMatch = re.match('◎片　　名(.*)', p)
            movieYearMatch = re.match('◎年　　份(.*)', p) if re.match('◎年　　份(.*)', p) else re.match('◎年　　代(.*)', p)
            if nameMatch:
                movieItem['movieName'] = nameMatch.group(1).strip()
            if realNameMatch:
                movieItem['movieRealName'] = realNameMatch.group(1).strip()
            if movieYearMatch:
                movieItem['movieYear'] = movieYearMatch.group(1).strip()
            if re.match('◎影片截图', p):
                beginDescr = False
            if beginDescr  == True:
                movieDescr = movieDescr + p
            if re.match('◎简　　介', p):
                beginDescr = True
        #如果解析后没有获取到电影名称则退出
        if not movieItem.get('movieName', None) or not movieItem.get('movieRealName', None):
            log.msg("电影地址:{}发布日期解析不到电影名称".format(response.url))
            return
        if len(movieDescr)>1000 : #如果描述太长则直接截断
            movieDescr = movieDescr[0:999]
        movieItem['movieDescr']=movieDescr

        moviePipelin = MoviePipeline()
        #如果已经有当前页面的电影链接存储过则直接退出
        if moviePipelin.movieLinkIsRepeat(movieItem['sourcePageUrl'],movieItem['source']):
            return
        self.crawler.stats.inc_value('movie_count')
        self.crawler.stats.get_value('movie_list').append(movieItem['movieRealName'])
        yield movieItem
        for downAdrressUrlInfo in downAdrressesUrl:
            downAdrressItem = ProMovieDownAddressItem()
            url = downAdrressUrlInfo.css('a::attr(href)').extract_first()
            downAdrressItem['downType'] = "迅雷"
            downAdrressId = CommoneUtils.getTableId()
            downAdrressItem['id'] = downAdrressId
            downAdrressItem['movieId'] = movieId
            downAdrressItem['downAddress'] = url
            yield downAdrressItem


