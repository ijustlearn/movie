# movie scrapy 电影爬虫
**该爬虫在python3.4环境下开发，理论支持3.4以及以上版本,配置mysql进行数据存储，有兴趣可以自己改别的pipeline，mysql需要新建一个movie库并执行movie.sql脚本**
## 功能介绍
**该爬虫实现了爬取[飘花电影网](https://www.piaohua.com/)与[电影天堂](https://www.dy2018.com/) 电影爬取爬取的字段包括：电影名称 年份 豆瓣评分 电影描述 海报链接 更新时间 来源 下载链接 等信息**
## 截图
![](https://github.com/ijustlearn/movie/blob/master/image1.png) ![](https://github.com/ijustlearn/movie/blob/master/image2.png)
## centos下安装方法
1. wget  https://github.com/ijustlearn/movie/archive/master.zip
2. `unzip master.zip`
3. `cd movie-master/movie/`
4. `virtualenv -p python3 --no-site-packages venv`
5. `source venv/bin/activate`
6. 部署到linux系统请把pywin32==223 从 requirements.txt中去掉（这个包是用于windows开发时debug用的）
7. `pip install -r requirements.txt`
8. `wim settings`文件,配置sql地址,以及邮件发送地址
9. mysql新增movie库字符集选择utf-8, 然后执行mvoie.sql脚本
9. `scrapy crawl piaohua -a is_inc=true` #爬取飘花网is_inc=true增量爬取，false全量爬取 
10. `scrapy crawl dy2018 -a is_inc=true` #爬取电影天堂网is_inc=true增量爬取，false全量爬
----
## 报错解决：
1. 报错  Invalid environment marker: python_version < '3' 请使用 `pip3 install  -r requirements.txt`
2. 报错 twisted/test/raiser.c:4:20: fatal error: Python.h: No such file or directory  参考https://stackoverflow.com/questions/43047284/how-to-install-python3-devel-on-red-hat-7 安装 python3-devel
## 其他：
本爬虫严禁用于任何商业用途，如果好用请star，谢谢~
