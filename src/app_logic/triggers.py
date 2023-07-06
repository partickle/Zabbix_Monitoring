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
                trigger_of_host = {
                    'triggerid': trigger['triggerid'],
                    'description': trigger['description'],
                    'expression': trigger['expression'],
                    'hosts': trigger['hosts']
                }
                triggers_of_host.append(trigger_of_host)
        return triggers_of_host

    # Метод добавляет хост с указанными параметрами
    def add_host(self, host_name, host_ip):
        self.zabbix.host.create(
            host=host_name,
            interfaces={
                "type": 1,
                "main": 1,
                "useip": 1,
                "ip": host_ip,
                "dns": "",
                "port": "10050"
            },
            groups={"groupid": "23"}
        )

    # Метод отправляет запрос на удаление хостов,
    # указанных в словаре как true, по ключу hostid
    def delete_hosts(self, hostids_maybe_checked):
        hostids_to_delete = []
        # Проходим по всем ключам словаря
        for hostid in hostids_maybe_checked:
            # Проверяем состояние hostid
            if hostids_maybe_checked[hostid]:
                hostids_to_delete.append(hostid)
        # * нужно, чтобы распаковать список как множество аргументов
        self.zabbix.host.delete(*hostids_to_delete)
