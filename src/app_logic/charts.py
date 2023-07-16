class Charts:
    def __init__(self, zabbix):
        self.zabbix = zabbix
        self.charts_data = None

    def get_chart_names(self, hostid):
        self.charts_data = self.zabbix.graph.get(
            output=['graphid', 'name'], hostids=hostid
        )

        return [chart['name'] for chart in self.charts_data]
