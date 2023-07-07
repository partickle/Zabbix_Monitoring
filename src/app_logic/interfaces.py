# Класс логики работы с интерфейсами хостов
class Interfaces:
    def __init__(self, zabbix):
        # При его инициализации посылается запрос к api zabbix
        # И информация сохраняется в поле класса
        self.zabbix = zabbix
        # Делаем запрос на хосты
        self.hosts_info = zabbix.host.get(output=['hostid', 'name', 'host'])
        # Получаем чистый список всех hostid
        self.hosts = [host['hostid'] for host in self.hosts_info]
        # Получаем интерфейсы всех хостов
        self.interfaces = zabbix.hostinterface.get(
            hostids=self.hosts,
            output=['hostid', 'interfaceid']
        )

    # Метод обращается к полю класса с информацией и
    # возвращает только те интерфейсы, которые принадлежат
    # заданному хосту
    def get_interfaces(self, host):
        interfaces_of_host = []
        for interface in self.interfaces:
            if interface['hostid'] == host['hostid']:
                interface_of_host = {
                    'hostid': interface['hostid'],
                    'interfaceid': interface['interfaceid']
                }
                interfaces_of_host.append(interface_of_host)
        return interface_of_host
