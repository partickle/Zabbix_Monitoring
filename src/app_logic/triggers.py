class Triggers:
    def __init__(self, zabbix):
        self.zabbix = zabbix

    def get_triggers(self, host):
        triggers = self.zabbix.trigger.get(hostids=host['hostid'], output=['description', 'triggerid', 'expression'],
                                           expandDescription=1, expandExpression=1)
        return triggers
