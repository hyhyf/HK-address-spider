import random

import django

from hkpost_scrapy.items import *

from hkpost_scrapy.service.db_service import SpiderLogService
from hkpost_scrapy.spider_utils.utils import Utils

utils = Utils()
base_url = 'https://www.hongkongpost.hk/correct_addressing/'
street_url = base_url + 'GetStreet.jsp?type_value=Street&zone={zone}&district={district}&lang=en_US&street=&estate=&phase=&building=&sid={sid}'
street_no_url = base_url + 'GetStreetNo.jsp?street={street}&lang=en_US&lang1=en_US&district={district}&estate=&phase=&building=&sid={sid}'
estate_url = base_url + 'GetEstate.jsp?type_value=Estate&zone={zone}&district={district}&lang=en_US&estate=&street={street}&streetno={streetNo}&status=1&phase=&building=&sid={sid}'
phase_url = base_url + 'GetPhase.jsp?estate={estate}&district={district}&street={street}&streetno={streetNo}&lang1=en_US&sid={sid}'
building_url = base_url + 'GetBuilding.jsp?type_value=Building&zone={zone}&district={district}&lang=en_US&building=&estate_name={estate}&street_name={street}&streetno={streetNo}&phase={phase}&status=1&sid={sid}'
floor_url = base_url + 'GetFloor.jsp?strno={strno}&street={street}&estate={estate}&phase={phase}&building={building}&district={district}&lang1=en_US&sid={sid}'
unit_url = base_url + 'GetUnit.jsp?strno={streetNo}&street={street}&estate={estate}&phase={phase}&building={building}&district={district}&floor={floor}&lang1=en_US&sid={sid}'
# 第三輪爬取-由地域-地區-街道-門牌等正向獲取，拿到所有的building數據,save


class BuildingSpider(scrapy.Spider):
    name = 'building_spider'
    allowed_domains = ['www.hongkongpost.hk']
    start_time = django.utils.timezone.now()
    addr_district = None

    def __init__(self, category=None, district_key=None, *args, **kwargs):
        self.district = district_key
        is_finished = SpiderLogService.is_spider_finished(self.name, district_key)
        self.save_end_log = False
        self.start_urls = []
        if is_finished:
            self.log("%s is already finished ! " % self.name)
        else:
            self.addr_district = SpiderLogService.query_district(district_key)
            if self.addr_district:
                SpiderLogService.save_spider_log(BuildingSpider.name, BuildingSpider.start_time, district_key, 'START')
                self.save_end_log = True
                self.start_urls.append(
                    street_url.format(zone=self.addr_district.zone_key, district=self.addr_district.district_key,
                                      sid=random.random()))

    def parse(self, response):
        self.log('A response from %s just arrived!' % response.url)
        options = response.xpath("//select/option")
        for op in options:
            if len(op.xpath("@value").extract()[0]) > 0:
                street = Street()
                street["zone_key"] = self.addr_district.zone_key
                street["zone_name"] = self.addr_district.zone_name
                street['district_key'] = self.addr_district.district_key
                street['district_name'] = self.addr_district.district_name
                street["street_key"] = op.xpath("@value").extract()[0]
                street["street_name"] = op.xpath("text()").extract()[0]
                yield street

                next_url = street_no_url.format(street=street['street_key'], district=street['district_key'],
                                                sid=random.random())
                yield scrapy.Request(next_url, callback=self.parse_street_no, meta={"street": street})

    def parse_street_no(self, response):
        street = response.meta["street"]
        options = response.xpath("//select/option")
        if len(options) > 1:
            for op in options:
                if len(op.xpath("@value").extract()[0]) > 0:
                    street_no = utils.copy_value_from_item(street, StreetNo)
                    street_no["street_no_key"] = op.xpath("@value").extract()[0]
                    street_no["street_no_name"] = op.xpath("text()").extract()[0]
                    yield street_no

                    next_url = estate_url.format(zone=street_no['zone_key'], district=street_no['district_key'],
                                                 street=street_no['street_key'], streetNo=street_no['street_no_key'],
                                                 sid=random.random())
                    yield scrapy.Request(next_url, callback=self.parse_estate, meta={"streetNo": street_no})
        else:
            street_no = utils.copy_value_from_item(street, StreetNo)
            street_no["street_no_key"] = ""
            street_no["street_no_name"] = ""
            yield street_no
            next_url = estate_url.format(zone=street_no['zone_key'], district=street_no['district_key'],
                                         street=street_no['street_key'], streetNo=street_no['street_no_key'],
                                         sid=random.random())
            yield scrapy.Request(next_url, callback=self.parse_estate, meta={"streetNo": street_no})

    def parse_estate(self, response):
        street_no = response.meta["streetNo"]
        options = response.xpath("//select/option")
        if len(options) > 1:
            for op in options:
                if len(op.xpath("@value").extract()[0]) > 0:
                    estate = utils.copy_value_from_item(street_no, Estate)
                    estate["estate_key"] = op.xpath("@value").extract()[0]
                    estate["estate_name"] = op.xpath("text()").extract()[0]
                    yield estate

                    next_url = phase_url.format(district=estate['district_key'],
                                                street=estate['street_key'], streetNo=estate['street_no_key'],
                                                estate=estate['estate_key'], sid=random.random())
                    yield scrapy.Request(next_url, callback=self.parse_phase, meta={"estate": estate})
        else:
            estate = utils.copy_value_from_item(street_no, Estate)
            estate["estate_key"] = ""
            estate["estate_name"] = ""
            next_url = phase_url.format(district=estate['district_key'],
                                        street=estate['street_key'], streetNo=estate['street_no_key'],
                                        estate=estate['estate_key'], sid=random.random())
            yield scrapy.Request(next_url, callback=self.parse_phase, meta={"estate": estate})

    def parse_phase(self, response):
        estate = response.meta["estate"]
        options = response.xpath("//select/option")
        if len(options) > 1:
            for op in options:
                if len(op.xpath("@value").extract()[0]) > 0:
                    phase = utils.copy_value_from_item(estate, Phase)
                    phase["phase_key"] = op.xpath("@value").extract()[0]
                    phase["phase_name"] = op.xpath("text()").extract()[0]
                    yield phase

                    next_url = building_url.format(zone=phase['zone_key'], district=phase['district_key'],
                                                   street=phase['street_key'], streetNo=phase['street_no_key'],
                                                   phase=phase['phase_key'].replace('&', '%26'),
                                                   estate=phase['estate_key'], sid=random.random())
                    yield scrapy.Request(next_url, callback=self.parse_building, meta={"phase": phase})
        else:
            phase = utils.copy_value_from_item(estate, Phase)
            phase["phase_key"] = ""
            phase["phase_name"] = ""

            next_url = building_url.format(zone=phase['zone_key'], district=phase['district_key'],
                                           street=phase['street_key'], streetNo=phase['street_no_key'],
                                           estate=phase['estate_key'], phase=phase['phase_key'].replace('&', '%26'),
                                           sid=random.random())
            yield scrapy.Request(next_url, callback=self.parse_building, meta={"phase": phase})

    def parse_building(self, response):
        phase = response.meta["phase"]
        options = response.xpath("//select/option")
        if len(options) > 1:
            for op in options:
                if len(op.xpath("@value").extract()[0]) > 0:
                    building = utils.copy_value_from_item(phase, Building)
                    building["building_key"] = op.xpath("@value").extract()[0]
                    building["building_name"] = op.xpath("text()").extract()[0].lstrip().rstrip()
                    full_name_reverse, full_name = utils.get_building_full_name(building)
                    building['full_name_reverse'] = full_name_reverse
                    building['full_name'] = full_name
                    yield building
                    # there is any building,spider end, building floors and units will handle in unit_spider

                    next_url = floor_url.format(district=building['district_key'],
                                                building=building['building_key'].replace('&', '%26'),
                                                street=building['street_key'],
                                                estate=building['estate_key'],
                                                phase=building['phase_key'].replace('&', '%26'),
                                                strno=building['street_no_key'],
                                                sid=random.random())
                    yield scrapy.Request(next_url, callback=self.parse_floor, meta={"building": building})
        else:
            # when there is no building, continue crawl floor data
            building = utils.copy_value_from_item(phase, Building)
            building["building_key"] = ''
            building["building_name"] = ''
            next_url = floor_url.format(district=building['district_key'],
                                        building=building['building_key'].replace('&', '%26'),
                                        street=building['street_key'],
                                        estate=building['estate_key'],
                                        phase=building['phase_key'].replace('&', '%26'),
                                        strno=building['street_no_key'],
                                        sid=random.random())
            yield scrapy.Request(next_url, callback=self.parse_floor, meta={"building": building})

    def parse_floor(self, response):
        building = response.meta["building"]
        options = response.xpath("//select/option")
        building_1 = utils.copy_value_from_item(building, Building)

        if len(options) > 1:
            # no building exist but when len(options of floor and unit)>1 ,save building data
            self.log(' insert a new building : %s ' % building)
            if len(building_1['building_key']) == 0:
                building_1['building_key'] = ""
                building_1['building_name'] = building_1['street_key'] + " NO." + building_1[
                    'street_no_key'] + ' (' + utils.get_ch_chars(building_1['street_name']) + building_1[
                                                'street_no_key'] + "號)".lstrip().rstrip()
                full_name_reverse, full_name = utils.get_building_full_name(building_1)
                building_1['full_name_reverse'] = full_name_reverse
                building_1['full_name'] = full_name
                yield building_1

            for op in options:
                value = op.xpath("@value").extract()[0]
                if len(value) > 0 and 'notinlist' not in value:
                    floor = utils.copy_value_from_item(building_1, Floor)
                    floor['floor_key'] = value
                    floor['floor_name'] = op.xpath("text()").extract()[0]
                    yield floor

                    next_url = unit_url.format(district=floor['district_key'],
                                               streetNo=floor['street_no_key'],
                                               street=floor['street_key'],
                                               estate=floor['estate_key'],
                                               phase=floor['phase_key'].replace('&', '%26'),
                                               building=floor['building_key'].replace('&', '%26'),
                                               floor=floor['floor_key'].replace('&', '%26'),
                                               sid=random.random())
                    yield scrapy.Request(next_url, callback=self.parse_unit, meta={"floor": floor})

    def parse_unit(self, response):
        floor = response.meta["floor"]
        options = response.xpath("//select/option")

        keys = Unit.fields.keys()
        if len(options) > 1:
            for op in options:
                value = op.xpath("@value").extract()[0]
                if len(value) > 0 and 'notinlist' not in value:
                    unit = utils.copy_value_from_item(floor, Unit)
                    street_no_name = unit['street_no_name']
                    unit['unit_key'] = value
                    unit['unit_name'] = op.xpath("text()").extract()[0]
                    unit['full_name_ch'] = utils.get_full_name_ch(keys, unit)
                    unit['full_name_en'] = utils.get_full_name_en(keys, unit)
                    unit['street_no_name'] = street_no_name
                    yield unit
        else:
            unit = utils.copy_value_from_item(floor, Unit)
            street_no_name = unit['street_no_name']
            unit['unit_key'] = ''
            unit['unit_name'] = ''
            unit['full_name_ch'] = utils.get_full_name_ch(keys, unit)
            unit['full_name_en'] = utils.get_full_name_en(keys, unit)
            unit['street_no_name'] = street_no_name
            yield unit
