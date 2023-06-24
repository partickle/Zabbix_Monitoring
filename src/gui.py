import sys

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
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
        self.setFixedSize(400, 550)

        # Применение css-стилей через чтение файла
        # (setStyleSheet как аргумент использует строку)
        self.setStyleSheet(open('res/styles/window_login.css').read())

        # Создаем поля с лого и с вводом
        layout_input = QVBoxLayout(self)
        layout_input.setContentsMargins(30, 0, 30, 0)
        layout_input.setAlignment(Qt.AlignTop)

        layout_logo = QVBoxLayout(self)
        layout_logo.setContentsMargins(0, 40, 0, 30)
        layout_logo.setSpacing(20)

        # Добавляем лого в формате png
        label_logo = QLabel()
        label_logo.setPixmap(QPixmap("res/img/logo.png"))
        label_logo.setAlignment(Qt.AlignCenter)

        # Создаем виджеты с полями url(адрес API Zabbix)/user/password
        label_logo_title = QLabel("Zabbix Monitoring")
        label_logo_title.setObjectName("label_logo")
        label_logo_title.setAlignment(Qt.AlignCenter)

        # Добавляем лого и надпись на лайаут
        layout_logo.addWidget(label_logo)
        layout_logo.addWidget(label_logo_title)

        layout_input.addLayout(layout_logo)

        label_url = QLabel("URL:")
        layout_input.addWidget(label_url)

        self.input_url = QLineEdit("http://25.63.71.93/")
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

        button_login = QPushButton("Вход")
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

        self.setWindowTitle("Zabbix Monitoring")
        self.setFixedSize(1200, 700)

        self.setStyleSheet(open('res/styles/window_app.css').read())

        # Создаем основной лайаут
        main_layout = QHBoxLayout(self)

        # Создаем левый виджет, средний и правый лайауты с меню, рабочим окном и логами соответственно
        middle_layout = QVBoxLayout()
        left_widget = WindowMenu(middle_layout)
        right_layout = QVBoxLayout()

        # Добавление левого, среднего и правого окон в основной лайаут
        main_layout.addWidget(left_widget)
        main_layout.addLayout(middle_layout)
        main_layout.addLayout(right_layout)

        # Корректировка "зазоров" между лайаутами
        main_layout.setContentsMargins(0, 0, 0, 0)  # Отступы между краями главного лайаута
        main_layout.setSpacing(0)  # Установка того, что пространство между лайаутом и окном будет 0
        main_layout.setStretch(0, 2)  # Какой лайаут сколько частей занимает
        main_layout.setStretch(1, 4)
        main_layout.setStretch(2, 2)


# Класс меню (слева основного окна приложения)
class WindowMenu(QDialog):
    def __init__(self, action_layout):
        super().__init__()

        # Текущее открытое окно во активном лайауте
        self.cur_action_window = None

        # Создаем копию активного окна и делаем его self, чтобы использовать в других методах
        self.action_layout = action_layout

        self.setFixedSize(300, 700)
        self.setStyleSheet(open('res/styles/window_menu.css').read())

        # Создаем главный лайаут и настраиваем отступы
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Создаем лайаут с меню и настраиваем отступы
        menu_layout = QVBoxLayout()
        menu_layout.setAlignment(Qt.AlignTop)
        menu_layout.setContentsMargins(10, 0, 0, 0)
        menu_layout.setSpacing(0)

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

        menu_layout.addWidget(button_node_web)
        menu_layout.addWidget(button_users)

        # Создаем лайаут с быстрым меню
        quick_layout = QHBoxLayout()

        # Создаем кнопки
        button_user = QPushButton()
        button_user.setObjectName("quick_buttons")  # Присваиваем отдельный класс для стилизации
        button_user.setIcon(QIcon("res/icon/user.svg"))  # Добавляем в кнопку иконку в svg-формате для качества
        button_user.setIconSize(QSize(48, 48))  # Задаем размер
        quick_layout.addWidget(button_user)

        button_settings = QPushButton()
        button_settings.setObjectName("quick_buttons")
        button_settings.setIcon(QIcon("res/icon/settings.svg"))
        button_settings.setIconSize(QSize(48, 48))
        quick_layout.addWidget(button_settings)

        button_logout = QPushButton()
        button_logout.setObjectName("quick_buttons")
        button_logout.setIcon(QIcon('res/icon/logout.svg'))
        button_logout.setIconSize(QSize(48, 48))
        quick_layout.addWidget(button_logout)

        # Добавляем на лайаут
        main_layout.addLayout(menu_layout)
        main_layout.addLayout(quick_layout)

    # Метод, который открывает новое окно в активном лайауте.
    # Не теряет состояние текущего окна, если нажать еще раз на кнопку
    def open_window_action(self, name_window):
        if name_window == "window_node_web" and not isinstance(self.cur_action_window, WindowNodeWeb):
            self.close_window_action()
            window_node_web = WindowNodeWeb()
            self.action_layout.addWidget(window_node_web)
            self.cur_action_window = window_node_web
        elif name_window == "window_users.css" and not isinstance(self.cur_action_window, WindowUsers):
            self.close_window_action()
            window_users = WindowUsers()
            self.action_layout.addWidget(window_users)
            self.cur_action_window = window_users

    # Метод, который закрывает текущее окно в активном лайауте
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


# Класс активного окна узлов сети
class WindowNodeWeb(QDialog):
    def __init__(self):
        super().__init__()

        self.setFixedSize(600, 700)
        self.setStyleSheet(open('res/styles/window_node_web.css').read())

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


# Класс активного окна с пользователями
class WindowUsers(QDialog):
    def __init__(self):
        super().__init__()

        self.setFixedSize(600, 700)
        self.setStyleSheet(open('res/styles/window_users.css').read())


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window_login = WindowApp(67)
    window_login.show()

    sys.exit(app.exec_())
