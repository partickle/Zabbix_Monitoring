# Пример отличного рефакторинга -
# https://github.com/guilatrova/GMaps-Crawler/blob/main/src/gmaps_crawler/facades.py

import datetime


# Класс логики терминала
class Terminal:
    def __init__(self, zabbix):
        self.zabbix = zabbix
        self.last_checked_str = ""  # Создаем переменную с последним проверенным логом
        self.last_checked_str_arr = []  # И с множеством логов

    # Метод для проверки новых логов
    def log_request(self):
        new_checked_str = []  # Создаем массив для хранения новых логов

        # Делаем заброс event.get
        logs = self.zabbix.event.get(output='extend', sortfield='clock', sortorder='DESC')

        # Если логов нет, то возвращаем False (обновлений нет)
        if len(logs) == 0:
            return False

        # Прогоняем логи через цикл
        for log in logs:  # Не reversed, потому что они и так уже в обратном порядке
            # Заводим переменную полученной строки сразу с парсингом
            new_str = log['eventid'] + "." + get_norm_data(int(log['clock'])) + " " + log['name']
            if self.last_checked_str == new_str:  # Если это последняя строка в терминале, то...
                break  # Прерываем цикл
            new_checked_str.append(new_str)  # Если нет, то добавляем ее в массив

        # Если в массиве есть обновления, то...
        if len(new_checked_str) != 0:
            self.last_checked_str_arr = list(reversed(new_checked_str))  # Сохраняем их
            return True  # И отправляем сигнал того, что пришло обновление

        return False

    # Метод для заполнения существующих логов
    def log_full_request(self, label):
        # Сообщение о формате отображения логов
        label.setText("FORMAT_LOGS: \"EventId.yyyy-mm-dd. HH:HM:SS Message\"\n===================\n ")

        logs = self.zabbix.event.get(output='extend', sortfield='clock', sortorder='DESC')
        if len(logs) == 0:
            return

        # Прогоняем все существующие логи на данный момент
        for log in reversed(logs):  # Логи обычно записываются в обратном порядке, поэтому reversed
            new_str = log['eventid'] + "." + get_norm_data(int(log['clock'])) + " " + log['name']
            label.setText(label.text() + "\n" + new_str)  # Добавляем в лейбл лог
            self.last_checked_str = new_str  # И обновляем последнюю добавленную строку


# Функция для преобразования даты из UNIX timestamp в привычную
def get_norm_data(unix_timestamp):
    datetime_obj = datetime.datetime.fromtimestamp(unix_timestamp)
    return datetime_obj.strftime('%Y-%m-%d.%H:%M:%S')
