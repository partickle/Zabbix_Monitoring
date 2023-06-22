import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLineEdit, \
    QPushButton, QDialog, QMessageBox
from pyzabbix import ZabbixAPI, ZabbixAPIException


class WindowLogin(QDialog):
    def __init__(self):
        super().__init__()

        # Загружаем строку с css-стилем для Qt-tools
        # (setStyleSheet как аргумент использует строку)
        with open('styles/window_login.css', 'r') as css_file:
            self.style_sheet = css_file.read()

        self.setWindowTitle("Авторизация")
        self.setFixedSize(400, 500)

        self.setStyleSheet(self.style_sheet)

        # Создаем виджеты с полями url(адрес API Zabbix)/user/password
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 0, 50, 100)

        layout_logo = QVBoxLayout(self)
        layout_logo.setContentsMargins(0, 50, 0, 70)

        label_logo = QLabel("Zabbix Monitoring")
        label_logo.setObjectName("label_logo")
        layout_logo.addWidget(label_logo)

        layout.addLayout(layout_logo)

        label_url = QLabel("URL:")
        layout.addWidget(label_url)

        self.input_url = QLineEdit()
        layout.addWidget(self.input_url)

        label_user = QLabel("User:")
        layout.addWidget(label_user)

        self.input_user = QLineEdit()
        layout.addWidget(self.input_user)

        label_password = QLabel("Password:")
        layout.addWidget(label_password)

        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_password)

        button_login = QPushButton("Login")
        button_login.clicked.connect(self.login)
        layout.addWidget(button_login)

    # Метод подключения к API Zabbix
    def login(self):
        url = self.input_url.text()
        user = self.input_user.text()
        password = self.input_password.text()

        # Обработка ошибок
        if url == "" or user == "" or password == "":
            QMessageBox.information(self, "Мда", "Введите что-нибудь...")
            return

        try:
            # Подключение
            zabbix = ZabbixAPI(url)
            zabbix.login(user, password)
            QMessageBox.information(self, "Успех", "Вы успешно вошли!")
            self.windowMenu = WindowMenu(zabbix)
            self.windowMenu.show()

        except ZabbixAPIException as e:
            QMessageBox.information(self, "Ошибка Zabbix API", f'{e}')
        except ConnectionError as e:
            QMessageBox.information(self, "Ошибка подключения", f'{e}')
        except TimeoutError as e:
            QMessageBox.information(self, "Тайм-аут подключения", f'{e}')
        except Exception as e:
            QMessageBox.information(self, "Общая ошибка", f'{e}')


# Класс приложения с реализацией функций API (меню)
class WindowMenu(QMainWindow):
    def __init__(self, zabbix):
        super().__init__()
        self.setWindowTitle("Zabbix Monitoring")
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
        self.connect_to_zabbix(zabbix)

    def connect_to_zabbix(self, zabbix):
        #hosts = zabbix.host.get(search={'host':['Zabbix server']}, excludeSearch=1, output=['hostid', 'name']) excludeSearch не работает на данной версии
        hosts = zabbix.host.get(output=['hostid', 'name', 'host'])
        print(hosts)
        hostsToPrint = []
        for host in hosts:
            if host['name'] != 'Zabbix server':
                hostsToPrint.append(host)
        host_names = [host['host'] for host in hostsToPrint]
        self.hosts_list.setText("\n".join(host_names))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WindowLogin()
    window.show()
    sys.exit(app.exec_())
