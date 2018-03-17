import pymysql
from scrapy import  log
from scrapy.exceptions import DropItem

from movie import settings
from movie.items import ProMovieItem,ProMovieDownAddressItem
from movie.utils.commoneUtils import  CommoneUtils
@CommoneUtils.singleton
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
                item.setdefault('createTime',CommoneUtils.current_milli_time())
                item.setdefault('enable','Y')
                self.cursor.execute("""insert into pro_movie (id,movie_name,movie_descr,movie_img_url,movie_year,movie_real_name,create_time,enable,source,source_page_url,update_date) VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                                    (item['id'],item['movieName'],item['movieDescr'],item['movieImgUrl'],item['movieYear'],item['movieRealName'],item['createTime'],item['enable'],item['source'],item['sourcePageUrl'],item['updateDate'],))
                #print("""insert into pro_movie (id,movie_name,movie_descr,movie_img_url,movie_year,movie_real_name,create_time,enable) VALUE ({},{},{},{},{},{},{},%s)""".format(item['id'],item['movieName'],item['movieDescr'],item['movieImgUrl'],item['movieYear'],item['movieRealName'],item['createTime'],item['enable']))
                self.connect.commit()
            except Exception as e :
                log.msg("存数据出错")
                self.connect.rollback()
                raise e
            return item
        if item.__class__ == ProMovieDownAddressItem:
            try:
                self.cursor.execute("""insert into pro_movie_down_address (id,movie_id,down_address,down_type) VALUE (%s,%s,%s,%s)""",
                                    (item['id'],item['movieId'],item['downAddress'],item['downType']))
                self.connect.commit()
            except Exception as e :
                self.connect.rollback()
                raise e
            return item
        else:
            pass
    def movieLinkIsRepeat(self,sourcePageUrl:str,source:str) -> bool:
        """
        检查电影来源链接是否已经存储过避免重复存储
        :param sourcePageUrl: 来源页面
        :param source: 来源类型
        :return: 真假
        """
        self.cursor.execute("select id from pro_movie where source_page_url = %s and source = %s",
                            (sourcePageUrl, source))
        ret = self.cursor.fetchone()
        if ret:
            return True
        return False

