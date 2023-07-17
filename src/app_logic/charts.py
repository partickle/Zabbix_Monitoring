class Charts:
    def __init__(self, zabbix):
        self.zabbix = zabbix
        self.charts_data = None

        self.zabbix_url = zabbix.url.replace("api_jsonrpc.php", "")

    def get_chart_names(self, hostid):
        self.charts_data = self.zabbix.graph.get(
            output=['graphid', 'name'], hostids=hostid
        )

        return [chart['name'] for chart in self.charts_data]

    def get_graphid_by_name(self, name):
        for chart in self.charts_data:
            if chart['name'] == name:
                return chart['graphid']
        return 'Не найден'

    def get_chart_img_data(self, graphid, cd):  # cd - chart/diagram
        width = 450
        height = 400

        if cd == '6':
            width = 575
            height = 500

        params = {
            'graphid': graphid,
            'width': width,
            'height': height,
        }

        response = self.zabbix.req_session.get(
            f'{self.zabbix_url}chart{cd}.php', params=params
        )

        if response.status_code == 200:
            return response.content
        else:
            return f'Ошибка загрузки изображения: {response.status_code}'
