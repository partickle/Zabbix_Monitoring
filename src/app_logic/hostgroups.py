# Класс логики работы с группами хостов
class Hostgroups:
    def __init__(self, zabbix):
        # При его инициализации посылается запрос к api zabbix
        # И информация сохраняется в поле класса
        self.zabbix = zabbix
        # Получаем группы всех хостов
        self.hostgroups = zabbix.hostgroup.get(
            output=['groupid', 'name']
        )
        # Словарь соответствия выбранного имени группы и
        # текста команды для Zabbix API (id группы)
        # ids_of_hostgroups = {}
        # for hostgroup in self.hostgroups:
        #     ids_of_hostgroups[hostgroup['name']] = hostgroup['groupid']
        self.ids_of_hostgroups = {
            hostgroup['name']: hostgroup['groupid']
            for hostgroup in self.hostgroups
        }

    # Метод обращается к полю класса с информацией и
    # возвращает все группы хостов
    def get_hostgroups(self):
        return self.hostgroups
