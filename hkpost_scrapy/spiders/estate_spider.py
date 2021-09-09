import random
from urllib import parse

import django
from hkpost_scrapy.items import *

# 第二輪爬取-由屋邨逆向爬取：先獲取地域-地區的所有屋邨，找出沒有街道或者沒有街道門牌的屋邨，保存estates/phase數據
# eg:香港-香港仔-石排灣邨
from hkpost_scrapy.service.db_service import SpiderLogService
from hkpost_scrapy.spider_utils.utils import Utils

utils = Utils()
base_url = 'https://www.hongkongpost.hk/correct_addressing/'
estate_url = base_url + 'GetEstate.jsp?type_value=Estate&zone={zone}&district={district}&lang=en_US&estate=&street=&streetno=&status=0&phase=&building=&sid={sid}'
street_url = base_url + 'GetStreet.jsp?type_value=Street&zone={zone}&district={district}&lang=en_US&street=&estate={estate}&phase=&building=&sid={sid}'
street_no_url = base_url + 'GetStreetNo.jsp?street={street}&lang=en_US&lang1=en_US&district={district}&estate={estate}&phase=&building=&sid={sid}'
phase_url = base_url + 'GetPhase.jsp?estate={estate}&district={district}&street={street}&streetno={streetNo}&lang1=en_US&sid={sid}'
building_url = base_url + 'GetBuilding.jsp?type_value=Building&zone={zone}&district={district}&lang=en_US&building=&estate_name={estate}&street_name={street}&streetno={streetno}&phase={phase}&status=1&sid={sid}'
floor_url = base_url + 'GetFloor.jsp?strno={strno}&street={street}&estate={estate}&phase={phase}&building={building}&district={district}&lang1=en_US&sid={sid}'
unit_url = base_url + 'GetUnit.jsp?strno={strno}&street={street}&estate={estate}&phase={phase}&building={building}&district={district}&floor={floor}&lang1=en_US&sid={sid}'


class EstateSpider(scrapy.Spider):
    name = 'estate_spider'
    allowed_domains = ['www.hongkongpost.hk']
    start_time = django.utils.timezone.now()
    addr_district = None

    def __init__(self, category=None, district_key=None, *args, **kwargs):
        is_finished = SpiderLogService.is_spider_finished(self.name, district_key)
        self.save_end_log = False
        self.start_urls = []
        if is_finished:
            self.log("%s is already finished ! " % self.name)
        else:
            self.addr_district = SpiderLogService.query_district(district_key)
            if self.addr_district:
                SpiderLogService.save_spider_log(EstateSpider.name, EstateSpider.start_time, district_key, 'START')
                self.save_end_log = True
                self.start_urls.append(
                    estate_url.format(zone=self.addr_district.zone_key, district=self.addr_district.district_key,
                                      sid=random.random()))

    def parse(self, response):
        options = response.xpath("//select/option")
        for op in options:
            if len(op.xpath("@value").extract()[0]) > 0:
                estate = Estate()
                estate["zone_key"] = self.addr_district.zone_key
                estate["zone_name"] = self.addr_district.zone_name
                estate['district_key'] = self.addr_district.district_key
                estate['district_name'] = self.addr_district.district_name
                estate["estate_key"] = op.xpath("@value").extract()[0]
                estate["estate_name"] = op.xpath("text()").extract()[0]

                next_url = street_url.format(zone=estate['zone_key'], district=estate['district_key'],
                                             estate=estate['estate_key'], sid=random.random())
                yield scrapy.Request(next_url, callback=self.parse_street, meta={"estate": estate})

    def parse_street(self, response):
        estate = response.meta['estate']
        options = response.xpath("//select/option")
        if len(options) == 1:
            # when street_key is null ,street_no_key must be null too, so save estate
            estate['street_key'] = ''
            estate['street_name'] = ''
            estate['street_no_key'] = ''
            estate['street_no_name'] = ''
            yield estate

            next_url = phase_url.format(street=estate['street_key'], streetNo=estate['street_no_key'],
                                        district=estate['district_key'], estate=estate['estate_key'],
                                        sid=random.random())
            yield scrapy.Request(next_url, callback=self.parse_phase, meta={"estate": estate})

        else:
            for op in options:
                if len(op.xpath("@value").extract()[0]) > 0:
                    estate_1 = utils.copy_value_from_item(estate, Estate)
                    estate_1['street_key'] = op.xpath("@value").extract()[0]
                    estate_1['street_name'] = op.xpath("text()").extract()[0]
                    # estate with street_key will be saved in parse_street_no function, and save with street_no info

                    next_url = street_no_url.format(street=estate_1['street_key'], district=estate_1['district_key'],
                                                    estate=estate_1['estate_key'], sid=random.random())
                    yield scrapy.Request(next_url, callback=self.parse_street_no, meta={"estate_key": estate_1['estate_key'],"estate_name":estate_1['estate_name'] , "street":estate_1})

    def parse_street_no(self, response):
        street = response.meta['street']
        estate_key = response.meta['estate_key']
        estate_name = response.meta['estate_name']
        options = response.xpath("//select/option")
        if len(options) == 1:
            streetNo = utils.copy_value_from_item(street, StreetNo)
            streetNo['street_no_key'] = ''
            streetNo['street_no_name'] = ''
            estate = utils.copy_value_from_item(streetNo, Estate)
            estate['estate_key'] = estate_key
            estate['estate_name'] = estate_name
            yield estate

            next_url = phase_url.format(street=estate['street_key'], streetNo=estate['street_no_key'],
                                        district=estate['district_key'], estate=estate['estate_key'],
                                        sid=random.random())
            yield scrapy.Request(next_url, callback=self.parse_phase, meta={"estate": estate})
        else:
            for op in options:
                if len(op.xpath("@value").extract()[0]) > 0:
                    streetNo = utils.copy_value_from_item(street, StreetNo)
                    streetNo['street_no_key'] = op.xpath("@value").extract()[0]
                    streetNo['street_no_name'] = op.xpath("text()").extract()[0]
                    estate = utils.copy_value_from_item(streetNo, Estate)
                    estate['estate_key'] = estate_key
                    estate['estate_name'] = estate_name
                    # yield streetNo
                    yield estate

                    next_url = phase_url.format(street=estate['street_key'], streetNo=estate['street_no_key'],
                                                district=estate['district_key'], estate=estate['estate_key'], sid=random.random())
                    yield scrapy.Request(next_url, callback=self.parse_phase, meta={"estate": estate})

    def parse_phase(self, response):
        estate = response.meta['estate']
        options = response.xpath("//select/option")
        if len(options) == 1:
            phase = utils.copy_value_from_item(estate, Phase)
            phase["phase_key"] = ""
            phase["phase_name"] = ""
            # yield phase  {}&streetno={}&phase={phase
            next_url = building_url.format(zone=phase['zone_key'], district=phase['district_key'],
                                        street=phase['street_key'], streetno=phase['street_no_key'],
                                        estate=phase['estate_key'], phase=phase['phase_key'],
                                        sid=random.random())
            yield scrapy.Request(next_url, callback=self.parse_building, meta={"phase": phase})
        else:
            for op in options:
                if len(op.xpath("@value").extract()[0]) > 0:
                    phase = utils.copy_value_from_item(estate, Phase)
                    phase["phase_key"] = op.xpath("@value").extract()[0]
                    phase["phase_name"] = op.xpath("text()").extract()[0]
                    yield phase

                    next_url = building_url.format(zone=phase['zone_key'], district=phase['district_key'],
                                                   street=phase['street_key'], streetno=phase['street_no_key'],
                                                   estate=phase['estate_key'], phase=phase['phase_key'],
                                                   sid=random.random())
                    yield scrapy.Request(next_url, callback=self.parse_building, meta={"phase": phase})

    def parse_building(self, response):
        phase = response.meta["phase"]
        options = response.xpath("//select/option")
        # if street_key not none, building data would be handled in building_spider
        if len(phase['street_key']) == 0:
            if len(options) > 1:
                for op in options:
                    if len(op.xpath("@value").extract()[0]) > 0 :
                        building = utils.copy_value_from_item(phase, Building)
                        building["building_key"] = op.xpath("@value").extract()[0]
                        building["building_name"] = op.xpath("text()").extract()[0].lstrip().rstrip()
                        full_name_reverse, full_name = utils.get_building_full_name(building)
                        building['full_name_reverse'] = full_name_reverse
                        building['full_name'] = full_name
                        yield building

                        next_url = floor_url.format(district=building['district_key'], street=building['street_key'],
                                                    strno=building['street_no_key'], estate=building['estate_key'],
                                                    phase=building['phase_key'], building=building['building_key'],
                                                    sid=random.random())
                        yield scrapy.Request(next_url, callback=self.parse_floor, meta={"building": building})

            else:
                building = utils.copy_value_from_item(phase, Building)
                building["building_key"] = ''
                building["building_name"] = ''
                # continue crawl floor data
                next_url = floor_url.format(district=building['district_key'], street=building['street_key'],
                                            strno=building['street_no_key'], estate=building['estate_key'],
                                            phase=building['phase_key'], building=building['building_key'],
                                            sid=random.random())
                yield scrapy.Request(next_url, callback=self.parse_floor, meta={"building": building})

    def parse_floor(self, response):
        building = response.meta["building"]
        options = response.xpath("//select/option")
        if len(options) == 1:
            # no floors but has units,eg:香港 深水灣 深水灣道 6   ROCKY BANK  6號
            floor = utils.copy_value_from_item(building, Floor)
            floor['floor_key'] = ''
            floor['floor_name'] = ''
            next_url = unit_url.format(district=floor['district_key'],
                                       building=floor['building_key'],
                                       strno=floor['street_no_key'],
                                       street=floor['street_key'],
                                       estate=floor['estate_key'],
                                       phase=floor['phase_key'],
                                       floor=floor['floor_key'],
                                       sid=random.random())
            yield scrapy.Request(next_url, callback=self.parse_unit, meta={"floor": floor})

        else:
            for op in options:
                value = op.xpath("@value").extract()[0]
                if len(value) > 0 and 'notinlist' not in value:
                    floor = utils.copy_value_from_item(building, Floor)
                    floor['floor_key'] = value
                    floor['floor_name'] = op.xpath("text()").extract()[0]
                    yield floor

                    next_url = unit_url.format(district=floor['district_key'],
                                               building=floor['building_key'],
                                               strno=floor['street_no_key'],
                                               street=floor['street_key'],
                                               estate=floor['estate_key'],
                                               phase=floor['phase_key'],
                                               floor=floor['floor_key'],
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
            unit['unit_key'] = ''
            unit['unit_name'] = ''
            if len(floor['floor_key']) > 0:
                street_no_name = unit['street_no_name']
                unit['full_name_ch'] = utils.get_full_name_ch(keys, unit)
                unit['full_name_en'] = utils.get_full_name_en(keys, unit)
                unit['street_no_name'] = street_no_name
                yield unit