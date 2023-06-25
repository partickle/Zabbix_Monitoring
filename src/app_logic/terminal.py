# Пример отличного рефакторинга -
# https://github.com/guilatrova/GMaps-Crawler/blob/main/src/gmaps_crawler/facades.py

import datetime


# Класс логики терминала
class Terminal:
    def __init__(self, zabbix):
        self.zabbix = zabbix
        self.last_checked_str = ""  # Создаем переменную с последним проверенным логом

    # Метод для проверки новых логов
    def log_request(self):
        new_checked_str = ""

        # Делаем заброс event.get
        logs = self.zabbix.event.get(output='extend', sortfield='clock', sortorder='DESC')
        for log in logs:
            # Компануем элемент
            new_checked_str = log['eventid'] + "." + get_norm_data(int(log['clock'])) + " " + log['name']

        if new_checked_str != self.last_checked_str:  # Если текущая строка не равна последней, то тогда добавляем ее
            self.last_checked_str = new_checked_str
            return True

        return False

    # Метод для заполнения существующих логов
    def log_full_request(self, label):
        # Сообщение о формате отображения логов
        label.setText("FORMAT_LOGS: \"EventId.yyyy-mm-dd. HH:HM:SS Message\"\n===================\n ")

        logs = self.zabbix.event.get(output='extend', sortfield='clock', sortorder='DESC')
        for log in reversed(logs):  # Логи обычно записываются в обратном порядке, поэтому reversed
            label.setText(label.text() + "\n" + log['eventid'] + "." +
                          get_norm_data(int(log['clock'])) + " " + log['name'])

        self.last_checked_str = \
            logs[-1]['eventid'] + "." + get_norm_data(int(logs[-1]['clock'])) + " " + logs[-1]['name']


# Функция для преобразования даты из UNIX timestamp в привычную
def get_norm_data(unix_timestamp):
    datetime_obj = datetime.datetime.fromtimestamp(unix_timestamp)
    return datetime_obj.strftime('%Y-%m-%d.%H:%M:%S')
