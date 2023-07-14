import datetime


# Класс логики окна проблем
class Problems:
    def __init__(self, zabbix):
        # Создаем переменную для хранения массива словарей с проблемами
        self.problems_data = zabbix.problem.get(
            output="extend", sortfield="eventid", sortorder="DESC",
            selectTags="extend"
        )

    # Метод, который возвращает данные
    def get_data(self):
        return self.problems_data
