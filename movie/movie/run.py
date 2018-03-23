# -*- coding: utf-8 -*-
# @Time     : 2017/1/1 17:51
# @Author   : woodenrobot


from scrapy import cmdline


name = 'piaohua'
is_inc  = 'false'
cmd = 'scrapy crawl {0} -a is_inc={1}'.format(name,is_inc)
cmdline.execute(cmd.split())