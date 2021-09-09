import logging
import random
import django

from hkpost_scrapy.items import *
from hkpost_scrapy.service.db_service import SpiderLogService
from hkpost_scrapy.spider_utils.utils import Utils

utils = Utils()
base_url = 'https://www.hongkongpost.hk/correct_addressing/'
building_url = base_url + 'GetBuilding.jsp?type_value=Building&zone={zone}&district={district}&lang=en_US&building=&estate_name=&street_name=&streetno=&phase=&status=0&sid={sid}'
estate_url = base_url + 'GetEstate.jsp?type_value=Estate&zone={zone}&district={district}&lang=en_US&estate=&status=1&street=&streetno=&phase=&building={building}&sid={sid}'
check_estate_building_url = base_url + 'GetBuilding.jsp?type_value=Building&zone={zone}&district={district}&lang=en_US&building={building}&estate_name={estate}&street_name=&streetno=&phase=&status=1&sid={sid}'

street_url = base_url + 'GetStreet.jsp?type_value=Street&zone={zone}&district={district}&lang=en_US&street=&estate={estate}&phase=&building={building}&sid={sid}'
street_no_url = base_url + 'GetStreetNo.jsp?street={street}&lang=en_US&lang1=en_US&district={district}&estate={estate}&phase=&building={building}&sid={sid}'
# phase has no connection with building
phase_url = base_url + 'GetPhase.jsp?estate={estate}&district={district}&street={street}&streetno={streetNo}&lang1=en_US&sid={sid}'
floor_url = base_url + 'GetFloor.jsp?strno={strno}&street={street}&estate={estate}&phase={phase}&building={building}&district={district}&lang1=en_US&sid={sid}'
unit_url = base_url + 'GetUnit.jsp?strno={strno}&street={street}&estate={estate}&phase={phase}&building={building}&district={district}&floor={floor}&lang1=en_US&sid={sid}'
check_building_url = base_url + "GetBuilding.jsp?type_value=Building&zone={zone}&district={district}&lang=en_US&building=&estate_name={estate_name}&street_name={street_name}&streetno={streetNo}&phase={phase}&status=1&sid={sid}"


class UnitSpider(scrapy.Spider):
    name = 'unit_spider'
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
            SpiderLogService.save_spider_log(UnitSpider.name, UnitSpider.start_time, district_key, 'START')
            self.save_end_log = True
            self.start_urls.append(
                building_url.format(zone=self.addr_district.zone_key, district=self.addr_district.district_key,
                                    sid=random.random()))

    def parse(self, response):
        options = response.xpath("//select/option")
        for op in options:
            # logging.debug('option text ' + op.xpath("text()").extract()[0])
            if len(op.xpath("@value").extract()[0]) > 0:
                building = Building()
                building['zone_key'] = self.addr_district.zone_key
                building['zone_name'] = self.addr_district.zone_name
                building['district_key'] = self.addr_district.district_key
                building['district_name'] = self.addr_district.district_name
                building["building_key"] = op.xpath("@value").extract()[0]
                building["building_name"] = op.xpath("text()").extract()[0].lstrip().rstrip()

                next_url = estate_url.format(zone=building['zone_key'], district=building['district_key'],
                                             building=building['building_key'].replace('&', '%26'), sid=random.random())
                yield scrapy.Request(next_url, callback=self.parse_estate, meta={"building": building})

    def parse_estate(self, response):
        building = response.meta["building"]
        options = response.xpath("//select/option")
        if len(options) == 1:
            building['estate_key'] = ''
            building['estate_name'] = ''

            next_url = street_url.format(zone=building['zone_key'],
                                         district=building['district_key'],
                                         estate=building['estate_key'],
                                         building=building['building_key'].replace('&', '%26'),
                                         sid=random.random())
            yield scrapy.Request(next_url, callback=self.parse_street, meta={"building": building})
        else:
            for op in options:
                if len(op.xpath("@value").extract()[0]) > 0:
                    building_1 = utils.copy_value_from_item(building, Building)
                    building_1['estate_key'] = op.xpath("@value").extract()[0]
                    building_1['estate_name'] = op.xpath("text()").extract()[0]
                    # check building,in case building value changes while  estate value changes
                    next_url = check_estate_building_url.format(zone=building_1['zone_key'],
                                                                district=building_1['district_key'],
                                                                estate=building_1['estate_key'],
                                                                building=building_1['building_key'].replace('&', '%26'),
                                                                sid=random.random())

                    yield scrapy.Request(next_url, callback=self.check_building_estate, meta={"building": building_1, 'estate_num': len(options)})

    def check_building_estate(self, response):
        building = response.meta["building"]
        options = response.xpath("//select/option")
        estate_num = response.meta["estate_num"]

        if building['building_name'] not in [op.xpath("text()").extract()[0].strip() for op in options]:
            if estate_num == 2:
                building['estate_key'] = ''
                building['estate_name'] = ''
            else:
                return
        next_url = street_url.format(zone=building['zone_key'],
                                     district=building['district_key'],
                                     estate=building['estate_key'],
                                     building=building['building_key'].replace('&', '%26'),
                                     sid=random.random())
        yield scrapy.Request(next_url, callback=self.parse_street, meta={"building": building})

    def parse_street(self, response):
        building = response.meta["building"]
        options = response.xpath("//select/option")

        if len(options) == 1:
            building['street_key'] = ''
            building['street_name'] = ''

            next_url = street_no_url.format(street=building['street_key'], district=building['district_key'],
                                            estate=building['estate_key'],
                                            building=building['building_key'].replace('&', '%26'),
                                            sid=random.random())
            yield scrapy.Request(next_url, callback=self.parse_street_no, meta={"building": building})

        else:
            for op in options:
                if len(op.xpath("@value").extract()[0]) > 0:
                    building_1 = utils.copy_value_from_item(building, Building)
                    building_1['street_key'] = op.xpath("@value").extract()[0]
                    building_1['street_name'] = op.xpath("text()").extract()[0]
                    next_url = street_no_url.format(street=building_1['street_key'], district=building_1['district_key'],
                                                    estate=building_1['estate_key'],
                                                    building=building_1['building_key'].replace('&', '%26'),
                                                    sid=random.random())
                    yield scrapy.Request(next_url, callback=self.parse_street_no, meta={"building": building_1})

    def parse_street_no(self, response):
        building = response.meta["building"]
        options = response.xpath("//select/option")

        if len(options) == 1:
            building['street_no_key'] = ''
            building['street_no_name'] = ''
            next_url = check_building_url.format(zone=building['zone_key'],
                                                 district=building['district_key'],
                                                 estate_name=building['estate_key'],
                                                 street_name=building['street_key'],
                                                 streetNo=building['street_no_key'],
                                                 phase='',
                                                 sid=random.random())
            yield scrapy.Request(next_url, callback=self.check_building_street_no, meta={"building": building})
        else:
            for op in options:
                if len(op.xpath("@value").extract()[0]) > 0:
                    building_1 = utils.copy_value_from_item(building, Building)
                    building_1['street_no_key'] = op.xpath("@value").extract()[0]
                    building_1['street_no_name'] = op.xpath("text()").extract()[0]

                    next_url = check_building_url.format(zone=building_1['zone_key'],
                                                         district=building_1['district_key'],
                                                         estate_name=building_1['estate_key'],
                                                         street_name=building_1['street_key'],
                                                         streetNo=building_1['street_no_key'],
                                                         phase='',
                                                         sid=random.random())
                    yield scrapy.Request(next_url, callback=self.check_building_street_no, meta={'building': building_1})

    # 点要check？当spider fetch data至street_no & phase，可能改变building的值
    def check_building_street_no(self, response):
        building = response.meta["building"]
        options = response.xpath("//select/option")

        building_1 = utils.copy_value_from_item(building, Building)
        if building['building_name'] not in [op.xpath("text()").extract()[0].strip() for op in options]:
            return

        next_url = phase_url.format(estate=building['estate_key'],
                                    district=building['district_key'],
                                    street=building['street_key'],
                                    streetNo=building['street_no_key'],
                                    sid=random.random())
        yield scrapy.Request(next_url, callback=self.parse_phase, meta={"building": building_1})

    def parse_phase(self, response):
        building = response.meta["building"]
        options = response.xpath("//select/option")

        # building_key is unreliable,so check building data before save building
        if len(options) == 1:
            building_1 = utils.copy_value_from_item(building, Building)
            building_1['phase_key'] = ''
            building_1['phase_name'] = ''

            next_url = check_building_url.format(zone=building_1['zone_key'],
                                                 district=building_1['district_key'],
                                                 estate_name=building_1['estate_key'],
                                                 street_name=building_1['street_key'],
                                                 streetNo=building_1['street_no_key'],
                                                 phase=building_1['phase_key'].replace('&', '%26'),
                                                 sid=random.random())
            yield scrapy.Request(next_url, callback=self.check_building_phase, meta={"building": building_1})
        else:
            for op in options:
                if len(op.xpath("@value").extract()[0]) > 0:
                    building_1 = utils.copy_value_from_item(building, Building)
                    building_1['phase_key'] = op.xpath("@value").extract()[0]
                    building_1['phase_name'] = op.xpath("text()").extract()[0]

                    next_url = check_building_url.format(zone=building_1['zone_key'],
                                                         district=building_1['district_key'],
                                                         estate_name=building_1['estate_key'],
                                                         street_name=building_1['street_key'],
                                                         streetNo=building_1['street_no_key'],
                                                         phase=building_1['phase_key'].replace('&', '%26'),
                                                         sid=random.random())

                    yield scrapy.Request(next_url, callback=self.check_building_phase, meta={'building': building_1})

    def check_building_phase(self, response):
        building = response.meta["building"]
        options = response.xpath("//select/option")
        # query no building by phase param,save building without phase info:
        if len(building['estate_key']) > 0 and building['building_name'] not in [op.xpath("text()").extract()[0].strip() for op in options]:

            building_db = SpiderLogService.query_building(building['district_key'], building['street_key'],
                                                          building['street_no_key'], building['estate_key'],
                                                          building['building_key'], building['building_name'])

            # 如果數據庫已有數據，説明已insert過
            if building_db is None:
                building_5 = utils.copy_value_from_item(building, Building)
                building_5['phase_key'] = ''
                building_5['phase_name'] = ''

                building_5['building_name'] = building_5['building_name'].lstrip().rstrip()
                full_name_reverse, full_name = utils.get_building_full_name(building_5)
                building_5['full_name_reverse'] = full_name_reverse
                building_5['full_name'] = full_name
                yield building_5
                next_url = floor_url.format(district=building_5['district_key'],
                                            building=building_5['building_key'].replace('&', '%26'),
                                            street=building_5['street_key'],
                                            estate=building_5['estate_key'],
                                            phase=building_5['phase_key'].replace('&', '%26'),
                                            strno=building_5['street_no_key'],
                                            sid=random.random())
                yield scrapy.Request(next_url, callback=self.parse_floor, meta={"building": building_5})
        else:
            for op in options:
                if len(op.xpath("@value").extract()[0]) > 0:
                    if building['building_key'] == op.xpath("@value").extract()[0] and building['building_name'] == op.xpath("text()").extract()[0].strip():
                        building_db = SpiderLogService.query_building(building['district_key'], building['street_key'],
                                                                      building['street_no_key'], building['estate_key'],
                                                                      building['building_key'], building['building_name'])

                        if building_db is not None:
                            # 期數爲空，説明有符合期數條件的building，則更新
                            if building_db.phase_key == '' or len(building_db.phase_key) == 0:
                                building_db.phase_key = building['phase_key']
                                building_db.phase_name = building['phase_name']
                                full_name_reverse, full_name = utils.get_building_full_name(building)
                                building_db.full_name_reverse = full_name_reverse
                                building_db.full_name = full_name
                                building_db.save()

                                next_url = floor_url.format(district=building['district_key'],
                                                            building=building['building_key'].replace('&', '%26'),
                                                            street=building['street_key'],
                                                            estate=building['estate_key'],
                                                            phase=building['phase_key'].replace('&', '%26'),
                                                            strno=building['street_no_key'],
                                                            sid=random.random())
                                yield scrapy.Request(next_url, callback=self.parse_floor,
                                                     meta={"building": building})
                            elif building_db.phase_key == building['phase_key'] and building_db.phase_name == building['phase_name']:
                                return
                            else:
                                building_5 = utils.copy_value_from_item(building, Building)
                                building_5['building_name'] = building_5['building_name'].lstrip().rstrip()
                                full_name_reverse, full_name = utils.get_building_full_name(building_5)
                                building_5['full_name_reverse'] = full_name_reverse
                                building_5['full_name'] = full_name
                                yield building_5
                                next_url = floor_url.format(district=building_5['district_key'],
                                                            building=building_5['building_key'].replace('&', '%26'),
                                                            street=building_5['street_key'],
                                                            estate=building_5['estate_key'],
                                                            phase=building_5['phase_key'].replace('&', '%26'),
                                                            strno=building_5['street_no_key'],
                                                            sid=random.random())
                                yield scrapy.Request(next_url, callback=self.parse_floor, meta={"building": building_5})
                        else:
                            building_5 = utils.copy_value_from_item(building, Building)
                            building_5['building_name'] = building_5['building_name'].lstrip().rstrip()
                            full_name_reverse, full_name = utils.get_building_full_name(building_5)
                            building_5['full_name_reverse'] = full_name_reverse
                            building_5['full_name'] = full_name
                            yield building_5
                            next_url = floor_url.format(district=building_5['district_key'],
                                                        building=building_5['building_key'].replace('&', '%26'),
                                                        street=building_5['street_key'],
                                                        estate=building_5['estate_key'],
                                                        phase=building_5['phase_key'].replace('&', '%26'),
                                                        strno=building_5['street_no_key'],
                                                        sid=random.random())
                            yield scrapy.Request(next_url, callback=self.parse_floor, meta={"building": building_5})

    def parse_floor(self, response):
        building = response.meta["building"]
        options = response.xpath("//select/option")
        if len(options) == 1:
            # no floors but has units,eg:香港 深水灣 深水灣道 6   ROCKY BANK  6號
            floor = utils.copy_value_from_item(building, Floor)
            floor['floor_key'] = ''
            floor['floor_name'] = ''
            next_url = unit_url.format(district=floor['district_key'],
                                       building=floor['building_key'].replace('&', '%26'),
                                       strno=floor['street_no_key'],
                                       street=floor['street_key'],
                                       estate=floor['estate_key'],
                                       phase=floor['phase_key'].replace('&', '%26'),
                                       floor=floor['floor_key'].replace('&', '%26'),
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
                                               building=floor['building_key'].replace('&', '%26'),
                                               strno=floor['street_no_key'],
                                               street=floor['street_key'],
                                               estate=floor['estate_key'],
                                               phase=floor['phase_key'].replace('&', '%26'),
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
            unit['unit_key'] = ''
            unit['unit_name'] = ''
            if len(floor['floor_key']) > 0:
                street_no_name = unit['street_no_name']
                unit['full_name_ch'] = utils.get_full_name_ch(keys, unit)
                unit['full_name_en'] = utils.get_full_name_en(keys, unit)
                unit['street_no_name'] = street_no_name
                yield unit
