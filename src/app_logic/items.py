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
        # Словарь соответствия выбранного текста типа элемента данных и
        # текста команды для Zabbix API
        self.types_of_items = {
            "Zabbix agent": "0", "Zabbix trapper": "2",
            "Simple check": "3", "Zabbix internal": "5",
            "Zabbix agent (active)": "7", "Web item": "9",
            "External check": "10", "Database monitor": "11",
            "IPMI agent": "12", "SSH agent": "13",
            "TELNET agent": "14", "Calculated": "15",
            "JMX agent": "16", "SNMP trap": "17",
            "Dependent item": "18", "HTTP agent": "19",
            "SNMP agent": "20", "Script": "21"
        }
        # Словарь соответствия выбранного текста типа возвращаемого значения и
        # текста команды для Zabbix API
        self.value_types_of_items = {
            "Число с плавающей точкой": "0",
            "Символ": "1",
            "Лог": "2",
            "Число без знака": "3",
            "Текст": "4"
        }

    # Метод обращается к полю класса с информацией и
    # возвращает только те элементы данных, которые принадлежат
    # заданному хосту
    def get_items(self, host):
        items_of_host = []
        for item in self.items:
            if item['hostid'] == host['hostid']:
                item_of_host = {
                    'itemid': item['itemid'],
                    'name': item['name'],
                    'key_': item['key_'],
                    'hostid': item['hostid']
                }
                items_of_host.append(item_of_host)
        return items_of_host

    # Метод добавляет элемент данных с указанными параметрами
    def add_item(self, hostid, interfaceid, item_name,
                 key, type, value_type, delay_in_s):
        self.zabbix.item.create(
            hostid=hostid,
            interfaceid=interfaceid,
            name=item_name,
            key_=key,
            type=type,
            value_type=value_type,
            delay=delay_in_s
        )

    # Метод отправляет запрос на удаление элементов данных,
    # указанных в словаре как true, по ключу itemid
    def delete_items(self, itemids_maybe_checked):
        itemids_to_delete = []
        # Проходим по всем ключам словаря
        for itemid in itemids_maybe_checked:
            # Проверяем состояние itemid
            if itemids_maybe_checked[itemid]:
                itemids_to_delete.append(itemid)
        # * нужно, чтобы распаковать список как множество аргументов
        self.zabbix.item.delete(*itemids_to_delete)
