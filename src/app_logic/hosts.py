# Класс логики работы с хостами
class Hosts:
    def __init__(self, zabbix):
        # При его инициализации посылается запрос к api zabbix
        # И информация сохраняется в поле класса
        self.zabbix = zabbix
        self.hosts_info = zabbix.host.get(output=['hostid', 'name', 'host'])

        # Информация сервера, используется в настройке.
        # Именно это убирает универсальность приложения.
        # В будущем нужно бы доработать (уже не убирает универсальность)
        # Эта информация теперь универсальна для
        # создания хостов в плане сервера,
        # однако все еще нужно добавить группы хостов вкладку в приложение,
        # а также ролей, групп пользователей
        # hostgroups = zabbix.hostgroup.get(output=['groupid', 'name'])
        # print(hostgroups)
        # roles = zabbix.role.get(output=['roleid', 'name'])
        # print(roles)
        # usergroups = zabbix.usergroup.get(output=['usrgrpid', 'name'])
        # print(usergroups)

    # Метод возвращает список всех хостов, кроме серверного
    def get_hosts(self):
        hosts_to_show = []
        for host in self.hosts_info:
            if host['host'] != 'Zabbix server':
                hosts_to_show.append(host)
        return hosts_to_show

    # Метод добавляет хост с указанными параметрами
    def add_host(self, host_name, host_ip, groupids):
        groups = [{"groupid": id} for id in groupids]
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
            groups=groups
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

    def get_hostid_by_name(self, name):
        for host in self.hosts_info:
            if host['name'] == name:
                return host['hostid']
        return 'Не найден'
