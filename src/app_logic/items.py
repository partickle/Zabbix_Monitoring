# Класс логики работы с элементами данных
class Items:
    def __init__(self, zabbix):
        # При его инициализации посылается запрос к api zabbix
        # И информация сохраняется в поле класса
        self.zabbix = zabbix
        # Делаем запрос на хосты
        self.hosts_info = zabbix.host.get(output=['hostid', 'name', 'host'])
        # Получаем чистый список всех hostid
        self.hosts = [host['hostid'] for host in self.hosts_info]
        # Получаем все элементы данных связанные со всеми хостами
        self.items = zabbix.item.get(
            hostids=self.hosts,
            output=['itemid', 'name', 'key_', 'hostid']
        )

    # Метод обращается к полю класса с информацией и
    # возвращает только те элементы данных, которые принадлежат
    # заданному хосту
    def get_items(self, host):
        items_of_host = []
        for item in self.items:
            if item['hostid'] == host['hostid']:
                item_of_host = {}
                item_of_host['itemid'] = item['itemid']
                item_of_host['name'] = item['name']
                item_of_host['key_'] = item['key_']
                item_of_host['hostid'] = item['hostid']
                items_of_host.append(item_of_host)
        return items_of_host
