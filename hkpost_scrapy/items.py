# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy_djangoitem import DjangoItem
from save_app.models import *


class SpiderLog(DjangoItem):
    django_model = SpiderLog


class Zone(DjangoItem):
    django_model = Zone


class District(DjangoItem):
    django_model = District


class Street(DjangoItem):
    django_model = Street


class StreetNo(DjangoItem):
    django_model = StreetNo


class Estate(DjangoItem):
    django_model = Estate


class Phase(DjangoItem):
    django_model = Phase


class Building(DjangoItem):
    django_model = Building


class Floor(DjangoItem):
    django_model = Floor


class Unit(DjangoItem):
    django_model = Unit


class ErrorLog(DjangoItem):
    django_model = ErrorLog
