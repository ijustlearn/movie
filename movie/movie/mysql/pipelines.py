import pymysql
from scrapy import  log
from scrapy.exceptions import DropItem

from movie import settings
from movie.items import ProMovieItem,ProMovieDownAddressItem
from movie.utils.commoneUtils import  CommoneUtils
class MoviePipeline():
    def __init__(self):
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            db=settings.MYSQL_DBNAME,
            charset='utf8',
            use_unicode=True)
        self.cursor = self.connect.cursor()
    def __del__(self):
        try:
            self.connect.close()
        except Exception as e :
            pass
    def process_item(self,item,spider):
        if item.__class__ == ProMovieItem:
            try:
                if  not  item.get('movieName',None) or not  item.get('movieRealName',None):
                    log.msg("电影名称没有获取到")
                    raise DropItem()
                self.cursor.execute("select id from pro_movie where source_page_url = %s and source = %s",(item['sourcePageUrl'],item['source']))
                ret = self.cursor.fetchone()
                if ret:
                    log.msg("已存在")
                    raise DropItem()
                item.setdefault('createTime',CommoneUtils.current_milli_time())
                item.setdefault('enable','Y')
                self.cursor.execute("""insert into pro_movie (id,movie_name,movie_descr,movie_img_url,movie_year,movie_real_name,create_time,enable,source,source_page_url) VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                                    (item['id'],item['movieName'],item['movieDescr'],item['movieImgUrl'],item['movieYear'],item['movieRealName'],item['createTime'],item['enable'],item['source'],item['sourcePageUrl'],))
                #print("""insert into pro_movie (id,movie_name,movie_descr,movie_img_url,movie_year,movie_real_name,create_time,enable) VALUE ({},{},{},{},{},{},{},%s)""".format(item['id'],item['movieName'],item['movieDescr'],item['movieImgUrl'],item['movieYear'],item['movieRealName'],item['createTime'],item['enable']))
                self.connect.commit()
            except Exception as e :
                self.connect.rollback()
                raise e
            return item
        if item.__class__ == ProMovieDownAddressItem:
            try:
                # self.cursor.execute("select id from pro_movie where id = %s",(item['movieId']))
                # ret = self.cursor.fetchone()
                # if not ret:
                #     log.msg("movieId不存在，丢弃链接")
                #     raise DropItem()
                self.cursor.execute("""insert into pro_movie_down_address (id,movie_id,down_address,down_type) VALUE (%s,%s,%s,%s)""",
                                    (item['id'],item['movieId'],item['downAddress'],item['downType']))
                self.connect.commit()
            except Exception as e :
                self.connect.rollback()
                raise e
            return item
        else:
            pass
