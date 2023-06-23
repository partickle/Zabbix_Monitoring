import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QLineEdit, \
    QPushButton, QDialog, QMessageBox, QHBoxLayout
from pyzabbix import ZabbixAPI, ZabbixAPIException


# Класс окна с авторизацией
class WindowLogin(QDialog):
    def __init__(self):
        super().__init__()
        # Создаем пустой экземпляр класса окна главного меню, который будет использоваться позже
        self.window_menu = None

        self.setWindowTitle("Авторизация")
        self.setFixedSize(400, 500)

        # Применение css-стилей через чтение файла
        # (setStyleSheet как аргумент использует строку)
        self.setStyleSheet(open('styles/window_login.css').read())

        # Создаем поля с лого и с вводом
        layout_input = QVBoxLayout(self)
        layout_input.setContentsMargins(50, 0, 50, 100)

        layout_logo = QVBoxLayout(self)
        layout_logo.setContentsMargins(0, 50, 0, 70)

        # Создаем виджеты с полями url(адрес API Zabbix)/user/password
        label_logo = QLabel("Zabbix Monitoring")
        label_logo.setObjectName("label_logo")
        layout_logo.addWidget(label_logo)

        layout_input.addLayout(layout_logo)

        label_url = QLabel("URL:")
        layout_input.addWidget(label_url)

        self.input_url = QLineEdit("http://25.71.15.72/")
        layout_input.addWidget(self.input_url)

        label_user = QLabel("Пользователь:")
        layout_input.addWidget(label_user)

        self.input_user = QLineEdit("Admin")
        layout_input.addWidget(self.input_user)

        label_password = QLabel("Пароль:")
        layout_input.addWidget(label_password)

        self.input_password = QLineEdit("zabbix")
        self.input_password.setEchoMode(QLineEdit.Password)
        layout_input.addWidget(self.input_password)

        button_login = QPushButton("Войти")
        button_login.clicked.connect(self.login)
        layout_input.addWidget(button_login)

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
            self.close()

            # Создание окна меню
            self.window_menu = WindowApp(zabbix)
            self.window_menu.show()
            self.window_menu.exec_()

        except ZabbixAPIException as e:
            QMessageBox.information(self, "Ошибка Zabbix API", f'{e}')
        except ConnectionError as e:
            QMessageBox.information(self, "Ошибка подключения", f'{e}')
        except TimeoutError as e:
            QMessageBox.information(self, "Тайм-аут подключения", f'{e}')
        except Exception as e:
            QMessageBox.information(self, "Общая ошибка", f'{e}')


# Класс приложения с реализацией функций API (меню)
class WindowApp(QDialog):
    def __init__(self, zabbix):
        super().__init__()

        # Создаем экземпляр Zabbix API
        self.zabbix = zabbix

        # Текущее открытое окно во втором лайауте
        self.cur_action_window = None

        self.setWindowTitle("Zabbix Monitoring")
        self.setFixedSize(1200, 700)

        self.setStyleSheet(open('styles/window_app.css').read())

        # Создаем основной лайаут
        main_layout = QHBoxLayout(self)

        # Создаем левый, средний и правый лайаут с меню, рабочим окном и логами соответственно
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignTop)

        self.middle_layout = QVBoxLayout()  # Делаем self, чтобы его можно передать в другие методы
        right_layout = QVBoxLayout()

        # Создаем массив с кнопками
        self.buttons_menu = []

        # Создаем кнопки и добавляем их в массив
        button_node_web = QPushButton("Узлы сети")
        self.buttons_menu.append(button_node_web)
        # Для каждой кнопки подключаем сигнал clicked к слоту button_clicked
        button_node_web.clicked.connect(lambda: self.button_clicked(button_node_web))
        button_node_web.clicked.connect(lambda: self.open_window_action("window_node_web"))

        button_users = QPushButton("Пользователи")
        self.buttons_menu.append(button_users)
        button_users.clicked.connect(lambda: self.button_clicked(button_users))
        button_users.clicked.connect(lambda: self.open_window_action("window_users.css"))

        left_layout.addWidget(button_node_web)
        left_layout.addWidget(button_users)

        # Добавление левого, среднего и правого окон в основной лайаут
        main_layout.addLayout(left_layout)
        main_layout.addLayout(self.middle_layout)
        main_layout.addLayout(right_layout)

        # Корректировка "зазоров" между лайаутами
        main_layout.setContentsMargins(0, 0, 0, 0)  # Отступы между краями главного лайаута
        main_layout.setSpacing(0)  # Установка того, что пространство между лайаутом и окном будет 0
        main_layout.setStretch(0, 2)  # Какой лайаут сколько частей занимает
        main_layout.setStretch(1, 4)
        main_layout.setStretch(2, 2)

    # Метод, который открывает новое окно во втором лайауте.
    # Не теряет состояние текущего окна, если нажать еще раз на кнопку
    def open_window_action(self, name_window):
        if name_window == "window_node_web" and not isinstance(self.cur_action_window, WindowNodeWeb):
            self.close_window_action()
            window_node_web = WindowNodeWeb()
            self.middle_layout.addWidget(window_node_web)
            self.cur_action_window = window_node_web
        elif name_window == "window_users.css" and not isinstance(self.cur_action_window, WindowUsers):
            self.close_window_action()
            window_users = WindowUsers()
            self.middle_layout.addWidget(window_users)
            self.cur_action_window = window_users

    # Метод, который закрывает текущее окно во втором лайауте
    def close_window_action(self):
        if self.cur_action_window is not None:
            self.cur_action_window.deleteLater()
            self.cur_action_window = None

    # Метод, который вызывается при нажатии на любую кнопку
    def button_clicked(self, button):
        for btn in self.buttons_menu:  # Проверяем каждую кнопку
            if btn != button:  # Если она не равна текущей нажатой кнопке,
                btn.setEnabled(True)
        button.setEnabled(False)  # Состояние текущей нажатой кнопки устанавливается во включенное и нажатое

    # def connect_to_zabbix(self, zabbix):
    #     hosts = zabbix.host.get(output=['hostid', 'name'], filter=['Zabbix server'])
    #     host_names = [host['name'] for host in hosts]
    #     host_id = [host['hostid'] for host in hosts]
    #
    #     self.hosts_list.setText("".join(host_names) + "          \n".join(host_id))


class WindowNodeWeb(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Zabbix App")
        self.setFixedSize(600, 700)

        self.setStyleSheet(open('styles/window_node_web.css').read())
        main_layout = QHBoxLayout(self)

        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.arr = []

        b1 = QPushButton("Button 1")
        b2 = QPushButton("Button 2")
        b3 = QPushButton("Button 3")

        self.arr.append(b1)
        self.arr.append(b2)
        self.arr.append(b3)

        b1.clicked.connect(lambda: self.button_clicked(b1))
        b2.clicked.connect(lambda: self.button_clicked(b2))
        b3.clicked.connect(lambda: self.button_clicked(b3))

        main_layout.addWidget(b1)
        main_layout.addWidget(b2)
        main_layout.addWidget(b3)

    def button_clicked(self, button):
        for btn in self.arr:  # Проверяем каждую кнопку
            if btn != button:  # Если она не равна текущей нажатой кнопке,
                btn.setEnabled(True)
        button.setEnabled(False)


class WindowUsers(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Zabbix App")
        self.setFixedSize(600, 700)

        self.setStyleSheet(open('styles/window_users.css').read())


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window_app = WindowApp(1234)
    window_app.show()

    sys.exit(app.exec_())
