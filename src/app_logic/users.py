# Класс логики работы с пользователями
class Users:
    def __init__(self, zabbix):
        # При его инициализации посылается запрос к api zabbix
        # И информация сохраняется в поле класса
        self.zabbix = zabbix
        self.users = zabbix.user.get(
            output=['username', 'userid', 'roleid', 'name', 'surname']
        )

    # Метод возвращает список всех пользователей
    def get_users(self):
        return self.users

    # Метод добавляет пользователя с указанными параметрами
    def add_user(self, username, password,
                 role_id, name, surname):
        self.zabbix.user.create(
            username=username,
            passwd=password,
            roleid=role_id,  # Доработать
            name=name,
            surname=surname,
            usrgrps=[{"usrgrpid": "17"}]  # Доработать
        )

    # Метод отправляет запрос на удаление пользователей,
    # указанных в словаре как true, по ключу userid
    def delete_users(self, userids_maybe_checked):
        userids_to_delete = []
        # Проходим по всем ключам словаря
        for userid in userids_maybe_checked:
            # Проверяем состояние userid
            if userids_maybe_checked[userid]:
                userids_to_delete.append(userid)
        # * нужно, чтобы распаковать список как множество аргументов
        self.zabbix.user.delete(*userids_to_delete)
