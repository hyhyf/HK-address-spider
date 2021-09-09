# -*- coding: utf-8 -*-

# Scrapy settings for hkpost_scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import logging
import sys
import os
from logging.handlers import RotatingFileHandler

import django
from scrapy.utils.log import configure_logging

BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
PRO_ROOT = os.path.dirname(BASE_DIR)  # 两个项目共同的根目录

sys.path.append(os.path.join(PRO_ROOT, 'hkpost_addr_spider'))
sys.path.append(os.path.join(BASE_DIR, 'hkpost_scrapy'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'hkpost_addr_spider.settings'
django.setup()

LOG_ENABLED = False
configure_logging(install_root_handler=False)

log_file = './spider_logs.log'
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logHandler = RotatingFileHandler(log_file, maxBytes=1073741824, backupCount=1, encoding='utf-8')
logHandler.setLevel(logging.DEBUG)
logHandler.setFormatter(formatter)
root_logger.addHandler(logHandler)

SPIDER_MODULES = ['hkpost_scrapy.spiders']
NEWSPIDER_MODULE = 'hkpost_scrapy.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'hkpost_scrapy (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1

REDIRECT_ENABLED = False
RETRY_ENABLED = True
RETRY_TIMES = 999999
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 400, 403, 402, 408, 302]

# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

USER_AGENT_LIST = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; HCI0449; .NET CLR 1.0.3705) ",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; i-NavFourF; .NET CLR 1.1.4322) ",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Maxthon; ",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
]

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    'hkpost_scrapy.middlewares.HkpostScrapySpiderMiddleware': 543,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'hkpost_scrapy.middlewares.HkpostScrapyDownloaderMiddleware': 543,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 600,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'hkpost_scrapy.pipelines.HkpostScrapyPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
