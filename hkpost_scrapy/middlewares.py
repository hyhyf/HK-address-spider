# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import random

from scrapy import signals
from scrapy.downloadermiddlewares.redirect import BaseRedirectMiddleware

from hkpost_scrapy.service.db_service import SpiderLogService
from hkpost_scrapy.settings import USER_AGENT_LIST


class HkpostScrapySpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(s.spider_error, signal=signals.spider_error)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.
        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        # spider.crawler.engine.close_spider(spider, 'process_spider_exception')
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    def spider_closed(self, spider, reason):
        spider.logger.info('{0} closed, reason: {1}'.format(spider.name, reason))
        if spider.save_end_log :
            if reason == "finished":
                SpiderLogService.save_spider_log(spider.name, spider.start_time,
                                                 spider.addr_district.district_key if spider.addr_district is not None else None
                                                 , 'END')
            else:
                SpiderLogService.save_spider_log(spider.name, spider.start_time,
                                                 spider.addr_district.district_key if spider.addr_district is not None else None
                                                 , 'ERROR')

    # 当spider的回调函数产生错误时(例如，抛出异常)，该信号被发送。
    def spider_error(self, failure, response, spider):
        code = response.status
        print('error occurs when process spider datas!')
        spider.crawler.engine.close_spider(spider, "error occurs when process spider datas!close spider!!")


class HkpostScrapyDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.
        # 检验一下请求头
        # print(request.headers['User-Agent'])
        # 获取一个请求头
        ua = random.choice(USER_AGENT_LIST)
        # 设置请求头代理
        request.headers['User-Agent'] = ua
        request.headers['origin'] = "https://www.hongkongpost.hk"
        request.headers['referer'] = "https://www.hongkongpost.hk/correct_addressing/index.jsp?lang=en_US"
        request.headers['accept-language'] = "en-US,en;q=0.9"
        request.headers['accept-encoding'] = "gzip, deflate, br"

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        if response.status != 200:
            SpiderLogService.save_error_log(spider.name, response.status,
                                            spider.addr_district.district_key if spider.addr_district is not None else None,
                                            request.url,
                                            '')
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        print("exception occurs!!")
        spider.close('exception occurs!!')
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY):
            with open(str(spider.name) + ".txt", "a") as f:
                f.write(str(request) + "\n")
            return None

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

