# Класс логики работы с триггерами
class Triggers:
    def __init__(self, zabbix):
        # При его инициализации посылается запрос к api zabbix
        # И информация сохраняется в поле класса
        self.zabbix = zabbix
        # Делаем запрос на хосты
        # self.hosts_info = zabbix.host.get(output=['hostid', 'name', 'host'])
        # Получаем чистый список всех hostid
        # self.hosts = [host['hostid'] for host in self.hosts_info]
        # Получаем все триггеры, связанные со всеми хостами
        # (для получения в ответе у каждого триггера id его хоста используется
        # параметр selectHosts)
        self.triggers = zabbix.trigger.get(
            output=['triggerid', 'description', 'expression'],
            selectHosts=['host', 'hostid'],
            expandExpression=True
        )
        # Словарь соответствия выбранного текста приоритета и
        # текста команды для Zabbix API
        self.priorities_of_triggers = {
            "Без класса": "0",
            "Информация": "1",
            "Предупреждение": "2",
            "Средней важности": "3",
            "Высокой важности": "4",
            "Происшествие": "5",
        }

    # Метод обращается к полю класса с информацией и
    # возвращает только те триггеры, которые принадлежат
    # заданному хосту
    def get_triggers(self, host):
        triggers_of_host = []
        for trigger in self.triggers:
            if trigger['hosts'][0]['hostid'] == host['hostid']:
                trigger_of_host = {
                    'triggerid': trigger['triggerid'],
                    'description': trigger['description'],
                    'expression': trigger['expression'],
                    'hosts': trigger['hosts']
                }
                triggers_of_host.append(trigger_of_host)
        return triggers_of_host

    # Метод добавляет триггер с указанными параметрами
    def add_trigger(self, description, expression, priority):
        self.zabbix.trigger.create(
            description=description,
            expression=expression,
            priority=priority
        )

    # Метод отправляет запрос на удаление триггеров,
    # указанных в словаре как true, по ключу triggerid
    def delete_triggers(self, triggerids_maybe_checked):
        triggerids_to_delete = []
        # Проходим по всем ключам словаря
        for triggerid in triggerids_maybe_checked:
            # Проверяем состояние triggerid
            if triggerids_maybe_checked[triggerid]:
                triggerids_to_delete.append(triggerid)
        # * нужно, чтобы распаковать список как множество аргументов
        self.zabbix.trigger.delete(*triggerids_to_delete)
