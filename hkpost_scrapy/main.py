# you can run command (python main.py --dkey=10 ) to crawl data whice district_key=10
# or you can run command (python main.py) to crawl all districts data

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
import time
import logging
from scrapy.utils.project import get_project_settings

import argparse

parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument('--dkey', type=str, default=None)
args = parser.parse_args()
district_key = args.dkey
print("crawl data by param :district_key = %s" % district_key)

# 在控制台打印日志
configure_logging()
# CrawlerRunner获取settings.py里的设置信息
runner = CrawlerRunner(get_project_settings())

from hkpost_scrapy.service.db_service import SpiderLogService

district_list = []
if district_key is None:
    district_list = SpiderLogService.get_all_district()
else:
    district_list.append(SpiderLogService.query_district(district_key))


@defer.inlineCallbacks
def crawl_address():
    if district_list:
        for district in district_list:
            logging.info("new cycle starting")
            yield runner.crawl("building_spider", district_key=district.district_key)
            time.sleep(3)
            yield runner.crawl("unit_spider", district_key=district.district_key)
            time.sleep(3)
        reactor.stop()


crawl_address()
reactor.run()

