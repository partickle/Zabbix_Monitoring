# Класс логики работы с группами Пользователей
class Usrgrps:
    def __init__(self, zabbix):
        # При его инициализации посылается запрос к api zabbix
        # И информация сохраняется в поле класса
        self.zabbix = zabbix
        # Получаем группы всех пользователей
        self.usrgrps = zabbix.usergroup.get(
            output=['usrgrpid', 'name']
        )
        # Словарь соответствия выбранного имени группы и
        # текста команды для Zabbix API (id группы)
        self.ids_of_usrgrps = {
            usrgrp['name']: usrgrp['usrgrpid']
            for usrgrp in self.usrgrps
        }

    # Метод обращается к полю класса с информацией и
    # возвращает все группы пользователей
    def get_usrgrps(self):
        return self.usrgrps
