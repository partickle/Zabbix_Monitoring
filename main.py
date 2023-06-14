import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from pyzabbix import ZabbixAPI


class ZabbixApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Zabbix App")
        self.setGeometry(100, 100, 400, 300)

        self.hosts_label = QLabel()
        self.hosts_label.setText("Список хостов:")

        self.hosts_list = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.hosts_label)
        layout.addWidget(self.hosts_list)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.connect_to_zabbix()

    def connect_to_zabbix(self):
        zabbix_url = 'http://www.google.com'
        zabbix_user = 'your_username'
        zabbix_password = 'your_password'

        zabbix = ZabbixAPI(url=zabbix_url)
        zabbix.login(user=zabbix_user, password=zabbix_password)

        hosts = zabbix.host.get(output=['hostid', 'name'])
        host_names = [host['name'] for host in hosts]

        self.hosts_list.setText("\n".join(host_names))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ZabbixApp()
    window.show()
    sys.exit(app.exec_())
