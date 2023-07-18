class Charts:
    def __init__(self, zabbix):
        self.zabbix = zabbix  # Инициализируем экземпляр сессии
        self.charts_data = None  # Создаем дату графиков узла сети

        # Формируем ссылку обращения к хосту
        self.zabbix_url = zabbix.url.replace("api_jsonrpc.php", "")

    # Метод получения названия графиков
    def get_chart_names(self, hostid):
        # Записаем в дату ответ с запроса на получения данных о всех графиках
        # конкретного узла сети
        self.charts_data = self.zabbix.graph.get(
            output=['graphid', 'name'], hostids=hostid
        )

        # Возвращаем массив имен
        return [chart['name'] for chart in self.charts_data]

    # Метод получения id графика по его имени
    def get_graphid_by_name(self, name):
        for chart in self.charts_data:
            if chart['name'] == name:
                return chart['graphid']
        return 'Не найден'

    # Метод получения изображения графика
    def get_chart_img_data(self, graphid, cd):  # cd - chart/diagram (число)
        # chart2.php строит именно графики, chart6.php строит диаграммы

        # Создаем переменные с шириной и высотой
        width = 450
        height = None  # Для графиков высота будет адаптивной

        # Формируем размеры диаграммы
        if cd == '6':
            width = 575  # Для диаграмм высота будет фиксированная
            height = 550  # во избежание некорректного отображения

        # Создаем словарь с параметрами на запрос
        params = {
            'graphid': graphid,
            'width': width,
            'height': height,
        }

        # Делаем запрос на получение графика
        response = self.zabbix.req_session.get(
            f'{self.zabbix_url}chart{cd}.php', params=params
        )

        # Делаем проверку: все ли пришло без сбоев
        if response.status_code == 200:
            # Если да, то возвращаем дату изображения
            return response.content
        else:
            # Если нет, то сообщение об ошибке
            return f'Ошибка загрузки изображения: {response.status_code}'
