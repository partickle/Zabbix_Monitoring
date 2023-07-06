import json


# Класс логики окна авторизации
class Login:
    def __init__(self):
        # Читаем json-файл, в котором у нас будет автологинизация
        with open('res/autologin.json', 'r', encoding='utf-8') as f:
            self.autologin_data = json.load(f)

    # Метод получения url
    def get_url(self):
        return self.autologin_data.get('url')

    # Метод получения логина
    def get_login(self):
        return self.autologin_data.get('login')

    # Метод получения пароля
    def get_password(self):
        return self.autologin_data.get('password')

    # Метод проверки файла, на хранение в нем данных авторизации
    def check_autologin(self):
        # Просто проверяем не пустые ли там строки
        if self.autologin_data.get('url') == "":
            return False
        return True

    # Метод записи данных авторизации в json-файл
    @staticmethod
    def set_autologin(url, login, password):
        # Формируем дату, которую будем записывать
        data = {
            "url": url,
            "login": login,
            "password": password
        }

        # Записываем
        with open('res/autologin.json', 'w') as outfile:
            json.dump(data, outfile)

    # Метод записи пустых данных
    @staticmethod
    def set_empty_autologin():
        Login.set_autologin('', '', '')
