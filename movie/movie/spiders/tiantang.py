import scrapy
import re
from movie.items import ProMovieItem, ProMovieDownAddressItem
from movie.utils.commoneUtils import CommoneUtils
from scrapy import Request

class Dy2018MovieScrapy(scrapy.Spider):
    name = 'dy2018'
    baseUrl = "https://www.dy2018.com"
    allowed_domains  = ["dy2018.com"]
    # start_urls = [
    #     # "https://www.dy2018.com/i/99150.html"
    #     "https://www.dy2018.com/html/gndy/dyzz/"
    # ]
    def start_requests(self):
        yield Request("https://www.dy2018.com/html/gndy/dyzz/", callback=self.parse0)
    def parse0(self, response):
        movieLinkList = response.css('.co_content8 > ul a::attr(href) ').extract()
        otherlinkList = response.css('.co_content8 > div a')
        for movielink in movieLinkList:
            currentUrl = self.baseUrl+movielink
            yield Request(currentUrl,callback=self.parse1)
        for otherlink in otherlinkList:
            isNextPage = otherlink.css('::text').extract_first()=='下一页'
            if isNextPage:
                yield Request(self.baseUrl+otherlink.css('::attr(href)').extract_first(), callback=self.parse1)

    def parse1(self, response):
        infos = response.css("#Zoom>p")
        movieItem = ProMovieItem()
        movieId =  CommoneUtils.getTableId()
        movieItem['id'] = movieId
        movieItem['source'] = self.name
        movieItem['sourcePageUrl'] = response.url
        pList =  infos.xpath('text()').extract()
        movieDescr = ""
        beginDescr = False
        movieItem['movieImgUrl'] = infos[0].xpath("//img/@src").extract_first()
        for p in pList:
            nameMatch = re.match('◎译　　名(.*)', p)
            realNameMatch = re.match('◎片　　名(.*)', p)
            movieYearMatch = re.match('◎年　　代(.*)', p)
            if nameMatch:
                movieItem['movieName'] = nameMatch.group(1)
            if realNameMatch:
                movieItem['movieRealName'] = realNameMatch.group(1)
            if movieYearMatch:
                movieItem['movieYear'] = movieYearMatch.group(1)
            if re.match('◎影片截图', p):
                beginDescr = False
            if beginDescr  == True:
                movieDescr = movieDescr + p
            if re.match('◎简　　介', p):
                beginDescr = True
        movieItem['movieDescr']=movieDescr
        downAdrressesUrl = response.css("#Zoom>table")
        for downAdrressUrlInfo in downAdrressesUrl:
            downAdrressItem = ProMovieDownAddressItem()
            url = downAdrressUrlInfo.css('a::attr(href)').extract_first()
            downAdrressItem['downType'] = "迅雷"
            downAdrressId = CommoneUtils.getTableId()
            downAdrressItem['id'] = downAdrressId
            downAdrressItem['movieId'] = movieId
            downAdrressItem['downAddress'] = url
            yield downAdrressItem
        yield movieItem

