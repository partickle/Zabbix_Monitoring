# Класс логики работы с хостами
class Hosts:
    def __init__(self, zabbix):
        # При его инициализации посылается запрос к api zabbix
        # И информация сохраняется в поле класса
        self.zabbix = zabbix
        self.hosts_info = zabbix.host.get(output=['hostid', 'name', 'host'])

    # Метод возвращает список всех хостов, кроме серверного
    def get_hosts(self):
        hosts_to_show = []
        for host in self.hosts_info:
            if host['host'] != 'Zabbix server':
                hosts_to_show.append(host)
        return hosts_to_show
