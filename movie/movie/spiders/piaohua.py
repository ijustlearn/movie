import datetime
import re

from scrapy.crawler import Crawler
from scrapy import  log
import scrapy
from scrapy import Request

from movie.items import ProMovieItem, ProMovieDownAddressItem
from movie.mysql.pipelines import MoviePipeline
from movie.utils.commoneUtils import CommoneUtils
from scrapy.mail import MailSender
class piaohuaMovieScrapy(scrapy.Spider):
    name = 'piaohua'
    baseUrl = "https://www.piaohua.com"
    allowed_domains  = ["piaohua.com"]
    is_inc = 'true'
    scrapy_date = datetime.datetime.now()  # 从哪天抓取数据默认当天
    # scrapy_date = datetime.datetime.strptime('2018-03-10', '%Y-%m-%d')
    def __init__(self,is_inc='true' ,*args,**kwargs):
        super(piaohuaMovieScrapy, self).__init__(*args, **kwargs)
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
        subject = '雪花网电影爬取通知'
        mailer.send(to=["477915244@qq.com"], subject=subject, body=body)

    def start_requests(self):
        self.crawler.stats.set_value('movie_list', [])
        self.crawler.stats.set_value('movie_count', 0)
        yield Request("https://www.piaohua.com/html/zuixindianying.html", callback=self.parse0)
        if self.is_inc == 'false':
            yield Request("https://www.piaohua.com/html/dongzuo/index.html", callback=self.parse2)
            yield Request("https://www.piaohua.com/html/xiju/index.html", callback=self.parse2)
            yield Request("https://www.piaohua.com/html/aiqing/index.html", callback=self.parse2)
            yield Request("https://www.piaohua.com/html/kehuan/index.html", callback=self.parse2)
            yield Request("https://www.piaohua.com/html/juqing/index.html", callback=self.parse2)
            yield Request("https://www.piaohua.com/html/xuannian/index.html", callback=self.parse2)
            yield Request("https://www.piaohua.com/html/zhanzheng/index.html", callback=self.parse2)
            yield Request("https://www.piaohua.com/html/zainan/index.html", callback=self.parse2)
            yield Request("https://www.piaohua.com/html/dongman/index.html", callback=self.parse2)

    def parse2(self,response):
        currentUrl = re.match('.*/',response.url).group(0)
        movieLinkList = response.css('#list > dl > dt > a::attr(href)').extract()
        for movieUrl in movieLinkList:
            yield Request(self.baseUrl+movieUrl,callback=self.parse1)
        pageUrlList = response.css('div#nml > div.page > a::attr(href)').extract()
        for pageUrl in pageUrlList:
            # if pageUrl not in scrapyedUrls: 使用系统url去重
            yield Request(currentUrl+pageUrl,callback=self.parse2)
    def parse0(self,response):
        movieList = response.css("#im li")
        for movie in movieList:
            updateDateStr = movie.css('span::text').extract_first()
            if updateDateStr == None : updateDateStr = movie.css('font::text').extract_first()
            if updateDateStr == None : continue
            print(updateDateStr)
            updateDate = datetime.datetime.strptime(updateDateStr, '%Y-%m-%d')
            #如果更新时间大于抓取时间 或者全量抓取 则进行页面抓取
            if updateDate.date() >= self.scrapy_date.date() or self.is_inc == 'false':
                link = movie.css('a::attr(href)').extract_first()
                if link == None: continue
                yield Request(self.baseUrl+link, callback=self.parse1)
    def parse1(self,response):
        movieItem = ProMovieItem()
        movieId =  CommoneUtils.getTableId()
        movieItem['id'] = movieId
        movieItem['source'] = self.name
        movieItem['sourcePageUrl'] = response.url

        showdesc = response.css('#showdesc::text').extract_first().strip()
        showdesc_list = re.split('   ',showdesc)
        print("{} 地址解析到的头部列表位{}".format(response.url,showdesc_list))
        movieItem['movieName'] = showdesc_list[0].split("：")[1]
        try:
            movieItem['updateDate'] = datetime.datetime.strptime(showdesc_list[1].split("：")[1],'%Y-%m-%d').timestamp()
        except Exception as e:
            print(e)
            movieItem['updateDate'] = datetime.datetime.now().timestamp()
            log.msg("电影地址:{}发布日期解析不到默认使用当前日期".format(response.url))

        movieItem['movieImgUrl'] = response.css('#showinfo > img::attr(src)').extract_first()
        # movieItem['movieName'] = response.css('#show > h3::text').extract_first()
        movieItem['movieDescr'] = ''
        infolist =  response.css('#showinfo > div::text').extract()
        descr_start = False
        for info in infolist :
            info = info.strip()
            realNameMatch = re.match('◎片　　名(.*)', info)
            movieYearMatch = re.match('◎年　　份(.*)', info) if re.match('◎年　　份(.*)', info) else re.match('◎年　　代(.*)', info)
            scoreMatch = re.match('◎豆瓣评分(.*)', info)
            descrMatch = re.match('◎简　　介', info)
            if realNameMatch:
                movieItem['movieRealName'] = realNameMatch.group(1).strip()
            if movieYearMatch:
                movieItem['movieYear'] = movieYearMatch.group(1).strip()
            if scoreMatch:
                movieItem['score'] = scoreMatch.group(1).strip()
            if descr_start :
                movieItem['movieDescr'] = movieItem['movieDescr'] + info
            if descrMatch:
                descr_start = True
        #如果解析后没有获取到电影名称则退出
        if not movieItem.get('movieName', None) or not movieItem.get('movieRealName', None):
            log.msg("电影地址:{}发布日期解析不到电影名称".format(response.url))
            return
        if len(movieItem['movieDescr'])>1000 : #如果描述太长则直接截断
            movieItem['movieDescr'] = movieItem['movieDescr'][0:999]
        moviePipelin = MoviePipeline()
        #如果已经有当前页面的电影链接存储过则直接退出
        if moviePipelin.movieLinkIsRepeat(movieItem['sourcePageUrl'],movieItem['source']):
            return
        self.crawler.stats.inc_value('movie_count')
        self.crawler.stats.get_value('movie_list').append(movieItem['movieRealName'])
        yield movieItem
        downList = response.css('#showinfo > table a::text').extract()
        for down_url in downList:
            downAdrressItem = ProMovieDownAddressItem()
            downAdrressItem['downType'] = "迅雷"
            downAdrressId = CommoneUtils.getTableId()
            downAdrressItem['id'] = downAdrressId
            downAdrressItem['movieId'] = movieId
            downAdrressItem['downAddress'] = down_url.strip()
            yield downAdrressItem
