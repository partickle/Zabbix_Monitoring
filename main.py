import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLineEdit, \
    QPushButton, QDialog, QMessageBox
from pyzabbix import ZabbixAPI, ZabbixAPIException


class WindowConnect(QDialog):
    def __init__(self):
        super().__init__()

        # Задаем css-стиль для Qt-tools
        self.style_sheet = """
                    QLabel {
                        color: #333333;
                        font-size: 16px;
                        font-weight: bold;
                    }

                    QLineEdit {
                        background-color: #F0F0F0;
                        border: 1px solid #CCCCCC;
                        padding: 5px;
                        border-radius: 3px;
                    }

                    QPushButton {
                        background-color: #0078D7;
                        color: #FFFFFF;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 3px;
                        font-weight: bold;
                    }

                    QPushButton:hover {
                        background-color: #005CA9;
                    }

                    QPushButton:pressed {
                        background-color: #002D5A;
                    }
                """

        self.setWindowTitle("Zabbix Monitoring")
        self.setFixedSize(350, 250)

        self.setStyleSheet(self.style_sheet)

        # Создаем виджеты с полями url(адрес API Zabbix)/user/password
        layout = QVBoxLayout(self)

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

        except ZabbixAPIException as e:
            QMessageBox.information(self, "Ошибка Zabbix API", f'{e}')
        except ConnectionError as e:
            QMessageBox.information(self, "Ошибка подключения", f'{e}')
        except TimeoutError as e:
            QMessageBox.information(self, "Тайм-аут подключения", f'{e}')
        except Exception as e:
            QMessageBox.information(self, "Общая ошибка", f'{e}')


# Класс приложения с реализацией функций API (меню)
class WindowZabbixApp(QMainWindow):
    def __init__(self):
        super().__init__()
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

        # def connect_to_zabbix(self):
        #     hosts = zabbix.host.get(output=['hostid', 'name'])
        #     host_names = [host['name'] for host in hosts]
        #
        #     self.hosts_list.setText("\n".join(host_names))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WindowConnect()
    window.show()
    sys.exit(app.exec_())
