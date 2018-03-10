# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import time


class ProMovieItem(scrapy.Item):
    id = scrapy.Field() #id
    movieName = scrapy.Field() #电影名称
    movieDescr = scrapy.Field() #电影描述
    movieImgUrl = scrapy.Field() #电影图片url
    movieYear = scrapy.Field() #电影年份
    movieRealName = scrapy.Field() #电影原本名称
    createTime = scrapy.Field() #创建时间
    enable = scrapy.Field() #是否启用
    source = scrapy.Field() #是否启用
    sourcePageUrl = scrapy.Field() #是否启用


class ProMovieDownAddressItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field() #id
    movieId = scrapy.Field() #电影id
    downAddress = scrapy.Field() #电影下载地址
    downType = scrapy.Field() #下载类型
