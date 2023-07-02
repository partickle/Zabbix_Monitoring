import sys
import threading

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QLineEdit, \
    QPushButton, QDialog, QMessageBox, QHBoxLayout, QScrollArea, QCheckBox, QWidget, \
    QGridLayout

from pyzabbix import ZabbixAPI, ZabbixAPIException
from app_logic import Terminal, Hosts, Items, Triggers


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
        left_widget = WindowMenu(middle_layout, self.zabbix)
        self.right_widget = WindowTerminal(self.zabbix)

        # Добавление левого, среднего и правого окон в основной лайаут
        main_layout.addWidget(left_widget)
        main_layout.addLayout(middle_layout)
        main_layout.addWidget(self.right_widget)

        # Корректировка "зазоров" между лайаутами
        main_layout.setContentsMargins(0, 0, 0, 0)  # Отступы между краями главного лайаута
        main_layout.setSpacing(0)  # Установка того, что пространство между лайаутом и окном будет 0
        main_layout.setStretch(0, 2)  # Какой лайаут сколько частей занимает
        main_layout.setStretch(1, 4)
        main_layout.setStretch(2, 2)

    # Метод, который при нажатии на крестик окна, выключает таймер и закрывает его
    def closeEvent(self, event):
        self.right_widget.timer_flag = False
        event.accept()


    @staticmethod
    def close_window(window_to_close):
        if window_to_close is not None:
            window_to_close.deleteLater()      


# Класс меню (слева основного окна приложения)
class WindowMenu(QDialog):
    def __init__(self, action_layout, zabbix):
        super().__init__()
        self.zabbix = zabbix
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
        button_logout.clicked.connect(QApplication.closeAllWindows)  # Закрываем все окна, таймер тоже перестанет идти
        quick_layout.addWidget(button_logout)

        # Добавляем на лайаут
        main_layout.addLayout(menu_layout)
        main_layout.addLayout(quick_layout)

    # Метод, который открывает новое окно в активном лайауте.
    # Не теряет состояние текущего окна, если нажать еще раз на кнопку
    def open_window_action(self, name_window):
        if name_window == "window_node_web" and not isinstance(self.cur_action_window, WindowNodeWeb):
            self.close_window_action()
            window_node_web = WindowNodeWeb(self.zabbix, self.action_layout)
            self.action_layout.addWidget(window_node_web)
            self.cur_action_window = window_node_web
        elif name_window == "window_users.css" and not isinstance(self.cur_action_window, WindowUsers):
            self.close_window_action()
            window_users = WindowUsers(self.zabbix, self.action_layout)
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


# Класс окна терминала, в котором будут транслироваться в реальном времени логи zabbix
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
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Отключаем горизонтальный скролл
        scroll_area.setWidgetResizable(True)  # Включаем динамическое масштабирование,
        scroll_area.setWidget(self.label)     # т.к. у нас будет увеличиваться окно

        # Загружаем сначала полный список логов
        self.terminal.log_full_request(self.label)

        # Ставим таймер секунду
        self.timer = threading.Timer(1.0, self.update_terminal)
        self.timer.start()

    # Метод обновления лейбла логов
    def update_terminal(self):
        # Если пришло обновление логов, то отображаем его
        if self.terminal.log_request():
            self.label.setText(self.label.text() + "\n".join(self.terminal.last_checked_str_arr) + "\n")

        # Если флаг таймера True, то...
        if self.timer_flag:
            # Здесь тоже создаем таймер, чтобы его зарекурсировать
            self.timer = threading.Timer(1.0, self.update_terminal)
            self.timer.start()


# Класс активного окна узлов сети
class WindowNodeWeb(QDialog):
    def __init__(self, zabbix, action_layout):
        super().__init__()
        
        self.setFixedSize(600, 700)
        self.setStyleSheet(open('res/styles/window_node_web.css').read())

        self.hosts = Hosts(zabbix)
        self.zabbix = zabbix
        self.action_layout = action_layout
        self.tmp_host = None
        self.simple_buttons_array = []

        root_VBox_layout = QVBoxLayout(self)
        main_window_scroll_area = QScrollArea(self)
        main_window_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Отключаем горизонтальный скролл
        main_window_scroll_area.setWidgetResizable(True)  # Включаем динамическое масштабирование,
        panel_of_buttons_change_widget = QWidget()
        main_window_scroll_widget = QWidget()
        panel_of_buttons_change_layout = QHBoxLayout()
        add_item_button = QPushButton("Add")
        self.simple_buttons_array.append(add_item_button)
        add_item_button.clicked.connect(lambda: self.simple_button_clicked(add_item_button))
        delete_choosen_hosts_button = QPushButton("Delete")
        self.simple_buttons_array.append(delete_choosen_hosts_button)
        delete_choosen_hosts_button.clicked.connect(lambda: self.simple_button_clicked(delete_choosen_hosts_button))
        main_window_items_layout = QGridLayout()
        
        hosts = self.hosts.get_hosts()
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
            
            current_host_items_button = QPushButton('items' + ' ' + str(len(self.hosts.get_items(host))))
            current_item_layout.addWidget(current_host_items_button)
            #current_host_items_button.clicked.connect(lambda: self.items_button_clicked(host)) Очень странно, что строка снизу уже работает, а это - нет
            #current_host_items_button.clicked.connect(lambda state, x=host: self.items_button_clicked(x)) # Этот рабочий код для закоменченного варианта вызываемой функции
            current_host_items_button.clicked.connect(self.items_button_clicked(host)) # Рабочий вариант для текущего варианта вызываемой фукнции

            current_host_triggers_button = QPushButton('triggers' + ' ' + str(len(self.hosts.get_triggers(host))))
            current_item_layout.addWidget(current_host_triggers_button)
            current_host_triggers_button.clicked.connect(self.triggers_button_clicked(host))
            
            current_item_widget.setLayout(current_item_layout)
            main_window_items_layout.addWidget(current_item_widget)    
        

        main_window_scroll_widget.setLayout(main_window_items_layout)
        panel_of_buttons_change_layout.addWidget(add_item_button)
        panel_of_buttons_change_layout.addWidget(delete_choosen_hosts_button)
        main_window_scroll_area.setWidget(main_window_scroll_widget)
        panel_of_buttons_change_widget.setLayout(panel_of_buttons_change_layout)
        root_VBox_layout.addWidget(main_window_scroll_area)
        root_VBox_layout.addWidget(panel_of_buttons_change_widget)

    '''
    def items_button_clicked(self, host):
        window_items = WindowItems(self.zabbix, self.action_layout, host)
        self.action_layout.addWidget(window_items)
        WindowApp.close_window(self) 
    '''

    def items_button_clicked(self, host):
        def button_clicked():
            window_items = WindowItems(self.zabbix, self.action_layout, host)
            self.action_layout.addWidget(window_items)
            WindowApp.close_window(self)
        return button_clicked    

    # Как я понял, здесь мы возвращаем connect-y упакованную функцию button_clicked и выглядит это примерно так: button.clicked.connect(button_clicked)
    # в которую уже упаковано значение host и self-поля, что позволяет корректно привязывать обработку событий

    def triggers_button_clicked(self, host):
        def button_clicked():
            window_triggers = WindowTriggers(self.zabbix, self.action_layout, host)
            self.action_layout.addWidget(window_triggers)
            WindowApp.close_window(self)
        return button_clicked


    def simple_button_clicked(self, button):
        for btn in self.arr:  # Проверяем каждую кнопку
            if btn != button:  # Если она не равна текущей нажатой кнопке,
                btn.setEnabled(True)
        button.setEnabled(False)

      


class WindowItems(QDialog):
    def __init__(self, zabbix, action_layout, host):
        super().__init__()
        self.setFixedSize(600, 700)
        self.setStyleSheet(open('res/styles/window_items.css').read())
        
        self.items = Items(zabbix)
        self.zabbix = zabbix
        self.host = host
        self.action_layout = action_layout
        self.simple_buttons_array = []

        root_VBox_layout = QVBoxLayout(self)        
        return_button = QPushButton()
        return_button.setIcon(QIcon("res/img/return.png"))
        return_button.setIconSize(QSize(50, 50))
        return_button.clicked.connect(lambda: self.return_button_clicked())

        main_window_scroll_area = QScrollArea(self)
        main_window_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Отключаем горизонтальный скролл
        main_window_scroll_area.setWidgetResizable(True)  # Включаем динамическое масштабирование,

        panel_of_buttons_change_widget = QWidget()
        main_window_scroll_widget = QWidget()
        panel_of_buttons_change_layout = QHBoxLayout()

        add_item_button = QPushButton("Add")
        self.simple_buttons_array.append(add_item_button)
        add_item_button.clicked.connect(lambda: self.simple_button_clicked(add_item_button))

        delete_choosen_items_button = QPushButton("Delete")
        self.simple_buttons_array.append(delete_choosen_items_button)
        delete_choosen_items_button.clicked.connect(lambda: self.simple_button_clicked(delete_choosen_items_button))

        main_window_items_layout = QGridLayout()
        
        items = self.items.get_items(self.host)
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
            main_window_items_layout.addWidget(current_item_widget)    

        main_window_scroll_widget.setLayout(main_window_items_layout)
        panel_of_buttons_change_layout.addWidget(add_item_button)
        panel_of_buttons_change_layout.addWidget(delete_choosen_items_button)
        main_window_scroll_area.setWidget(main_window_scroll_widget)
        panel_of_buttons_change_widget.setLayout(panel_of_buttons_change_layout)
        root_VBox_layout.addWidget(return_button)
        root_VBox_layout.addWidget(main_window_scroll_area)
        root_VBox_layout.addWidget(panel_of_buttons_change_widget)
        

    def return_button_clicked(self):
        window_hosts = WindowNodeWeb(self.zabbix, self.action_layout)
        self.action_layout.addWidget(window_hosts)
        WindowApp.close_window(self)
    
    def simple_button_clicked(self, button):
        pass


class WindowTriggers(QDialog):
    def __init__(self, zabbix, action_layout, host):
        super().__init__()
        self.setFixedSize(600, 700)
        self.setStyleSheet(open('res/styles/window_triggers.css').read())
        
        self.triggers = Triggers(zabbix)
        self.zabbix = zabbix
        self.host = host
        self.action_layout = action_layout
        self.simple_buttons_array = []

        root_VBox_layout = QVBoxLayout(self)        
        return_button = QPushButton()
        return_button.setIcon(QIcon("res/img/return.png"))
        return_button.setIconSize(QSize(50, 50))
        return_button.clicked.connect(lambda: self.return_button_clicked())

        main_window_scroll_area = QScrollArea(self)
        main_window_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Отключаем горизонтальный скролл
        main_window_scroll_area.setWidgetResizable(True)  # Включаем динамическое масштабирование,

        panel_of_buttons_change_widget = QWidget()

        main_window_scroll_widget = QWidget()
        panel_of_buttons_change_layout = QHBoxLayout()

        add_trigger_button = QPushButton("Add")
        self.simple_buttons_array.append(add_trigger_button)
        add_trigger_button.clicked.connect(lambda: self.simple_button_clicked(add_trigger_button))

        delete_choosen_triggers_button = QPushButton("Delete")
        self.simple_buttons_array.append(delete_choosen_triggers_button)
        delete_choosen_triggers_button.clicked.connect(lambda: self.simple_button_clicked(delete_choosen_triggers_button))

        main_window_triggers_layout = QGridLayout()
        
        triggers = self.triggers.get_triggers(self.host)
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
            main_window_triggers_layout.addWidget(current_trigger_widget)    

        main_window_scroll_widget.setLayout(main_window_triggers_layout)
        panel_of_buttons_change_layout.addWidget(add_trigger_button)
        panel_of_buttons_change_layout.addWidget(delete_choosen_triggers_button)
        main_window_scroll_area.setWidget(main_window_scroll_widget)
        panel_of_buttons_change_widget.setLayout(panel_of_buttons_change_layout)
        root_VBox_layout.addWidget(return_button)
        root_VBox_layout.addWidget(main_window_scroll_area)
        root_VBox_layout.addWidget(panel_of_buttons_change_widget)
        

    def return_button_clicked(self):
        window_hosts = WindowNodeWeb(self.zabbix, self.action_layout)
        self.action_layout.addWidget(window_hosts)
        WindowApp.close_window(self)
    
    def simple_button_clicked(self, button):
        pass


# Класс активного окна с пользователями
class WindowUsers(QDialog):
    def __init__(self, zabbix, action_layout):
        super().__init__()
        self.setFixedSize(600, 700)
        self.setStyleSheet(open('res/styles/window_users.css').read())


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window_login = WindowLogin()
    window_login.show()

    sys.exit(app.exec_())
