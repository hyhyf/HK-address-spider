import django
import scrapy

from hkpost_scrapy.items import SpiderLog, District, Zone
from urllib import parse

from hkpost_scrapy.service.db_service import SpiderLogService
from hkpost_scrapy.spider_utils.utils import Utils

utils = Utils()


class DistrictSpider(scrapy.Spider):
    name = 'district_spider'
    allowed_domains = ['www.hongkongpost.hk/']
    start_time = django.utils.timezone.now()

    def __init__(self, category=None, *args, **kwargs):
        self.addr_district = None
        self.save_end_log = False
        is_finished = SpiderLogService.is_spider_finished(self.name)
        if is_finished:
            self.log("%s is already finished ! " % self.name)
            self.start_urls = []
        else:
            SpiderLogService.save_spider_log(DistrictSpider.name, DistrictSpider.start_time, self.addr_district, 'START')
            self.save_end_log = True
            self.start_urls = utils.init_start_district_Urls()
            zones = utils.cache_zones
            for z in zones:
                zone = Zone()
                zone['id'] = z['id']
                zone['name'] = z['name']
                zone.save()

    def parse(self, response):
        self.log('A response from %s just arrived!' % response.url)
        url_params = parse.parse_qs(parse.urlparse(response.url).query)
        options = response.xpath("//select/option")
        for op in options:
            if len(op.xpath("@value").extract()[0]) > 0:
                district = District()
                district["zone_key"] = url_params['zone_value'][0]
                district["zone_name"] = utils.get_zone_name(district["zone_key"])
                district["district_key"] = op.xpath("@value").extract()[0]
                district["district_name"] = op.xpath("text()").extract()[0]
                yield district
