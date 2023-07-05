class Hosts:
    def __init__(self, zabbix):
        self.zabbix = zabbix
        self.hosts_info = zabbix.host.get(output=['hostid', 'name', 'host'])
        self.hosts = [host['hostid'] for host in self.hosts_info]

    def get_hosts(self):
        hosts_to_show = []
        for host in self.hosts_info:
            if host['host'] != 'Zabbix server':
                hosts_to_show.append(host)
        return hosts_to_show
