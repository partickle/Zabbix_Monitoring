class Items:
    def __init__(self, zabbix):
        self.zabbix = zabbix

    def get_items(self, host):
        items = self.zabbix.item.get(hostids=host['hostid'], output=['itemid', 'name', 'key_'])
        return items
   