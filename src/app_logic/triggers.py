# Класс логики работы с триггерами
class Triggers:
    def __init__(self, zabbix):
        # При его инициализации посылается запрос к api zabbix
        # И информация сохраняется в поле класса
        self.zabbix = zabbix
        # Делаем запрос на хосты
        self.hosts_info = zabbix.host.get(output=['hostid', 'name', 'host'])
        # Получаем чистый список всех hostid
        self.hosts = [host['hostid'] for host in self.hosts_info]
        # Получаем все триггеры, связанные со всеми хостами
        # (для получения в ответе у каждого триггера id его хоста используется
        # параметр selectHosts)
        self.triggers = zabbix.trigger.get(
            hostids=self.hosts,
            output=['triggerid', 'description', 'expression'],
            selectHosts=['host', 'hostid']
        )

    # Метод обращается к полю класса с информацией и
    # возвращает только те триггеры, которые принадлежат
    # заданному хосту
    def get_triggers(self, host):
        triggers_of_host = []
        for trigger in self.triggers:
            if trigger['hosts'][0]['hostid'] == host['hostid']:
                trigger_of_host = {}
                trigger_of_host['triggerid'] = trigger['triggerid']
                trigger_of_host['description'] = trigger['description']
                trigger_of_host['expression'] = trigger['expression']
                trigger_of_host['hosts'] = trigger['hosts']
                triggers_of_host.append(trigger_of_host)
        return triggers_of_host
