import re
from pyzabbix import ZabbixAPI, ZabbixAPIException


class Settings:
    def __init__(self, zabbix):
        # Инициализируем сессию
        self.zabbix = zabbix

        # Получаем данные залогиненного пользователя
        self.user_data = zabbix.user.checkAuthentication(sessionid=zabbix.auth)

    def change_password(self, old_password, new_password, repeat_new_password):
        change_data = {
            'userid': self.user_data.get('userid'),
            'passwd': new_password,
            'current_passwd': old_password
        }

        try:
            if old_password == "" or new_password == "" or repeat_new_password == "":
                return "Не оставляйте пустых строк"

            check_password = ZabbixAPI(self.zabbix.url)
            check_password.login(user=self.user_data.get('username'), password=old_password)
            check_password.user.logout()

            if len(new_password) < 8:
                return "Пароль должен быть больше 8 символов"
            elif len(re.findall(r'a-zA-Z', new_password)) > 2:
                return "Пароль должен содержать хотя бы две буквы"
            elif new_password == repeat_new_password:
                return "Пароли не совпадают"

            self.zabbix.user.update(change_data)

        except ZabbixAPIException:
            return "Вы ввели неверный текущий пароль. Повторите попытку"

    def change_login(self, new_login, password):
        change_data = {
            'userid': self.user_data.get('userid'),
            'passwd': password,
            'username': new_login
        }

        try:
            if password == "" or new_login == "":
                return "Не оставляйте пустых строк"

            check_password = ZabbixAPI(self.zabbix.url)
            check_password.login(user=self.user_data.get('username'), password=password)
            check_password.user.logout()

            self.zabbix.user.update(change_data)

        except ZabbixAPIException:
            return "Вы ввели неверный пароль. Повторите попытку"
