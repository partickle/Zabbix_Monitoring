class Charts:
    def __init__(self, zabbix):
        self.charts_data = zabbix.graph.get(output="extend")
        print(self.graphs_data)
