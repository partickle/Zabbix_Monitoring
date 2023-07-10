# Класс логики работы с ролями пользователей
class Roles:
    def __init__(self, zabbix):
        # При его инициализации посылается запрос к api zabbix
        # И информация сохраняется в поле класса
        self.zabbix = zabbix
        # Получаем все роли пользователей
        self.roles = zabbix.role.get(
            output=['roleid', 'name']
        )
        # Словарь соответствия выбранного имени роли и
        # текста команды для Zabbix API (id роли)
        self.ids_of_roles = {
            role['name']: role['roleid']
            for role in self.roles
        }

    # Метод обращается к полю класса с информацией и
    # возвращает все роли пользователей
    def get_roles(self):
        return self.roles
