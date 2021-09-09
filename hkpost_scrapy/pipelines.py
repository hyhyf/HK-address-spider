# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import django.db
from hkpost_scrapy.spiders.district_spider import utils


class HkpostScrapyPipeline(object):

    def process_item(self, item, spider):
        # 替換字段中的\xa0
        keys = item.fields.keys()
        for field in keys:
            if 'los_building_name' in field or 'id' in field:
                continue
            if 'name' in field:
                item[field] = item[field].replace(u'\xa0', u' ')
            if 'data_source' in field:
                item[field] = spider.name

        item["id"] = utils.generate_id(item)
        # 檢查mysql是否需要重連
        if not self.is_connection_usable():
            django.db.close_old_connections()

        item.save()
        return item

    def is_connection_usable(self):
        try:
            django.db.connection.connection.ping()
        except:
            return False
        else:
            return True

    # def close_spider(self, spider):
    #     """
    #     爬虫程序关闭时执行该函数
    #     用于初清理操作例如关闭数据库
    #     """
    #     print('---------------- %s finished ---------------- ' % spider.name)
    #     if spider.addr_district:
    #         SpiderLogService.save_spider_log(spider.name, spider.start_time,
    #                                          spider.addr_district.district_key, 'END')
    #     pass
    #
    # @classmethod
    # def from_crawler(cls, crawler):
    #     ins = cls(crawler.settings)
    #     crawler.signals.connect(ins.customize_close_spider, signal=signals.spider_closed)
    #     return ins
    #
    # def customize_close_spider(self, **kwargs):
    #     print("customize_close_spider kwargs: %s", kwargs)
    #     reason = kwargs.get("reason")  # reason maybe finished, shutdown or others
    #     spider = kwargs.get("spider")
    #     if reason == "finished":
    #         SpiderLogService.save_spider_log(spider.name, spider.start_time,
    #                                          spider.addr_district.district_key, 'END')
    #     else:
    #         print("close spider,reason:%s" % reason)
