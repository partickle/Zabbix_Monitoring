class Hosts:
    def __init__(self, zabbix):
        self.zabbix = zabbix

    def get_hosts(self):
        hosts = self.zabbix.host.get(output=['hostid','name','host'])
        hosts_to_show = []
        for host in hosts:
            if host['host'] != 'Zabbix server':
                hosts_to_show.append(host)
        return hosts_to_show

    def get_items(self, host):
        items = self.zabbix.item.get(hostids=host['hostid'], output=['itemid','name'])
        return items

    def get_triggers(self, host):
        triggers = self.zabbix.trigger.get(hostids=host['hostid'], output=['triggerid','status'])
        return triggers
