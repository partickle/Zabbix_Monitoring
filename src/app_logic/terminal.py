# Пример отличного рефакторинга -
# https://github.com/guilatrova/GMaps-Crawler/blob/main/src/gmaps_crawler/facades.py

from pyzabbix import ZabbixAPI
import requests

zabbi = ZabbixAPI("http://25.71.15.72")
zabbi.login("Admin", "zabbix")


class Terminal:
    @staticmethod
    def log_request(zabbix):
        req = requests.get(zabbix.url[:-15] + 'conf/zabbix.conf.php.example')
        print(req.content)


Terminal.connect_to_zabbix(zabbi)
