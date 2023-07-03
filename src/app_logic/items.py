class Items:
    def __init__(self, zabbix):
        self.zabbix = zabbix
        self.hosts_info = zabbix.host.get(output=['hostid', 'name', 'host'])
        self.hosts = [host['hostid'] for host in self.hosts_info]
        self.items = zabbix.item.get(hostids=self.hosts, output=['itemid', 'name', 'key_', 'hostid'])
    

    def get_items(self, host):
        items_of_host = []
        for item in self.items:
            if item['hostid'] == host['hostid']:
                item_of_host = {}
                item_of_host['itemid'] = item['itemid']
                item_of_host['name'] = item['name']
                item_of_host['key_'] = item['key_']
                item_of_host['hostid'] = item['hostid']
                items_of_host.append(item_of_host)
        return items_of_host
