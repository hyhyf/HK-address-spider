import django
from django.db.models.functions import Coalesce

from save_app.models import *


class SpiderLogService:

    @staticmethod
    def query_district(district_key):
        try:
            return District.objects.get(district_key=district_key)
        except District.DoesNotExist:
            print("district_key:%s not exist !" % district_key)
            return None

    @staticmethod
    def get_all_district():
        try:
            return District.objects.all()
        except District.DoesNotExist:
            return None

    @staticmethod
    def query_building(district_key, street_key, street_no_key, estate_key, building_key, building_name):
        try:
            return Building.objects.get(district_key=district_key, street_key=street_key,
                                        street_no_key=street_no_key, estate_key=estate_key,
                                        building_key=building_key, building_name=building_name)
        except Building.DoesNotExist:
            return None
        except Building.MultipleObjectsReturned:
            return Building.objects.filter(district_key=district_key, street_key=street_key,
                                           street_no_key=street_no_key, estate_key=estate_key,
                                           building_key=building_key, building_name=building_name).first()

    @staticmethod
    def query_building_by_id(building_id):
        try:
            return Building.objects.get(id=building_id)
        except Building.DoesNotExist:
            return None

    @staticmethod
    def is_spider_finished(spider_name, district=None):
        # finished = False
        try:
            if district:
                end_spider_log = SpiderLog.objects.get(spider_name=spider_name, spider_param=district, status='END')
            else:
                end_spider_log = SpiderLog.objects.get(spider_name=spider_name, status='END')
        except SpiderLog.DoesNotExist:
            return False
        except SpiderLog.MultipleObjectsReturned:
            return True
        else:
            return True

    @staticmethod
    def save_spider_log(spider_name, start_time, param, status):
        spider_log = SpiderLog()
        spider_log.spider_name = spider_name
        # spider_log.start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
        spider_log.start_time = start_time
        if status == 'END':
            spider_log.end_time = django.utils.timezone.now()
        spider_log.status = status
        spider_log.spider_param = param
        spider_log.save()

    @staticmethod
    def save_error_log(spider_name, http_status, district_key, request_url, error_msg):
        error_log = ErrorLog()
        error_log.spider_name = spider_name
        error_log.http_status = http_status
        error_log.district_key = district_key
        error_log.request_url = request_url
        error_log.error_msg = error_msg
        error_log.save()
