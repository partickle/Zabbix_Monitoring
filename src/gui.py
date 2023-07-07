import sys
import inspect
import threading

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QLineEdit, \
    QPushButton, QDialog, QMessageBox, QHBoxLayout, QScrollArea, QCheckBox, \
    QWidget, QGridLayout

from pyzabbix import ZabbixAPI, ZabbixAPIException
from app_logic import Terminal, Hosts, Items, Triggers, Account, Settings, \
    Interfaces, Login


# Класс окна с авторизацией
class WindowLogin(QDialog):
    def __init__(self):
        super().__init__()
        # Создаем пустой экземпляр класса окна главного меню, который будет
        # использоваться позже
        self.window_menu = None

        # Создаем экземпляр класса логики
        self.login_logic = Login()

        self.setWindowTitle("Авторизация")
        self.setFixedSize(400, 580)

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

        self.input_url = QLineEdit(self.login_logic.get_url())

        layout_input.addWidget(self.input_url)

        label_user = QLabel("Пользователь:")
        layout_input.addWidget(label_user)

        self.input_user = QLineEdit(self.login_logic.get_login())
        layout_input.addWidget(self.input_user)

        label_password = QLabel("Пароль:")
        layout_input.addWidget(label_password)

        self.input_password = QLineEdit(self.login_logic.get_password())

        self.input_password.setEchoMode(QLineEdit.Password)
        layout_input.addWidget(self.input_password)

        self.check_box = QCheckBox("Сохранить данные для входа")
        # Включаем/выключаем чекбокс
        self.check_box.setChecked(self.login_logic.check_autologin())
        layout_input.addWidget(self.check_box)

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

            # Сохранение пароля
            if self.check_box.isChecked():  # Если стоит галочка
                # То перезаписываем json
                Login.set_autologin(url, user, password)
            else:  # Если нет, то
                # То записываем пустые строки
                Login.set_empty_autologin()

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

        # Создаем левый виджет, средний и правый лайауты с
        # меню, рабочим окном и логами соответственно
        middle_layout = QVBoxLayout()
        left_widget = WindowMenu(middle_layout, self.zabbix, self)
        self.right_widget = WindowTerminal(self.zabbix)

        # Добавление левого, среднего и правого окон в основной лайаут
        main_layout.addWidget(left_widget)
        main_layout.addLayout(middle_layout)
        main_layout.addWidget(self.right_widget)

        # Корректировка "зазоров" между лайаутами

        # Отступы между краями главного лайаута
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Установка того, что пространство между лайаутом и окном будет 0
        main_layout.setSpacing(0)

        # Какой лайаут сколько частей занимает
        main_layout.setStretch(0, 2)
        main_layout.setStretch(1, 4)
        main_layout.setStretch(2, 2)

    # Метод, который при нажатии на крестик окна, выключает таймер и
    # закрывает его
    def closeEvent(self, event):
        self.right_widget.timer_flag = False
        event.accept()

    # Метод безопасно закрывает переданное окно
    @staticmethod
    def close_window(window_to_close):
        if window_to_close is not None:
            window_to_close.deleteLater()

    # Метод обновления окна
    @staticmethod
    def update_window_on_layout(cur_window, action_layout):
        new_window = WindowApp.make_new_instance_of_class_from_object(
            cur_window
        )
        action_layout.addWidget(new_window)
        WindowApp.close_window(cur_window)

    # Создает новый объект, копируя аргументы конструктора старого объекта
    @staticmethod
    def make_new_instance_of_class_from_object(cur_object):
        args = inspect.signature(cur_object.__init__).parameters.values()
        arg_values = [getattr(cur_object, arg.name) for arg in args]
        new_object = globals()[cur_object.__class__.__name__](*arg_values)
        return new_object


# Класс меню (слева основного окна приложения)
class WindowMenu(QDialog):
    def __init__(self, action_layout, zabbix, window_app):
        super().__init__()

        # Присваиваем текущую сессию
        self.zabbix = zabbix

        # Присваиваем окно приложения
        self.window_app = window_app

        # Создаем пустую переменную окна авторизации
        self.window_login = None

        # Текущее открытое окно во активном лайауте
        self.cur_action_window = None

        # Создаем копию активного окна и делаем его self,
        # чтобы использовать в других методах
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
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(0)

        # Создаем массив с кнопками
        self.buttons_menu = []

        # Создаем кнопки и добавляем их в массив
        button_node_web = QPushButton("Узлы сети")
        self.buttons_menu.append(button_node_web)

        # Для каждой кнопки подключаем сигнал clicked к слоту button_clicked
        button_node_web.clicked.connect(
            lambda: self.button_clicked(
                button_node_web
            )
        )

        button_node_web.clicked.connect(
            lambda: self.open_window_action(
                "window_node_web"
            )
        )

        button_users = QPushButton("Пользователи")
        self.buttons_menu.append(button_users)

        button_users.clicked.connect(
            lambda: self.button_clicked(
                button_users
            )
        )

        button_users.clicked.connect(
            lambda: self.open_window_action(
                "window_users"
            )
        )

        menu_layout.addWidget(button_node_web)
        menu_layout.addWidget(button_users)

        # Создаем лайаут с быстрым меню
        quick_layout = QHBoxLayout()

        # Создаем кнопки
        button_account = QPushButton()
        self.buttons_menu.append(button_account)
        # Присваиваем отдельный класс для стилизации
        button_account.setObjectName("quick_buttons")
        # Добавляем в кнопку иконку в svg-формате для качества
        button_account.setIcon(QIcon("res/icon/user.svg"))
        # Задаем размер
        button_account.setIconSize(QSize(48, 48))
        button_account.clicked.connect(
            lambda: self.button_clicked(
                button_account
            )
        )
        button_account.clicked.connect(
            lambda: self.open_window_action(
                "window_account"
            )
        )
        quick_layout.addWidget(button_account)

        button_settings = QPushButton()
        self.buttons_menu.append(button_settings)
        button_settings.setObjectName("quick_buttons")
        button_settings.setIcon(QIcon("res/icon/settings.svg"))
        button_settings.setIconSize(QSize(48, 48))
        button_settings.clicked.connect(
            lambda: self.button_clicked(
                button_settings
            )
        )
        button_settings.clicked.connect(
            lambda: self.open_window_action(
                "window_settings"
            )
        )
        quick_layout.addWidget(button_settings)

        button_logout = QPushButton()
        self.buttons_menu.append(button_logout)
        button_logout.setObjectName("quick_buttons")
        button_logout.setIcon(QIcon('res/icon/logout.svg'))
        button_logout.setIconSize(QSize(48, 48))
        button_logout.clicked.connect(
            lambda: self.button_clicked(
                button_logout
            )
        )
        button_logout.clicked.connect(self.button_logout)
        quick_layout.addWidget(button_logout)

        # Добавляем на лайаут
        main_layout.addLayout(menu_layout)
        main_layout.addLayout(quick_layout)

    # Метод, который открывает новое окно в активном лайауте.
    # Не теряет состояние текущего окна, если нажать еще раз на кнопку
    def open_window_action(self, name_window):
        if name_window == "window_node_web":
            self.close_window_action()
            window_node_web = WindowNodeWeb(
                self.zabbix, self.action_layout, self
            )
            self.action_layout.addWidget(window_node_web)
            self.cur_action_window = window_node_web
        elif name_window == "window_users":
            self.close_window_action()
            window_users = WindowUsers(self.zabbix, self.action_layout)
            self.action_layout.addWidget(window_users)
            self.cur_action_window = window_users
        elif name_window == "window_account":
            self.close_window_action()
            window_account = WindowAccount(self.zabbix)
            self.action_layout.addWidget(window_account)
            self.cur_action_window = window_account
        elif name_window == "window_settings":
            self.close_window_action()
            window_settings = WindowSettings(self.zabbix)
            self.action_layout.addWidget(window_settings)
            self.cur_action_window = window_settings

    # Метод выхода из учетной записи
    def button_logout(self):
        # Закрытие окна приложения
        self.window_app.close()

        # Создание окна авторизации
        self.window_login = WindowLogin()
        self.window_login.show()
        self.window_login.exec_()

    # Метод, который закрывает текущее окно в активном лайауте
    def close_window_action(self):
        if self.cur_action_window is not None:
            self.cur_action_window.deleteLater()
            self.cur_action_window = None

    # Метод, который вызывается при нажатии на любую кнопку
    def button_clicked(self, button):
        for btn in self.buttons_menu:  # Проверяем каждую кнопку
            if btn != button:  # Если она не равна текущей нажатой кнопке
                btn.setEnabled(True)
        # Состояние текущей нажатой кнопки устанавливается во включенное и
        # нажатое
        button.setEnabled(False)


class WindowAccount(QDialog):
    def __init__(self, zabbix):
        super().__init__()

        # Создаем словарь с данными для того, чтобы не делать кучу запросов
        self.user_data = Account.get_cur_user_data(zabbix)

        self.setFixedSize(600, 700)
        self.setStyleSheet(open('res/styles/window_account.css').read())

        # Создаем все нужные лейблы
        title = QLabel("Пользователь")
        title.setObjectName("title")

        icon = QLabel()
        icon.setPixmap(QIcon("res/icon/user_account.svg").pixmap(150, 150))

        name = QLabel(self.user_data.get('name'))
        name.setObjectName("name")

        surname = QLabel(self.user_data.get('surname'))
        surname.setObjectName("name")

        username_label = QLabel("Логин: ")
        username_label.setObjectName("label")

        lang_label = QLabel("Язык: ")
        lang_label.setObjectName("label")

        username = QLabel(self.user_data.get('username'))
        lang = QLabel(self.user_data.get('lang'))

        # Создаем главный лайаут
        main_layout = QVBoxLayout(self)

        # Создаем верхний и нижний лайауты
        top_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 350)

        # Создаем угловые лайауты
        left_top_layout = QVBoxLayout()
        left_top_layout.setAlignment(Qt.AlignRight | Qt.AlignBottom)

        right_top_layout = QVBoxLayout()
        right_top_layout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)

        left_bottom_layout = QVBoxLayout()
        left_bottom_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)

        right_bottom_layout = QVBoxLayout()
        right_bottom_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Добавляем все лайауты
        main_layout.addWidget(title)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)

        top_layout.addLayout(left_top_layout)
        top_layout.addLayout(right_top_layout)
        bottom_layout.addLayout(left_bottom_layout)
        bottom_layout.addLayout(right_bottom_layout)

        # А потом и лейблы на них
        left_top_layout.addWidget(icon)

        right_top_layout.addWidget(name)
        right_top_layout.addWidget(surname)

        left_bottom_layout.addWidget(username_label)
        left_bottom_layout.addWidget(lang_label)

        right_bottom_layout.addWidget(username)
        right_bottom_layout.addWidget(lang)

        # Отступы между краями главного лайаута
        main_layout.setContentsMargins(0, 0, 0, 0)


class WindowSettings(QDialog):
    def __init__(self, zabbix):
        super().__init__()

        # Инициализируем текущую сессию
        self.zabbix = zabbix

        # Создаем экземпляр класса логики
        self.settings_logic = Settings(zabbix)

        self.setFixedSize(600, 700)
        self.setStyleSheet(open('res/styles/window_settings.css').read())

        # Создаем все нужные лейблы
        title = QLabel("Настройки")
        title.setObjectName("title")

        # Создаем главный лайаут
        main_layout = QVBoxLayout(self)

        # Создаем нижний лайаут
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 250)

        # Создаем два угловых нижних лайаута
        left_bottom_layout = QVBoxLayout()
        left_bottom_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)

        right_bottom_layout = QVBoxLayout()
        right_bottom_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Добавляем все лайауты
        main_layout.addWidget(title)
        main_layout.addLayout(bottom_layout)

        bottom_layout.addLayout(left_bottom_layout)
        bottom_layout.addLayout(right_bottom_layout)

        # Создаем интерактивные элементы
        label_new_password = QLabel("Сменить пароль: ")
        label_new_password.setContentsMargins(0, 0, 0, 140)
        label_new_password.setObjectName('label')

        self.old_password = QLineEdit()
        self.old_password.setPlaceholderText("Текущий пароль")
        self.old_password.setEchoMode(QLineEdit.Password)

        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("Новый пароль")
        self.new_password.setEchoMode(QLineEdit.Password)

        self.repeat_new_password = QLineEdit()
        self.repeat_new_password.setPlaceholderText(
            "Новый пароль (подтверждение)"
        )
        self.repeat_new_password.setEchoMode(QLineEdit.Password)

        button_password = QPushButton("Сменить")
        button_password.setObjectName("change")
        button_password.clicked.connect(self.click_button_password)

        label_new_login = QLabel("Сменить логин: ")
        label_new_login.setObjectName('label')

        self.password = QLineEdit()
        self.password.setPlaceholderText("Текущий пароль")
        self.password.setEchoMode(QLineEdit.Password)

        self.new_login = QLineEdit()
        self.new_login.setPlaceholderText("Новый логин")

        button_login = QPushButton("Сменить")
        button_login.setObjectName("change")
        button_login.clicked.connect(self.click_button_login)

        # Добавляем все на лайауты
        left_bottom_layout.addWidget(label_new_password)
        left_bottom_layout.addWidget(label_new_login)

        right_bottom_layout.addWidget(self.old_password)
        right_bottom_layout.addWidget(self.new_password)
        right_bottom_layout.addWidget(self.repeat_new_password)
        right_bottom_layout.addWidget(button_password)

        right_bottom_layout.addWidget(self.password)
        right_bottom_layout.addWidget(self.new_login)
        right_bottom_layout.addWidget(button_login)

        # Отступы между краями главного лайаута
        main_layout.setContentsMargins(0, 0, 0, 0)

    def click_button_password(self):
        QMessageBox.information(
            self, "Смена пароля", self.settings_logic.change_password(
                self.old_password.text(), self.new_password.text(),
                self.repeat_new_password.text()))

    def click_button_login(self):
        QMessageBox.information(
            self, "Смена логина", self.settings_logic.change_login(
                self.new_login.text(), self.password.text()))


# Класс окна терминала, в котором
# будут транслироваться в реальном времени логи zabbix
class WindowTerminal(QDialog):
    def __init__(self, zabbix):
        super().__init__()

        # Создаем экземпляр класса с логикой терминала
        self.terminal = Terminal(zabbix)

        # Флаг для отключения таймера в closeEvent
        self.timer_flag = True

        self.setFixedSize(300, 700)
        self.setStyleSheet(open('res/styles/window_terminal.css').read())

        # Создаем лейбл, в котором будут отображаться логи
        self.label = QLabel()
        self.label.setFixedWidth(275)
        self.label.setAlignment(Qt.AlignTop)
        self.label.setWordWrap(True)

        # Создаем скролл, чтобы можно было смотреть предыдущие записи
        scroll_area = QScrollArea(self)
        scroll_area.setFixedSize(300, 700)

        # Отключаем горизонтальный скролл
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Включаем динамическое масштабирование,
        # т.к. у нас будет увеличиваться окно
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.label)

        # Загружаем сначала полный список логов
        self.terminal.log_full_request(self.label)

        # Ставим таймер секунду
        self.timer = threading.Timer(1.0, self.update_terminal)
        self.timer.start()

    # Метод обновления лейбла логов
    def update_terminal(self):
        # Если пришло обновление логов, то отображаем его
        if self.terminal.log_request():
            self.label.setText(
                self.label.text()
                + "\n".join(self.terminal.last_checked_str_arr)
                + "\n"
            )

        # Если флаг таймера True, то...
        if self.timer_flag:
            # Здесь тоже создаем таймер, чтобы его зарекурсировать
            self.timer = threading.Timer(1.0, self.update_terminal)
            self.timer.start()


# Класс активного окна узлов сети
class WindowNodeWeb(QDialog):
    def __init__(self, zabbix, action_layout, window_menu):
        super().__init__()

        self.setFixedSize(600, 700)
        self.setStyleSheet(open('res/styles/window_node_web.css').read())

        # Создаем экземпляры логики хостов, элементов данных и триггеров
        self.hosts = Hosts(zabbix)
        self.items = Items(zabbix)
        self.triggers = Triggers(zabbix)

        # API zabbix в сессии
        self.zabbix = zabbix

        # Текущий центральный лайаут, куда добавляются окна
        self.action_layout = action_layout

        # Ссылка на текущее открытое окно в центральном лайауте
        self.window_menu = window_menu

        # Основной лайаут - вертикальный
        root_vbox_layout = QVBoxLayout(self)

        # В основной лайаут добавится зона с прокруткой
        main_window_scroll_area = QScrollArea()

        # И панель с кнопками
        panel_of_buttons_widget = QWidget()

        # Отключаем горизонтальный скролл
        main_window_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        # Включаем динамическое масштабирование,
        main_window_scroll_area.setWidgetResizable(
            True
        )

        # Виджет, который вставится в scroll area
        main_window_scroll_widget = QWidget()

        # Лайаут панели с кнопками вставится в ее виджет
        panel_of_buttons_layout = QHBoxLayout()

        # Добавление кнопок в соответствующую панель
        add_host_button = QPushButton("Add")
        add_host_button.clicked.connect(
            lambda: self.add_host_button_clicked()
        )
        delete_chosen_hosts_button = QPushButton("Delete")
        delete_chosen_hosts_button.clicked.connect(
            lambda: self.delete_chosen_hosts_button_clicked()
        )

        # Основной лайаут scroll area
        self.main_window_hosts_layout = QGridLayout()

        hosts = self.hosts.get_hosts()

        # Для каждого хоста создается свой виджет и лайаут его
        # надписей и кнопок
        for host in hosts:
            current_item_widget = QWidget()
            current_item_layout = QHBoxLayout()

            is_selected_checkbox = QCheckBox()
            current_item_layout.addWidget(is_selected_checkbox)

            current_item_name_label = QLabel()
            current_item_name_label.setText(host['host'])
            current_item_layout.addWidget(current_item_name_label)

            current_item_key_label = QLabel()
            current_item_key_label.setText(host['hostid'])
            current_item_layout.addWidget(current_item_key_label)

            # Кнопка открытия окна элементов данных конкретного хоста
            current_host_items_button = QPushButton(
                'items' + ' ' + str(len(self.items.get_items(host)))
            )
            current_item_layout.addWidget(current_host_items_button)

            # Очень странно, что код снизу(тоже закоменченный) уже работает,
            # а этот код - нет
            # current_host_items_button.clicked.connect(
            #     lambda: self.items_button_clicked(host)
            # )

            # Этот рабочий код для закоменченного варианта вызываемой функции
            # current_host_items_button.clicked.connect(
            #     lambda state, x=host: self.items_button_clicked(x)
            # )

            # Рабочий вариант для текущего варианта вызываемой функции
            current_host_items_button.clicked.connect(
                self.items_button_clicked(host)
            )

            # Кнопка открытия окна триггеров конкретного хоста
            current_host_triggers_button = QPushButton(
                'triggers' + ' ' + str(len(self.triggers.get_triggers(host)))
            )
            current_item_layout.addWidget(current_host_triggers_button)
            current_host_triggers_button.clicked.connect(
                self.triggers_button_clicked(host)
            )

            current_item_widget.setLayout(current_item_layout)
            self.main_window_hosts_layout.addWidget(current_item_widget)

        # Вложение всех элементов так, как указано при их создании
        main_window_scroll_widget.setLayout(self.main_window_hosts_layout)
        panel_of_buttons_layout.addWidget(add_host_button)
        panel_of_buttons_layout.addWidget(delete_chosen_hosts_button)
        main_window_scroll_area.setWidget(main_window_scroll_widget)
        panel_of_buttons_widget.setLayout(panel_of_buttons_layout)
        root_vbox_layout.addWidget(main_window_scroll_area)
        root_vbox_layout.addWidget(panel_of_buttons_widget)

    # def items_button_clicked(self, host):
    #     window_items = WindowItems(self.zabbix, self.action_layout, host)
    #     self.action_layout.addWidget(window_items)
    #     WindowApp.close_window(self)

    # Функция обработки события нажатия на элементы данных хоста
    # Как я понял, здесь мы возвращаем connect-y
    # упакованную функцию button_clicked и выглядит это примерно так:
    # button.clicked.connect(button_clicked)
    # в которую уже упаковано значение host и self-поля,
    # что позволяет корректно привязывать обработку событий
    def items_button_clicked(self, host):
        def button_clicked():
            window_items = WindowItems(
                self.zabbix, self.action_layout, self.window_menu, host
            )
            self.window_menu.cur_action_window = window_items
            self.action_layout.addWidget(window_items)
            WindowApp.close_window(self)
        return button_clicked

    # Функция обработки события нажатия на триггеры хоста
    def triggers_button_clicked(self, host):
        def button_clicked():
            window_triggers = WindowTriggers(
                self.zabbix, self.action_layout, self.window_menu, host
            )
            self.window_menu.cur_action_window = window_triggers
            self.action_layout.addWidget(window_triggers)
            WindowApp.close_window(self)
        return button_clicked

    # Функция открытия окна добавления хоста по нажатию на кнопку
    def add_host_button_clicked(self):
        window_add_host = WindowAddHost(
            self.zabbix, self.action_layout, self.window_menu
        )
        self.window_menu.cur_action_window = window_add_host
        self.action_layout.addWidget(window_add_host)
        WindowApp.close_window(self)

    # Функция удаления хостов, которым установлена галочка в чекбоксе
    def delete_chosen_hosts_button_clicked(self):
        hostids_maybe_checked = {}
        for i in range(self.main_window_hosts_layout.rowCount()):
            value = self.main_window_hosts_layout \
                .itemAtPosition(i, 0).widget() \
                .layout().itemAt(0).widget().isChecked()
            key = self.main_window_hosts_layout \
                .itemAtPosition(i, 0).widget() \
                .layout().itemAt(2).widget().text()
            hostids_maybe_checked[key] = value
        self.hosts.delete_hosts(hostids_maybe_checked)
        WindowApp.update_window_on_layout(self, self.action_layout)


# Класс окна добавления нового хоста
class WindowAddHost(QDialog):
    def __init__(self, zabbix, action_layout, window_menu):
        super().__init__()

        self.setFixedSize(600, 700)
        self.setStyleSheet(open('res/styles/window_add_host.css').read())

        # Создает экземпляр логики хостов
        self.hosts = Hosts(zabbix)

        # API zabbix в сессии
        self.zabbix = zabbix

        # Текущий центральный лайаут, куда добавляются окна
        self.action_layout = action_layout

        # Ссылка на текущее открытое окно в центральном лайауте
        self.window_menu = window_menu

        # Основной лайаут - вертикальный
        root_vbox_layout = QVBoxLayout(self)

        # Кнопка возврата к окну хостов в основном лайауте
        return_button = QPushButton()
        return_button.setIcon(QIcon("res/icon/arrow_back.svg"))
        return_button.setIconSize(QSize(50, 50))

        # Привязка обработки события нажатия на нее
        return_button.clicked.connect(
            lambda: self.return_button_clicked()
        )

        # Поля для заполнения
        self.host_name_field = QLineEdit()
        self.host_ip_field = QLineEdit()

        # Кнопка добавления
        host_create_button = QPushButton("Добавить")
        host_create_button.clicked.connect(
            lambda: self.host_create_button_clicked()
        )

        root_vbox_layout.addWidget(return_button)
        root_vbox_layout.addWidget(self.host_name_field)
        root_vbox_layout.addWidget(self.host_ip_field)
        root_vbox_layout.addWidget(host_create_button)

    # Функция выполняет возврат обратно к окну хостов
    def return_button_clicked(self):
        window_hosts = WindowNodeWeb(
            self.zabbix, self.action_layout, self.window_menu
        )
        self.window_menu.cur_action_window = window_hosts
        self.action_layout.addWidget(window_hosts)
        WindowApp.close_window(self)

    # Добавление хоста и возврат к окну хостов
    def host_create_button_clicked(self):
        self.hosts.add_host(
            self.host_name_field.text(), self.host_ip_field.text()
        )
        self.return_button_clicked()


# Класс окна элементов данных конкретного хоста
class WindowItems(QDialog):
    def __init__(self, zabbix, action_layout, window_menu, host):
        super().__init__()

        self.setFixedSize(600, 700)
        self.setStyleSheet(open('res/styles/window_items.css').read())

        # Создаем экземпляр логики элементов данных
        self.items = Items(zabbix)

        # API zabbix в сессии
        self.zabbix = zabbix

        # Хост, у которого просматриваются элементы данных
        self.host = host

        # Текущий центральный лайаут, куда добавляются окна
        self.action_layout = action_layout

        # Ссылка на текущее открытое окно в центральном лайауте
        self.window_menu = window_menu

        # Основной лайаут - вертикальный
        root_vbox_layout = QVBoxLayout(self)

        # Кнопка возврата к окну хостов в основном лайауте
        return_button = QPushButton()
        return_button.setIcon(QIcon("res/icon/arrow_back.svg"))
        return_button.setIconSize(QSize(50, 50))

        # Привязка обработки события нажатия на нее
        return_button.clicked.connect(
            lambda: self.return_button_clicked()
        )

        # Основное окно со скроллом элементов данных
        main_window_scroll_area = QScrollArea()

        # Отключаем горизонтальный скролл
        main_window_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        # Включаем динамическое масштабирование
        main_window_scroll_area.setWidgetResizable(
            True
        )
        # Виджет панели с кнопками в основном лайауте
        panel_of_buttons_widget = QWidget()

        # Виджет скролл-окна
        main_window_scroll_widget = QWidget()

        # Лайаут панели с кнопками вставится в ее виджет
        panel_of_buttons_layout = QHBoxLayout()

        # Добавление соответствующих кнопок в лайаут панели
        add_item_button = QPushButton("Add")
        add_item_button.clicked.connect(
            lambda: self.add_item_button_clicked()
        )
        delete_chosen_items_button = QPushButton("Delete")
        delete_chosen_items_button.clicked.connect(
            lambda: self.delete_chosen_items_button_clicked()
        )
        # Основной лайаут scroll area
        self.main_window_items_layout = QGridLayout()

        items = self.items.get_items(self.host)

        # Для каждого элемента данных создается виджет и
        # лайаут надписей с информацией
        for item in items:
            current_item_widget = QWidget()
            current_item_layout = QHBoxLayout()

            is_selected_checkbox = QCheckBox()
            current_item_layout.addWidget(is_selected_checkbox)

            current_item_name_label = QLabel()
            current_item_name_label.setText(item['name'])
            current_item_layout.addWidget(current_item_name_label)

            current_item_id_label = QLabel()
            current_item_id_label.setText(item['itemid'])
            current_item_layout.addWidget(current_item_id_label)

            current_item_key_label = QLabel()
            current_item_key_label.setText(item['key_'])
            current_item_layout.addWidget(current_item_key_label)

            current_item_widget.setLayout(current_item_layout)
            self.main_window_items_layout.addWidget(current_item_widget)

        # Вложение элементов друг в друга так, как это было сказано ранее
        main_window_scroll_widget.setLayout(self.main_window_items_layout)
        panel_of_buttons_layout.addWidget(add_item_button)
        panel_of_buttons_layout.addWidget(delete_chosen_items_button)
        main_window_scroll_area.setWidget(main_window_scroll_widget)
        panel_of_buttons_widget.setLayout(panel_of_buttons_layout)
        root_vbox_layout.addWidget(return_button)
        root_vbox_layout.addWidget(main_window_scroll_area)
        root_vbox_layout.addWidget(panel_of_buttons_widget)

    # Функция выполняет возврат обратно к окну хостов
    def return_button_clicked(self):
        window_hosts = WindowNodeWeb(
            self.zabbix, self.action_layout, self.window_menu
        )
        self.window_menu.cur_action_window = window_hosts
        self.action_layout.addWidget(window_hosts)
        WindowApp.close_window(self)

    # Функция открытия окна добавления элемента данных по нажатию на кнопку
    def add_item_button_clicked(self):
        window_add_item = WindowAddItem(
            self.zabbix, self.action_layout, self.window_menu, self.host
        )
        self.window_menu.cur_action_window = window_add_item
        self.action_layout.addWidget(window_add_item)
        WindowApp.close_window(self)

    # Функция удаления элементов данных, которым установлена галочка в чекбоксе
    def delete_chosen_items_button_clicked(self):
        itemids_maybe_checked = {}
        for i in range(self.main_window_items_layout.rowCount()):
            value = self.main_window_items_layout \
                .itemAtPosition(i, 0).widget() \
                .layout().itemAt(0).widget().isChecked()
            key = self.main_window_items_layout \
                .itemAtPosition(i, 0).widget() \
                .layout().itemAt(2).widget().text()
            itemids_maybe_checked[key] = value
        self.items.delete_items(itemids_maybe_checked)
        WindowApp.update_window_on_layout(self, self.action_layout)


# Класс окна добавления нового элемента данных
class WindowAddItem(QDialog):
    def __init__(self, zabbix, action_layout, window_menu, host):
        super().__init__()

        self.setFixedSize(600, 700)
        self.setStyleSheet(open('res/styles/window_add_host.css').read())

        # Создает экземпляр логики хостов
        self.items = Items(zabbix)

        # Создаем экземпляр логики интерфейсов
        self.interfaces = Interfaces(zabbix)

        # API zabbix в сессии
        self.zabbix = zabbix

        # Хост, которому добавляется элемент данных
        self.host = host

        # Текущий центральный лайаут, куда добавляются окна
        self.action_layout = action_layout

        # Ссылка на текущее открытое окно в центральном лайауте
        self.window_menu = window_menu

        # Основной лайаут - вертикальный
        root_vbox_layout = QVBoxLayout(self)

        # Кнопка возврата к окну элементов данных в основном лайауте
        return_button = QPushButton()
        return_button.setIcon(QIcon("res/icon/arrow_back.svg"))
        return_button.setIconSize(QSize(50, 50))

        # Привязка обработки события нажатия на нее
        return_button.clicked.connect(
            lambda: self.return_button_clicked()
        )

        # Поля для заполнения
        self.item_name_field = QLineEdit("pinging")
        # self.item_name_field.setPlaceholderText("Имя нового элемента данных")
        self.key_field = QLineEdit("agent.ping")
        # self.key_field.setPlaceholderText("Ключ элемента данных")
        self.type_field = QLineEdit("0")
        self.value_type_field = QLineEdit("3")
        self.delay_in_s_field = QLineEdit("30")

        # Кнопка добавления
        item_create_button = QPushButton("Добавить")
        item_create_button.clicked.connect(
            lambda: self.item_create_button_clicked()
        )

        root_vbox_layout.addWidget(return_button)

        root_vbox_layout.addWidget(self.item_name_field)
        root_vbox_layout.addWidget(self.key_field)
        root_vbox_layout.addWidget(self.type_field)
        root_vbox_layout.addWidget(self.value_type_field)
        root_vbox_layout.addWidget(self.delay_in_s_field)

        root_vbox_layout.addWidget(item_create_button)

    # Функция выполняет возврат обратно к окну элементов данных
    def return_button_clicked(self):
        window_items = WindowItems(
            self.zabbix, self.action_layout, self.window_menu, self.host
        )
        self.window_menu.cur_action_window = window_items
        self.action_layout.addWidget(window_items)
        WindowApp.close_window(self)

    # Добавление элемента данных и возврат к окну элементов данных
    def item_create_button_clicked(self):
        interfaces = self.interfaces.get_interfaces(self.host)
        self.items.add_item(
            self.host['hostid'],
            interfaces['interfaceid'],
            self.item_name_field.text(),
            self.key_field.text(),
            self.type_field.text(),
            self.value_type_field.text(),
            self.delay_in_s_field.text()
        )
        self.return_button_clicked()


# Класс окна триггеров конкретного хоста
class WindowTriggers(QDialog):
    def __init__(self, zabbix, action_layout, window_menu, host):
        super().__init__()
        self.setFixedSize(600, 700)
        self.setStyleSheet(open('res/styles/window_triggers.css').read())

        # Создаем экземпляр логики триггеров
        self.triggers = Triggers(zabbix)

        # API zabbix в сессии
        self.zabbix = zabbix

        # Текущий хост, к которому привязаны триггеры
        self.host = host

        # Текущий центральный лайаут, куда добавляются окна
        self.action_layout = action_layout

        # Ссылка на текущее открытое окно в центральном лайауте
        self.window_menu = window_menu

        # Основной лайаут - вертикальный
        root_vbox_layout = QVBoxLayout(self)

        # Кнопка возврата к окну хостов в основном лайауте
        return_button = QPushButton()
        return_button.setIcon(QIcon("res/icon/arrow_back.svg"))
        return_button.setIconSize(QSize(50, 50))

        # Привязка обработки события нажатия на нее
        return_button.clicked.connect(lambda: self.return_button_clicked())

        # В основной лайаут добавится зона с прокруткой
        main_window_scroll_area = QScrollArea()

        # Отключаем горизонтальный скролл
        main_window_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        # Включаем динамическое масштабирование
        main_window_scroll_area.setWidgetResizable(
            True
        )
        # Виджет панели с кнопками в основном лайауте
        panel_of_buttons_widget = QWidget()

        # Виджет скролл-окна
        main_window_scroll_widget = QWidget()

        # Лайаут панели с кнопками вставится в ее виджет
        panel_of_buttons_layout = QHBoxLayout()

        # Добавление соответствующих кнопок в лайаут панели
        add_trigger_button = QPushButton("Add")
        add_trigger_button.clicked.connect(
            lambda: self.add_trigger_button_clicked()
        )
        delete_chosen_triggers_button = QPushButton("Delete")
        delete_chosen_triggers_button.clicked.connect(
            lambda: self.delete_chosen_triggers_button_clicked()
        )

        # Основной лайаут scroll area
        self.main_window_triggers_layout = QGridLayout()

        triggers = self.triggers.get_triggers(self.host)

        # Для каждого элемента данных создается виджет и
        # лайаут надписей с информацией
        for trigger in triggers:
            current_trigger_widget = QWidget()
            current_trigger_layout = QHBoxLayout()

            is_selected_checkbox = QCheckBox()
            current_trigger_layout.addWidget(is_selected_checkbox)

            current_trigger_description_label = QLabel()
            current_trigger_description_label.setText(trigger['description'])
            current_trigger_layout.addWidget(current_trigger_description_label)

            current_trigger_id_label = QLabel()
            current_trigger_id_label.setText(trigger['triggerid'])
            current_trigger_layout.addWidget(current_trigger_id_label)

            current_trigger_expression_label = QLabel()
            current_trigger_expression_label.setText(trigger['expression'])
            current_trigger_layout.addWidget(current_trigger_expression_label)

            current_trigger_widget.setLayout(current_trigger_layout)
            self.main_window_triggers_layout.addWidget(current_trigger_widget)

        # Вложение элементов друг в друга так, как это было сказано ранее
        main_window_scroll_widget.setLayout(self.main_window_triggers_layout)
        panel_of_buttons_layout.addWidget(add_trigger_button)
        panel_of_buttons_layout.addWidget(delete_chosen_triggers_button)
        main_window_scroll_area.setWidget(main_window_scroll_widget)
        panel_of_buttons_widget.setLayout(panel_of_buttons_layout)
        root_vbox_layout.addWidget(return_button)
        root_vbox_layout.addWidget(main_window_scroll_area)
        root_vbox_layout.addWidget(panel_of_buttons_widget)

    # Функция выполняет возврат обратно к окну хостов
    def return_button_clicked(self):
        window_hosts = WindowNodeWeb(
            self.zabbix, self.action_layout, self.window_menu
        )
        self.window_menu.cur_action_window = window_hosts
        self.action_layout.addWidget(window_hosts)
        WindowApp.close_window(self)

    # Функция открытия окна добавления триггера по нажатию на кнопку
    def add_trigger_button_clicked(self):
        window_add_trigger = WindowAddTrigger(
            self.zabbix, self.action_layout, self.window_menu, self.host
        )
        self.window_menu.cur_action_window = window_add_trigger
        self.action_layout.addWidget(window_add_trigger)
        WindowApp.close_window(self)

    # Функция удаления триггеров, которым установлена галочка в чекбоксе
    def delete_chosen_triggers_button_clicked(self):
        triggerids_maybe_checked = {}
        for i in range(self.main_window_triggers_layout.rowCount()):
            value = self.main_window_triggers_layout \
                .itemAtPosition(i, 0).widget() \
                .layout().itemAt(0).widget().isChecked()
            key = self.main_window_triggers_layout \
                .itemAtPosition(i, 0).widget() \
                .layout().itemAt(2).widget().text()
            triggerids_maybe_checked[key] = value
        self.triggers.delete_triggers(triggerids_maybe_checked)
        WindowApp.update_window_on_layout(self, self.action_layout)


# Класс окна добавления нового триггера
class WindowAddTrigger(QDialog):
    def __init__(self, zabbix, action_layout, window_menu, host):
        super().__init__()

        self.setFixedSize(600, 700)
        self.setStyleSheet(open('res/styles/window_add_host.css').read())

        # Создает экземпляр логики хостов
        self.triggers = Triggers(zabbix)

        # API zabbix в сессии
        self.zabbix = zabbix

        # Хост, которому добавляется триггер
        self.host = host

        # Текущий центральный лайаут, куда добавляются окна
        self.action_layout = action_layout

        # Ссылка на текущее открытое окно в центральном лайауте
        self.window_menu = window_menu

        # Основной лайаут - вертикальный
        root_vbox_layout = QVBoxLayout(self)

        # Кнопка возврата к окну хостов в основном лайауте
        return_button = QPushButton()
        return_button.setIcon(QIcon("res/icon/arrow_back.svg"))
        return_button.setIconSize(QSize(50, 50))

        # Привязка обработки события нажатия на нее
        return_button.clicked.connect(
            lambda: self.return_button_clicked()
        )

        # Поля для заполнения
        self.trigger_name_field = QLineEdit("host ne ale")
        self.expression_field = QLineEdit(
            "nodata(/bladway-PC/agent.ping, 31s)=1"
        )
        self.priority_field = QLineEdit("5")

        # Кнопка добавления
        trigger_create_button = QPushButton("Добавить")
        trigger_create_button.clicked.connect(
            lambda: self.trigger_create_button_clicked()
        )

        root_vbox_layout.addWidget(return_button)

        root_vbox_layout.addWidget(self.trigger_name_field)
        root_vbox_layout.addWidget(self.expression_field)
        root_vbox_layout.addWidget(self.priority_field)

        root_vbox_layout.addWidget(trigger_create_button)

    # Функция выполняет возврат обратно к окну триггеров
    def return_button_clicked(self):
        window_triggers = WindowTriggers(
            self.zabbix, self.action_layout, self.window_menu, self.host
        )
        self.window_menu.cur_action_window = window_triggers
        self.action_layout.addWidget(window_triggers)
        WindowApp.close_window(self)

    # Добавление хоста и возврат к окну хостов
    def trigger_create_button_clicked(self):
        self.triggers.add_trigger(
            self.trigger_name_field.text(),
            self.expression_field.text(),
            self.priority_field.text()
        )
        self.return_button_clicked()


# Класс активного окна с пользователями
class WindowUsers(QDialog):
    def __init__(self, zabbix, action_layout):
        super().__init__()

        self.setFixedSize(600, 700)
        self.setStyleSheet(open('res/styles/window_users.css').read())

        self.zabbix = zabbix
        self.action_layout = action_layout


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window_login = WindowLogin()
    window_login.show()

    sys.exit(app.exec_())
