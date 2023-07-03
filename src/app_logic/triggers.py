class Triggers:
    def __init__(self, zabbix):
        self.zabbix = zabbix
        self.hosts_info = zabbix.host.get(output=['hostid', 'name', 'host'])
        self.hosts = [host['hostid'] for host in self.hosts_info]
        self.triggers = zabbix.trigger.get(hostids=self.hosts, output=['triggerid', 'description', 'expression'], selectHosts=['host', 'hostid'])
    

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
