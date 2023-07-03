class Hosts:
    def __init__(self, zabbix):
        self.zabbix = zabbix
        self.hosts_info = zabbix.host.get(output=['hostid', 'name', 'host'])
        self.hosts = [host['hostid'] for host in self.hosts_info]
        self.items = zabbix.item.get(hostids=self.hosts, output=['itemid', 'name', 'key_', 'hostid'])
        self.triggers = zabbix.trigger.get(hostids=self.hosts, output=['triggerid', 'description', 'expression'], selectHosts=['host', 'hostid'])

    def get_hosts(self):
        hosts_to_show = []
        for host in self.hosts_info:
            if host['host'] != 'Zabbix server':
                hosts_to_show.append(host)
        return hosts_to_show

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

    def get_triggers(self, host):
        triggers_of_host = []
        for trigger in self.triggers:
            if trigger['hosts'][0]['hostid'] == host['hostid']:
                trigger_of_host = {}
                trigger_of_host['triggerid'] = trigger['triggerid']
                trigger_of_host['description'] = trigger['description']
                trigger_of_host['expression'] = trigger['expression']
                trigger_of_host['hosts'] = trigger['hosts']
                triggers_of_host.append(trigger_of_host)
        return triggers_of_host
