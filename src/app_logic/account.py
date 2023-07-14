class Account:
    def __init__(self, zabbix):
        # Получаем данные текущего пользователя
        self.user_data = zabbix.user.checkAuthentication(sessionid=zabbix.auth)

    # Метод получения имени пользователя
    def get_name(self):
        return self.user_data.get('name')

    # Метод получения фамилии пользователя
    def get_surname(self):
        return self.user_data.get('surname')

    # Метод получения логина пользователя
    def get_username(self):
        return self.user_data.get('username')

    # Метод получения языка, который стоит у пользователя
    def get_lang(self):
        return self.user_data.get('lang')
