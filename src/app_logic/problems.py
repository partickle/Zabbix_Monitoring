import datetime


class Problems:
    def __init__(self, zabbix):
        self.problems_data = zabbix.problem.get(
            output="extend", sortfield="eventid", sortorder="DESC",
            selectTags="extend"
        )

    def get_data(self):
        return self.problems_data

    # Функция для преобразования даты из UNIX timestamp в привычную
    @staticmethod
    def get_norm_data(unix_timestamp):
        datetime_obj = datetime.datetime.utcfromtimestamp(unix_timestamp)
        return datetime_obj.strftime('%Y.%m.%d\n%H:%M:%S')
