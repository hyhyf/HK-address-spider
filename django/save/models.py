from django.db import models


class SpiderLog(models.Model):
    id = models.IntegerField(max_length=10, primary_key=True)
    spider_name = models.CharField(max_length=255)
    start_time = models.DateTimeField(auto_now=False)
    end_time = models.DateTimeField(auto_now=False)
    status = models.CharField(max_length=255)
    spider_param = models.CharField(max_length=255)

    class Meta:
        db_table = "addr_spider_log"


# Create your models here.
class Zone(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    ts = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "addr_zones"


class District(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    zone_key = models.CharField(max_length=255)
    zone_name = models.CharField(max_length=255)
    district_key = models.CharField(max_length=255)
    district_name = models.CharField(max_length=255)
    ts = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "addr_districts"


class Street(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    zone_key = models.CharField(max_length=255)
    zone_name = models.CharField(max_length=255)
    district_key = models.CharField(max_length=255)
    district_name = models.CharField(max_length=255)
    street_key = models.CharField(max_length=255)
    street_name = models.CharField(max_length=255)
    ts = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "addr_streets"


class StreetNo(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    zone_key = models.CharField(max_length=255)
    zone_name = models.CharField(max_length=255)
    district_key = models.CharField(max_length=255)
    district_name = models.CharField(max_length=255)
    street_key = models.CharField(max_length=255)
    street_name = models.CharField(max_length=255)
    street_no_key = models.CharField(max_length=255)
    street_no_name = models.CharField(max_length=255)
    ts = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "addr_streets_no"


class Estate(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    zone_key = models.CharField(max_length=255)
    zone_name = models.CharField(max_length=255)
    district_key = models.CharField(max_length=255)
    district_name = models.CharField(max_length=255)
    street_key = models.CharField(max_length=255)
    street_name = models.CharField(max_length=255)
    street_no_key = models.CharField(max_length=255)
    street_no_name = models.CharField(max_length=255)
    estate_key = models.CharField(max_length=255)
    estate_name = models.CharField(max_length=255)
    ts = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "addr_estates"


class Phase(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    zone_key = models.CharField(max_length=255)
    zone_name = models.CharField(max_length=255)
    district_key = models.CharField(max_length=255)
    district_name = models.CharField(max_length=255)
    street_key = models.CharField(max_length=255)
    street_name = models.CharField(max_length=255)
    street_no_key = models.CharField(max_length=255)
    street_no_name = models.CharField(max_length=255)
    estate_key = models.CharField(max_length=255)
    estate_name = models.CharField(max_length=255)
    phase_key = models.CharField(max_length=255)
    phase_name = models.CharField(max_length=255)
    ts = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "addr_phases"


class Building(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    zone_key = models.CharField(max_length=255)
    zone_name = models.CharField(max_length=255)
    district_key = models.CharField(max_length=255)
    district_name = models.CharField(max_length=255)
    street_key = models.CharField(max_length=255)
    street_name = models.CharField(max_length=255)
    street_no_key = models.CharField(max_length=255)
    street_no_name = models.CharField(max_length=255)
    estate_key = models.CharField(max_length=255)
    estate_name = models.CharField(max_length=255)
    phase_key = models.CharField(max_length=255)
    phase_name = models.CharField(max_length=255)
    building_key = models.CharField(max_length=255)
    building_name = models.CharField(max_length=255)
    latitude = models.CharField(max_length=50)
    longitude = models.CharField(max_length=50)
    full_name = models.CharField(max_length=255)
    full_name_reverse = models.CharField(max_length=255)
    ts = models.DateTimeField(auto_now=True)
    data_source = models.CharField(max_length=50)
    class Meta:
        db_table = "addr_buildings"


class Floor(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    zone_key = models.CharField(max_length=255)
    zone_name = models.CharField(max_length=255)
    district_key = models.CharField(max_length=255)
    district_name = models.CharField(max_length=255)
    street_key = models.CharField(max_length=255)
    street_name = models.CharField(max_length=255)
    street_no_key = models.CharField(max_length=255)
    street_no_name = models.CharField(max_length=255)
    estate_key = models.CharField(max_length=255)
    estate_name = models.CharField(max_length=255)
    phase_key = models.CharField(max_length=255)
    phase_name = models.CharField(max_length=255)
    building_key = models.CharField(max_length=255)
    building_name = models.CharField(max_length=255)
    floor_key = models.CharField(max_length=255)
    floor_name = models.CharField(max_length=255)
    ts = models.DateTimeField(auto_now=True)
    data_source = models.CharField(max_length=50)
    class Meta:
        db_table = "addr_floors"


class Unit(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    zone_key = models.CharField(max_length=255)
    zone_name = models.CharField(max_length=255)
    district_key = models.CharField(max_length=255)
    district_name = models.CharField(max_length=255)
    street_key = models.CharField(max_length=255)
    street_name = models.CharField(max_length=255)
    street_no_key = models.CharField(max_length=255)
    street_no_name = models.CharField(max_length=255)
    estate_key = models.CharField(max_length=255)
    estate_name = models.CharField(max_length=255)
    phase_key = models.CharField(max_length=255)
    phase_name = models.CharField(max_length=255)
    building_key = models.CharField(max_length=255)
    building_name = models.CharField(max_length=255)
    floor_key = models.CharField(max_length=255)
    floor_name = models.CharField(max_length=255)
    unit_key = models.CharField(max_length=255)
    unit_name = models.CharField(max_length=255)
    full_name_en = models.CharField(max_length=255)
    full_name_ch = models.CharField(max_length=255)
    ts = models.DateTimeField(auto_now=True)
    los_building_name = models.CharField(max_length=255)
    data_source = models.CharField(max_length=50)

    class Meta:
        db_table = "addr_units"


class ErrorLog(models.Model):
    id = models.IntegerField(max_length=10, primary_key=True)
    spider_name = models.CharField(max_length=255)
    error_time = models.DateTimeField(auto_now=True)
    http_status = models.CharField(max_length=255)
    district_key = models.CharField(max_length=255)
    request_url = models.CharField(max_length=255)
    error_msg = models.CharField(max_length=255)

    class Meta:
        db_table = "error_log"
