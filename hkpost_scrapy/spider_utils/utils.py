import json
import os
import random
import re

class Utils:
    cache_zones = []

    def load_zones(self):
        file_path = os.path.dirname(__file__)
        json_file = os.path.join(file_path, 'zones_all.json')
        with open(json_file, encoding="utf8") as f:
            self.cache_zones = json.load(f)
        return self.cache_zones

    def get_zone_name(self, zone_key):
        zone_name = ''
        if self.cache_zones and len(self.cache_zones) > 0:
            for zone in self.cache_zones:
                if zone["id"] == zone_key:
                    zone_name = zone["name"]
        return zone_name

    def init_start_district_Urls(self):
        district_urls = []
        base_district_url = 'https://www1.hongkongpost.hk/correct_addressing/GetDistrict.jsp?' \
                            'zone_value={zone_value}&lang=&lang1=en_US&sid={sid}'
        zones = self.load_zones()
        for zone in zones:
            district_urls.append(base_district_url.format(zone_value=zone["id"], sid=random.random()))
        return district_urls

    @staticmethod
    def remove_ch_chars(str):
        result = re.sub(u"[\u4e00-\u9fa5\(\)]+", "", str)
        result = result.replace(" ", "")
        return result

    @staticmethod
    def get_ch_chars(str):
        result = re.sub("[A-Za-z0-9'\!\%\[\]\(\)]", "", str)
        return result.strip()

    def generate_id(self, model):
        filed_values = self.model_filed_values(model)
        id = "+".join(filed_values)
        # for f in filed_dict.keys():
        #     id = id + "+" + model[f] + "+"
        id = Utils.remove_ch_chars(id).replace("\n", "")
        if 'building_name' in model.fields.keys():
            id = id + model['building_name']
        id = id.replace(' ', '')
        if len(id) > 150:
            id = id[-149:]
        return id

    def copy_value_from_item(self, model_obj, modlecls):
        dest = modlecls()
        keys = model_obj.fields.keys()
        for field in keys:
            if field == "id" or field == "ts":
                continue
            else:
                if field in model_obj and field in modlecls.fields.keys():
                    dest[field] = model_obj[field]
        return dest

    def model_filed_values(self, model_obj, ignore=()):
        '''
        将一个model对象转换成字典
        '''
        filed_values = []
        # att_dict = {}
        keys = model_obj.fields.keys()
        for field in keys:
            if field == "id" or field == "ts" or field == "full_name" or field == "full_name_reverse" or field == "data_source":
                continue
            else:
                # att_dict[field] = model_obj[field]  # 生成字典
                if field in model_obj:
                    filed_values.append(model_obj[field])
        return filed_values

    def get_building_full_name(self, building):
        full_name_reverse = building['zone_name']+', ' + building['district_name'] + ', ' \
                            + building['street_name'] + ', ' + building['street_no_name'] + ', ' \
                            + building['estate_name'] + ', ' + building['phase_name'] + ', '\
                            + building['building_name']

        full_name = building['building_name'] + ', ' + building['phase_name'] + ', ' \
            + building['estate_name'] + ', ' + building['street_no_name'] + ', ' \
            + building['street_name'] + ', ' + building['district_name'] + ', ' \
            + building['zone_name']
        return full_name_reverse, full_name

    @staticmethod
    def get_full_name_ch(keys, item):
        full_name_ch = ''
        for field in keys:
            if 'name' in field:
                if 'full_name' in field:
                    continue
                if field in item:
                    if 'street_no_name' == field and "號" not in item['street_no_name']:
                        item['street_no_name'] = item['street_no_name'] + "號"
                    pat = re.compile(r'[(](.*?)[)]', re.S)  # 最小匹配
                    ch_name = re.findall(pat, item[field])
                    if ch_name is None or len(ch_name) == 0:
                        full_name_ch += str(item[field])
                    else:
                        # ch_name is from the last string in "()"
                        full_name_ch += ch_name[-1]
        return full_name_ch.strip()

    @staticmethod
    def get_full_name_en(keys, item):
        full_name_en = ''
        for field in keys:
            if 'name' in field:
                if 'full_name' in field:
                    continue
                if field in item:
                    if 'street_no_name' == field and "NO." not in item['street_no_name']:
                        item['street_no_name'] = "NO."+item['street_no_name'].replace('號','')
                    # result_local = str(item[field].split("(")[0]).lstrip().rstrip()
                    result_local = item[field].replace(str(item[field].split("(")[-1]), '')[:-1]
                    if result_local:
                        full_name_en += ","+ result_local
                    else:
                        full_name_en += ","+item[field]
        return full_name_en[1:].replace(",,,", ",").replace(",,",",")


if __name__ == '__main__':
    utils = Utils()
    # data = uitl.init_start_district_Urls()
    #
    # print(data)
    # str1 = "KING'S ROAD  (英皇道)"
    # result = Utils.get_ch_chars(str1)
    # print(result)
    unit ={}
    unit['zone_name'] ='HONG KONG (香港)'
    unit['district_name'] = 'AP LEI CHAU  (鴨脷洲)'
    unit['street_key'] = "LEE NAM ROAD"
    unit['street_name'] = "LEE NAM ROAD  (利南道)"
    unit['street_no_key'] = "111"
    unit['street_no_name'] = "111"
    unit['estate_name'] = ''
    unit['phase_name'] = ''

    unit['building_key'] = 'nullhihinullhihiDAH CHONG HONG (MOTOR SERVICE CTR) AP LEI CHAU SERVICE CTR'
    unit['building_name'] = "DAH CHONG HONG (MOTOR SERVICE CTR) AP LEI CHAU SERVICE CTR  (大昌貿易行汽車服務中心有限公司鴨脷洲服務中心)".lstrip().rstrip()
    full_name_reverse, full_name = utils.get_building_full_name(unit)
    unit['full_name_reverse'] = full_name_reverse
    unit['full_name'] = full_name

    keys = ['zone_name','district_name','street_name','street_no_name','estate_name','phase_name','building_name']
    unit['full_name_ch'] = utils.get_full_name_ch(keys, unit)
    unit['full_name_en'] = utils.get_full_name_en(keys, unit)
    print('full_name_ch = ' , unit['full_name_ch'])
    print('full_name_en = ' , unit['full_name_en'])

    result = re.search(r"(?<=\()[^\(\)]*(?=\))",  unit['building_name'])

    p1 = re.compile(r'[(](.*?)[)]', re.S)  # 最小匹配
    # p2 = re.compile(r'[(](.*)[)]', re.S)  # 贪婪匹配
    print("findall --->", re.findall(p1,  unit['building_name']))
    # print(re.findall(p2,  unit['building_name']))

    if result is not None:
        match_result =  result.group()
        print('match_result = ',match_result)
