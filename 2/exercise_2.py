from enum import Enum
from tkinter import *
import os
import pickle
from copy import copy

CLIENTS_DATABASE_FILE_NAME = 'clients.data'


# Коласс для хранения информации о клиентах
class Client:
    def __init__(self, _name: str, _balance: int):
        self.__name = _name
        self.__balance = _balance

    @property
    def name(self):
        return self.__name

    @property
    def balance(self):
        return self.__balance

    def increase_balance(self, _value: int):
        exception_if_invalid_amount(_value)
        self.__balance += _value

    def decrease_balance(self, _value: int):
        exception_if_invalid_amount(_value)
        self.__balance -= _value


# Проверка на корректность суммы
def exception_if_invalid_amount(_amount):
    if int(_amount) < 0:
        raise ValueError('Сумма должна быть больше 0!')


# Статический класс для управления счетами клиентов
class AccountsManager:
    # Для хранения зарегистрированных клиентов.
    __clients_by_name = {}
    # Для хранения бэкапа клиентов до коммита.
    __clients_backup = {}
    use_database = False

    def __init__(self):
        raise Exception('This is a static class!')

    # Проверяем, существует ли клиент с таким именем
    @classmethod
    def is_client_exists(cls, _name: str):
        return _name in cls.__clients_by_name

    @classmethod
    def load_clients_from_database(cls):
        if cls.use_database and os.path.isfile(CLIENTS_DATABASE_FILE_NAME):
            with open(CLIENTS_DATABASE_FILE_NAME, 'rb') as _file:
                cls.__clients_by_name = pickle.load(_file)

    @classmethod
    def __write_clients_database(cls):
        if cls.use_database:
            with open(CLIENTS_DATABASE_FILE_NAME, 'wb') as _file:
                pickle.dump(cls.__clients_by_name, _file)

    # Закрепляем изменения путем очистки словаря с бэкапом. Откатиться назад больше нельзя.
    @classmethod
    def commit_if_has_changes(cls):
        if cls.__clients_backup:
            cls.__clients_backup = {}
            print('Committed')

            cls.__write_clients_database()
            return True
        else:
            print('No changes to commit')
            return False

    # Откатываем состояние всех затронутых клиентов
    @classmethod
    def rollback(cls):
        for _name, _client in cls.__clients_backup.items():
            cls.__clients_by_name[_name] = _client

        cls.__clients_backup = {}
        print('Reverted')

    # Валидируем имя пользователя и создаем для него счет, если еще не создан
    @classmethod
    def register_new_client(cls, _name: str, _balance: int):
        if ' ' in _name or '\n' in _name:
            return f'Имя пользователя {_name} не должно содержать пробелы!.'

        elif _name in cls.__clients_by_name:
            raise Exception(f'Клиент с именем {_name} уже зарегистрирован!')

        else:
            _new_client = Client(_name, _balance)
            cls.__clients_by_name[_name] = _new_client
            cls.__write_clients_database()

        print(f'Клиент {_name} успешно зарегистрирован.')

    # Пополнение баланса указанного клиента на указанную сумму
    @classmethod
    def deposit(cls, _name: str, _sum: int):
        _sum = int(_sum)
        exception_if_invalid_amount(_sum)

        _client = cls.__get_client_register_if_not_exists(_name)
        cls.__backup_client(_client)
        cls.__deposit(_client, _sum)

        return f'Зачисление {_sum} клиенту {_name}'

    # Списание с баланса клиента указанной суммы
    @classmethod
    def withdraw(cls, _name: str, _sum: int):
        _sum = int(_sum)
        exception_if_invalid_amount(_sum)

        _client = cls.__get_client_register_if_not_exists(_name)
        cls.__backup_client(_client)
        cls.__withdraw(_client, _sum)

        return f'Списание {_sum} у клиента {_name}.'

    # Вывод на экран баланса указанного клиента или всех клиентов
    @classmethod
    def balance(cls, _name=''):
        if _name:
            if _name in cls.__clients_by_name:
                _client = cls.__clients_by_name[_name]
                return f'У клиента {_client.name} баланс {_client.balance}.'
            else:
                return 'NO CLIENT.'
        else:
            _balances = ''

            for _client in cls.__clients_by_name.values():
                _balances += f'У клиента {_client.name} баланс {_client.balance}.\n'

            return _balances.strip()

    # Перевод средств от одного клиента другому
    @classmethod
    def transfer(cls, _name1: str, _name2: str, _sum: int):
        _sum = int(_sum)
        exception_if_invalid_amount(_sum)

        _client1 = cls.__get_client_register_if_not_exists(_name1)
        _client2 = cls.__get_client_register_if_not_exists(_name2)

        cls.__backup_client(_client1)
        cls.__backup_client(_client2)

        cls.__withdraw(_client1, _sum)
        cls.__deposit(_client2, _sum)

        return f'Перевод от клиента {_client1.name} клиенту {_client2.name}. Сумма {_sum}.'

    # Начисление процента от суммы на балансе всем клиентам с положительным балансом
    @classmethod
    def income(cls, _percent: int):
        _log = ''
        _percent = int(_percent)
        exception_if_invalid_amount(_percent)

        for _client in cls.__clients_by_name.values():
            if _client.balance > 0:
                _sum = int(_client.balance * (_percent / 100))
                print(_client.balance * (_percent / 100), _sum)

                cls.__backup_client(_client)
                cls.__withdraw(_client, _sum)
                _log += f'Зачисление {_percent}%/{_sum} клиенту {_client.name}.\n'

        return _log.strip()

    # Можно вызвать этот метод в любом месте транзакции командой TEST_FAIL
    @classmethod
    def test_fail(cls):
        raise Exception("Test exception handling")

    @classmethod
    def __backup_client(cls, _client: Client):
        if _client.name not in cls.__clients_backup:
            cls.__clients_backup[_client.name] = copy(_client)

    # Базовая операция списания без валидации
    @classmethod
    def __withdraw(cls, _client: Client, _sum: int):
        _client.decrease_balance(_sum)

    # Базовая операция зачисления без валидации
    @classmethod
    def __deposit(cls, _client: Client, _sum: int):
        _client.increase_balance(_sum)

    # Возвращаем клиента если он существует, либо регистрируем нового и возвращаем его
    @classmethod
    def __get_client_register_if_not_exists(cls, _name: str):
        if _name in cls.__clients_by_name:
            return cls.__clients_by_name[_name]
        else:
            cls.register_new_client(_name, 0)
            return cls.__clients_by_name[_name]


class Colors(Enum):
    black = 'black'
    white = 'white'


def clear_text_fields(_event):
    global commands_input_field
    global program_output_field
    commands_input_field.delete("1.0", END)
    write_in_output_field('')


def on_calculate_click(_event):
    global commands_input_field

    # Собираем все команды из поля для ввода.
    _input_commands = commands_input_field.get("1.0", END)
    # Удаляем пустые строки и преобразуем строку в список команд с аргументами.
    _input_commands = [x for x in _input_commands.split('\n') if x != '']
    _result_messages = []
    _has_error = False

    # В ТЗ явно не отражено, поэтому было принято решение воспринимать последовательность команд как единую транзакцию
    # и, в случае ошибки, откатывать все измененния, внесенные этими командами.

    # Согласно ТЗ: Количество команд, которые может ввести пользователь за один раз – не более 20.
    if len(_input_commands) > 20:
        _result_messages = ['Максимальное количество команд - 20. Удалите некоторые команды и попробуйте снова.']
        _has_error = True

    else:
        # Перебираем все команды с аргументами из списка.
        for _row in _input_commands:
            # Получаем из строки саму команду и ее аргументы.
            _args = _row.split(' ')
            _command = _args[0]
            del _args[0]

            # Согласно ТЗ: Команды должны вводится только большими буквами.
            if _command != _command.upper():
                _error_message = f'Команды должны вводится только большими буквами! Введено: {_command}'
                _result_messages.append(_error_message)
                _has_error = True
                break

            else:
                # Для вызова метода по имени
                _command = _command.lower()

            # Поскольку в ТЗ было четко прописано что
            # "Предполагается, что пользователь такой системы грамотный и команды с аргументами вводит без ошибок в рамках их вышесформулированного синтаксиса."
            # Дополнительных проверок на существование команд и соответствие аргументов реализовано не будет.
            try:
                # Вызываем метод по иемни и передаем аргументы.
                _result = getattr(AccountsManager, _command)(*_args)

                if isinstance(_result, list):
                    _result_messages += _result
                else:
                    _result_messages.append(_result)

            # В случае, если все же кто-то ошибется, бросаем исключение прямо в лицо.
            except Exception as e:
                print(e.__str__())
                _result_messages.append(e.__str__())
                _has_error = True
                break

        if _has_error:
            AccountsManager.rollback()
            _result_messages.append('[!!!]Операции не были проведены из за ошибки!')
        else:
            # Если коммит прошел, то выдаем сообщение об успехе.
            # Метод вернет False в случае если нет изменений для закрепления.
            if AccountsManager.commit_if_has_changes():
                _result_messages.append('[V]Изменения успешно закрепелены.')

    write_in_output_field('\n'.join(_result_messages))


def write_in_output_field(_text: str):
    global program_output_field
    print(f'Program output:\n{_text}')
    program_output_field.config(state='normal')
    program_output_field.delete("1.0", END)
    program_output_field.insert("1.0", _text)
    program_output_field.config(state='disabled')


# Смена светлой темы на темную и наоборот
def change_theme(_event):
    global is_dark_theme
    is_dark_theme = not is_dark_theme
    update_theme()


# Установка цветов в зависимости от выбранной темы
def update_theme():
    if is_dark_theme:
        _fg_color = Colors.white.value
        _bg_color = Colors.black.value
    else:
        _fg_color = Colors.black.value
        _bg_color = Colors.white.value

    window.configure(background=_bg_color)

    # Перебираем все дочерние элементы окна и устанавливаем цвета для атрибутов, если эти атрибуты есть у элемента
    for _child in window.children.values():
        if 'bg' in _child.keys():
            _child.configure(bg=_bg_color)

        if 'fg' in _child.keys():
            _child.configure(fg=_fg_color)

        if 'insertbackground' in _child.keys():
            _child.configure(insertbackground=_fg_color)


if __name__ == '__main__':
    window = Tk()
    window.title('Potapov-NA Banking')
    window.resizable(False, False)

    # Создаем интерфейс
    input_label = Label(window, text='Commands input:')
    input_label.grid(row=1, column=1, sticky='W', pady=2)

    commands_input_field = Text(window, width=45, height=15, borderwidth=2, font=("Times New Roman", 14), wrap='no')
    commands_input_field.grid(row=2, column=1, sticky='W', columnspan=3)
    input_scrollY = Scrollbar(window, command=commands_input_field.yview, orient=VERTICAL, width=12)
    input_scrollY.grid(row=2, column=4, sticky='NSE', pady=5)
    input_scrollX = Scrollbar(window, command=commands_input_field.xview, orient=HORIZONTAL, width=12)
    input_scrollX.grid(row=3, column=1, sticky='NWE', padx=5, columnspan=3)
    commands_input_field.config(yscrollcommand=input_scrollY.set, xscrollcommand=input_scrollX.set)

    output_label = Label(window, text='Program output:')
    output_label.grid(row=1, column=5, sticky='W', pady=2)
    # Поле для вывода сообщений послеь выполнения программы. Закрыто для редактирования пользователем.
    program_output_field = Text(window, width=45, height=15, borderwidth=2, state='disabled',
                                font=('Times New Roman', 14),
                                wrap='word')
    program_output_field.grid(row=2, column=5, sticky='W', columnspan=3)
    output_scrollY = Scrollbar(window, command=program_output_field.yview, orient=VERTICAL, width=12, troughcolor='red')
    output_scrollY.grid(row=2, column=8, sticky='NSE', pady=5)

    calculate_btn = Button(window, text='Calculate', width=10, height=1, borderwidth=2)
    # Регистрируем обработчик нажатия
    calculate_btn.bind("<Button-1>", on_calculate_click)
    calculate_btn.grid(row=4, column=1, sticky='W', pady=4, padx=2)

    clear_btn = Button(window, text='Clear', width=10, height=1, borderwidth=2)
    # Регистрируем обработчик нажатия
    clear_btn.bind("<Button-1>", clear_text_fields)
    clear_btn.grid(row=4, column=2, sticky='W', pady=4, padx=2)

    change_theme_btn = Button(window, text='Theme', width=5, height=1, borderwidth=2)
    # Регистрируем обработчик нажатия
    change_theme_btn.bind("<Button-1>", change_theme)
    change_theme_btn.grid(row=1, column=7, sticky='E', pady=2, padx=2)

    is_dark_theme = False
    update_theme()

    # Если хочется чтобы клиенты не удалялись после перезапуска программы.
    # В ТЗ не описано, наверное, банк однодневка :)
    _load_clients_database = False

    if _load_clients_database:
        AccountsManager.use_database = True
        AccountsManager.load_clients_from_database()

        if not AccountsManager.is_client_exists('Potapov'):
            AccountsManager.register_new_client('Potapov', 70165405)

    else:
        AccountsManager.register_new_client('Potapov', 70165405)

    window.mainloop()
