create table addr_spider_log (id int(10) AUTO_INCREMENT PRIMARY KEY, spider_name varchar(50),start_time datetime ,end_time datetime, status VARCHAR(20),spider_param varchar(10))  DEFAULT CHARSET=utf8;

create table addr_zones (id VARCHAR(10) PRIMARY KEY, name VARCHAR(50), ts datetime DEFAULT CURRENT_TIMESTAMP)  DEFAULT CHARSET=utf8;

create table addr_districts (id VARCHAR(200) PRIMARY KEY, zone_key VARCHAR(50), zone_name VARCHAR(50), district_key VARCHAR(50), district_name VARCHAR(50), ts datetime DEFAULT CURRENT_TIMESTAMP)  DEFAULT CHARSET=utf8;

create table addr_streets (id VARCHAR(200) PRIMARY KEY, zone_key VARCHAR(50), zone_name VARCHAR(50), district_key VARCHAR(50), district_name VARCHAR(50), street_key VARCHAR(50), street_name VARCHAR(50), ts datetime DEFAULT CURRENT_TIMESTAMP)  DEFAULT CHARSET=utf8;

create table addr_streets_no (id VARCHAR(200) PRIMARY KEY, zone_key VARCHAR(50), zone_name VARCHAR(50), district_key VARCHAR(50), district_name VARCHAR(50), street_key VARCHAR(50), street_name VARCHAR(50), street_no_key VARCHAR(50), street_no_name VARCHAR(50), ts datetime DEFAULT CURRENT_TIMESTAMP)  DEFAULT CHARSET=utf8;

create table addr_estates (id VARCHAR(200) PRIMARY KEY, zone_key VARCHAR(50), zone_name VARCHAR(50), district_key VARCHAR(50), district_name VARCHAR(50), street_key VARCHAR(50), street_name VARCHAR(50), street_no_key VARCHAR(50), street_no_name VARCHAR(50), estate_key VARCHAR(200), estate_name VARCHAR(400), ts datetime DEFAULT CURRENT_TIMESTAMP)  DEFAULT CHARSET=utf8;

create table addr_phases (id VARCHAR(200) PRIMARY KEY, zone_key VARCHAR(50), zone_name VARCHAR(50), district_key VARCHAR(50), district_name VARCHAR(50), street_key VARCHAR(50), street_name VARCHAR(50), street_no_key VARCHAR(50), street_no_name VARCHAR(50), estate_key VARCHAR(200), estate_name VARCHAR(400), phase_key VARCHAR(50), phase_name VARCHAR(50), ts datetime DEFAULT CURRENT_TIMESTAMP)  DEFAULT CHARSET=utf8;

create table addr_buildings (id VARCHAR(400) PRIMARY KEY, zone_key VARCHAR(50), zone_name VARCHAR(50), district_key VARCHAR(50), district_name VARCHAR(50), street_key VARCHAR(50), street_name VARCHAR(50), street_no_key VARCHAR(50), street_no_name VARCHAR(50), estate_key VARCHAR(200), estate_name VARCHAR(400), phase_key VARCHAR(50), phase_name VARCHAR(50), building_key VARCHAR(200), building_name VARCHAR(200), ts datetime DEFAULT CURRENT_TIMESTAMP, latitude VARCHAR(20), longitude VARCHAR(20), full_name VARCHAR(300), full_name_reverse VARCHAR(300))  DEFAULT CHARSET=utf8;


create table addr_floors (id VARCHAR(400) PRIMARY KEY, zone_key VARCHAR(50), zone_name VARCHAR(50), district_key VARCHAR(50), district_name VARCHAR(50), street_key VARCHAR(50), street_name VARCHAR(50), street_no_key VARCHAR(50), street_no_name VARCHAR(50), estate_key VARCHAR(200), estate_name VARCHAR(400), phase_key VARCHAR(50), phase_name VARCHAR(50), building_key VARCHAR(100), building_name VARCHAR(100), floor_key VARCHAR(100), floor_name VARCHAR(50), ts datetime DEFAULT CURRENT_TIMESTAMP)  DEFAULT CHARSET=utf8;


create table addr_units (id VARCHAR(400) PRIMARY KEY, zone_key VARCHAR(50), zone_name VARCHAR(50), district_key VARCHAR(50), district_name VARCHAR(50), street_key VARCHAR(50), street_name VARCHAR(50), street_no_key VARCHAR(50), street_no_name VARCHAR(50), estate_key VARCHAR(200), estate_name VARCHAR(200), phase_key VARCHAR(50), phase_name VARCHAR(50), building_key VARCHAR(200), building_name VARCHAR(200), floor_key VARCHAR(100), floor_name VARCHAR(50), unit_key VARCHAR(200), unit_name VARCHAR(50), full_name_en VARCHAR(300), full_name_ch VARCHAR(300), ts datetime DEFAULT CURRENT_TIMESTAMP, los_building_name VARCHAR(300))  DEFAULT CHARSET=utf8;

create table error_log (id int(10) AUTO_INCREMENT PRIMARY KEY, spider_name varchar(50), http_status varchar(5),error_time datetime, district_key varchar(50), request_url VARCHAR(400), error_msg varchar(200))  DEFAULT CHARSET=utf8;
