import datetime
import re

from scrapy.crawler import Crawler
from scrapy import log
import scrapy
from scrapy import Request

from movie.items import ProMovieItem, ProMovieDownAddressItem
from movie.mysql.pipelines import MoviePipeline
from movie.utils.commoneUtils import CommoneUtils
from scrapy.mail import MailSender


class piaohuaMovieScrapy(scrapy.Spider):
    name = 'piaohua'
    baseUrl = "https://www.piaohua.com"
    allowed_domains = ["piaohua.com"]
    is_inc = 'true'
    scrapy_date = datetime.datetime.now()  # 从哪天抓取数据默认当天

    # scrapy_date = datetime.datetime.strptime('2018-03-27', '%Y-%m-%d')
    def __init__(self, is_inc='true', *args, **kwargs):
        super(piaohuaMovieScrapy, self).__init__(*args, **kwargs)
        self.is_inc = is_inc
        if is_inc == 'false':
            print("全量抓取电影")
        else:
            print("增量抓取电影")
            print("抓取日期：{}的电影".format(self.scrapy_date.strftime("%Y-%m-%d")))

    def closed(self, reason):
        # 爬取完成后进行邮件通知
        mailer = MailSender.from_settings(self.settings)
        body = '''本次爬取状态:{}\r\n本次爬取电影数量:{}\r\n本次爬取电影列表:{}'''.format(reason, self.crawler.stats.get_value('movie_count'),
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

    def parse2(self, response):
        currentUrl = re.match('.*/', response.url).group(0)
        movieLinkList = response.css('#list > dl > dt > a::attr(href)').extract()
        for movieUrl in movieLinkList:
            yield Request(self.baseUrl + movieUrl, callback=self.parse1)
        pageUrlList = response.css('div#nml > div.page > a::attr(href)').extract()
        for pageUrl in pageUrlList:
            # if pageUrl not in scrapyedUrls: 使用系统url去重
            yield Request(currentUrl + pageUrl, callback=self.parse2)

    def parse0(self, response):
        movieList = response.css(".col-sm-4.col-md-3.col-lg-2")
        for movie in movieList:
            updateDateStr = movie.css('span::text').extract_first()
            if updateDateStr == None: updateDateStr = movie.css('span font::text').extract_first()
            if updateDateStr == None: continue
            updateDate = datetime.datetime.strptime(updateDateStr, '%Y-%m-%d')
            # 如果更新时间大于抓取时间 或者全量抓取 则进行页面抓取
            if updateDate.date() >= self.scrapy_date.date() or self.is_inc == 'false':
                link = movie.css('a::attr(href)').extract_first()
                if link == None: continue
                yield Request(self.baseUrl + link, callback=self.parse1)

    def parse1(self, response):
        movieItem = ProMovieItem()
        movieId = CommoneUtils.getTableId()
        movieItem['id'] = movieId
        movieItem['source'] = self.name
        movieItem['sourcePageUrl'] = response.url

        showdesc_list = response.css('.info span::text').extract()
        movieItem['movieName'] = showdesc_list[0].split("：")[1]
        try:
            movieItem['updateDate'] = datetime.datetime.strptime(showdesc_list[1].split("：")[1], '%Y-%m-%d').timestamp()
        except Exception as e:
            print(e)
            movieItem['updateDate'] = datetime.datetime.now().timestamp()
            log.msg("电影地址:{}发布日期解析不到默认使用当前日期".format(response.url))
        movieImgUrl = response.css('.txt img::attr(src)').extract_first()
        if movieImgUrl.find('/') == 0:
            movieImgUrl = self.baseUrl + movieImgUrl
        movieItem['movieImgUrl'] = movieImgUrl
        # movieItem['movieName'] = response.css('#show > h3::text').extract_first()
        movieItem['movieDescr'] = ''

        infolist = response.css('.info span::text').extract()
        # 因为电影页面有可能不一样，需要判断出是哪种界面，总共有三种界面，使用两种解析方式解析

        if len(infolist) > 5:
            self.__parse_movie_item_1(infolist, movieItem)
        else:
            infolist = response.css('.txt div::text').extract()
            isCategory1 = False
            for info in infolist:
                info = info.strip()
                math = re.match('◎', info)
                if math:
                    isCategory1 = True
                    break
            if isCategory1:
                self.__parse_movie_item_1(infolist, movieItem)
            else:
                self.__parse_movie_item_2(infolist, movieItem)


        # 如果解析后没有获取到电影名称则退出
        if not movieItem.get('movieName', None) and not movieItem.get('movieRealName', None):
            log.msg("电影地址:{}发布日期解析不到电影名称".format(response.url))
            return
        if len(movieItem['movieDescr']) > 1000:  # 如果描述太长则直接截断
            movieItem['movieDescr'] = movieItem['movieDescr'][0:999]
        moviePipelin = MoviePipeline()
        # 如果已经有当前页面的电影链接存储过则直接退出
        if moviePipelin.movieLinkIsRepeat(movieItem['sourcePageUrl'], movieItem['source']):
            return
        self.crawler.stats.inc_value('movie_count')
        self.crawler.stats.get_value('movie_list').append(movieItem['movieName'])
        yield movieItem
        downList1 = response.xpath('//a[contains(@href,"magnet")]/@href').extract()
        downList2 = response.xpath('//a[contains(@href,"ftp")]/@href').extract()
        downList1.extend(downList2)
        for down_url in downList1:
            downAdrressItem = ProMovieDownAddressItem()
            downAdrressItem['downType'] = "迅雷"
            downAdrressId = CommoneUtils.getTableId()
            downAdrressItem['id'] = downAdrressId
            downAdrressItem['movieId'] = movieId
            downAdrressItem['downAddress'] = down_url.strip()
            yield downAdrressItem

    def __parse_movie_item_1(self, infolist, movieItem):
        """
        类似<div class="txt">
        ◎译　　名　
        <br>
        ◎片　　名　Super Typhoon
        <br>
        ◎年　　代　2008
        <br>
        ◎国　　家　中国
        <br>
        ◎类　　别　惊悚/剧情/动作
        <br>
        ◎语　　言　国语
        <br>
        ◎字　　幕　中文
        <br>
        ......
        </div>

        或者：

        <div>
        <div>◎译　　名　黑色党徒/Black Klansman</div>
        <div>◎片　　名　BlacKkKlansman</div>
        <div>◎年　　代　2018</div>
        ......
        </div>
        这种格式页面的解析

        :param infolist:
        :param movieItem:
        :return ProMovieItem:
        """
        descr_start = False
        for info in infolist:
            info = info.strip()
            realNameMatch = re.match('◎片　　名(.*)', info)
            movieYearMatch = re.match('◎年　　份(.*)', info) if re.match('◎年　　份(.*)', info) else re.match('◎年　　代(.*)', info)
            scoreMatch = re.match('◎豆瓣评分(.*)', info)
            descrMatch = re.match('◎简　　介', info)
            otherMatch = re.match('◎', info)
            if realNameMatch:
                movieItem['movieRealName'] = realNameMatch.group(1).strip()
            if movieYearMatch:
                movieItem['movieYear'] = movieYearMatch.group(1).strip()
            if scoreMatch:
                movieItem['score'] = scoreMatch.group(1).strip()
            if descr_start:
                if otherMatch:
                    descr_start = False
                    continue
                movieItem['movieDescr'] = movieItem['movieDescr'] + info
            if descrMatch:
                descr_start = True
        return movieItem

    def __parse_movie_item_2(self, infolist, movieItem):
        """
        类似 <div class="txt">
        <div> 导演: 约翰·卢森霍普</div>
        <div> 编剧: 约翰·卢森霍普 / 戴维·亚伦·科恩</div>
        <div> 主演: 约翰·特拉沃尔塔 / 詹迪·莫拉 / 凯瑟琳·温妮克 / 米拉·索维诺 / 凯南·鲁兹 / 马修·莫迪恩 / 詹姆斯·瑞马尔 / 阿莫里·诺拉斯科</div>
        <div> 类型: 剧情 / 动作</div>
        <div> 制片国家/地区: 美国</div>
        <div> 上映日期: 2018-11-16(美国)</div>
        <div> 片长: 102分钟</div>
        </div>
        这种格式的页面解析
        :param infolist:
        :param movieItem:
        :return ProMovieItem:
        """
        i = 1
        for info in infolist:
            info = info.strip()
            movieYearMatch = re.match('上映日期:(.*)', info)
            if movieYearMatch:
                movieItem['movieYear'] = movieYearMatch.group(1).strip()
            movieItem['score'] = '无'
            if i == len(infolist):
                movieItem['movieDescr'] = info
            i += 1
        return movieItem
