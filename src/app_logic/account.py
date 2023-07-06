class Account:
    # Метод получения данных текущего пользователя
    @staticmethod
    def get_cur_user_data(zabbix):
        return zabbix.user.checkAuthentication(sessionid=zabbix.auth)
