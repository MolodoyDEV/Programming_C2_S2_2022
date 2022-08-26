# Ячеек памяти для 70165405: 9
# Количество строк «цифрового дисплея» для 70165405: 10
# Доп функции для П: Inv, sin, cos, tan

import re
from enum import Enum
from tkinter import Frame, Tk, LEFT, Text, Button, Scrollbar, END, VERTICAL, Label, TOP
import tkinter
from math import sin, cos, tan

# Флаг, указывающий находится ли калькулятор в расширенном режиме или в обычном
is_extended_mode = False
MAX_HISTORY_ROWS = 10
# Компиляция регулярки для валидации возведения в степень.
INVALID_SQRT_EXPRESSION_RE = re.compile('.*-\d{1,}sqrt.*')
# Все числа и знаки в поле для ввода представлены в виде списка, например ['53', '+', '1']
current_input_expression = ['0']


# Перечисление доступных типов кнопок
class ButtonActionType(Enum):
    save = 'MS'
    read = 'MR'
    clear = 'MC'
    plus = 'M+'
    minus = 'M-'


# Статический класс для взаимодействия с ячейками памяти
class Memory:
    MEMORY_CELLS_COUNT = 9
    # Ячейки памяти, MEMORY_CELLS_COUNT штук
    __memory_cells_by_index = {x: '0' for x in range(0, MEMORY_CELLS_COUNT)}
    # Списки кнопок для работы с ячейками памяти по их типу
    __memory_buttons_by_action = {
        ButtonActionType.plus: [],
        ButtonActionType.minus: [],
        ButtonActionType.clear: [],
        ButtonActionType.read: [],
        ButtonActionType.save: []
    }

    def __init__(self):
        raise Exception('This is a static class!')

    @classmethod
    def append_button(cls, _action_type: ButtonActionType, _button: tkinter.Button):
        # Кнопка будет прикреплена к ячейке памяти с тем же индеком, что в списке cls.__memory_buttons_by_action[_action_type]
        # Здесь важна правильная последовательность добавления кнопок при создании UI.
        cls.__memory_buttons_by_action[_action_type].append(_button)

    # Найти ячейку памяти по кнопке. Необходимо, чтобы при нажатии на кнопку понять с какой ячейкой памяти производятся дейтсвия
    @classmethod
    def get_memory_cell_index(cls, _search_button: tkinter.Button):
        _action_type = ButtonActionType(_search_button.cget("text"))
        _clicked_button_index = 0

        while _clicked_button_index < len(cls.__memory_buttons_by_action[_action_type]):
            _button = cls.__memory_buttons_by_action[_action_type][_clicked_button_index]

            if _button is _search_button:
                return _clicked_button_index

            else:
                _clicked_button_index += 1

        raise Exception(f'Memory cell for button {_search_button.__repr__()} not found!')

    # Записать значения в ячейку с индеском _index
    @classmethod
    def write_cell(cls, _index: int, _value):
        _value = str(_value)

        if _value.replace('.', '').replace('-', '').isdigit():
            cls.__memory_cells_by_index[_index] = _value
        else:
            raise ValueError(f'Invalid {_value} numeric value')

    # Прочитать значения из ячейки с индексом _index
    @classmethod
    def read_cell(cls, _index: int):
        return cls.__memory_cells_by_index[_index]


# Перечисление доступных операций
class MathOperation(Enum):
    sin = 'sin'
    cos = 'cos'
    tan = 'tan'


# Рекурсия для подсчета суммы всех чисел пока не останется одно
def calculate_all_numbers_sum(_value) -> int:
    _value = str(_value)

    if len(_value) > 1:
        return calculate_all_numbers_sum(sum([int(x) for x in _value]))
    else:
        return int(_value)


def calculate_cos(_value: float):
    return cos(_value)


def calculate_sin(_value: float):
    return sin(_value)


def calculate_tan(_value: float):
    return tan(_value)


# Получения функции, реализующей операцию по ее типу
FUNCTION_BY_OPERATION = {
    MathOperation.sin: calculate_sin,
    MathOperation.cos: calculate_cos,
    MathOperation.tan: calculate_tan
}


# region Обработчики нажатий на кнопки
# Переключение между обычным и расширенным режимом.
def toggle_calculator_mode(_event):
    global is_extended_mode
    is_extended_mode = not is_extended_mode

    if is_extended_mode:
        window.title('Калькулятор. Расширенный режим.')
        extension_frame.pack(side=TOP)

    else:
        window.title('Калькулятор. Обычный режим.')
        extension_frame.pack_forget()


# Обработчик нажатия на кнопку CE
def on_ce_pressed(_event):
    global current_input_expression

    if current_input_expression:
        # Удаляем из поля для ввода последнее введенное число или знак
        del current_input_expression[-1]

        # Если в результате поле осталось пустым, то пишем ноль.
        if not current_input_expression:
            current_input_expression = ['0']

        update_input_field_view()


# Обработчик нажатия на кнопку C
def on_c_pressed(_event):
    global current_input_expression
    current_input_expression = ['0']
    update_input_field_view()
    append_to_history_field('C')


# Обработчик нажатия кнопки =
def on_enter_pressed(_event):
    global current_input_expression
    # Получаем значения из поля для ввода, отсекая одинокие символы справа
    _user_input = ''.join(current_input_expression).rstrip('(+-./*')
    # Результат вычисления в числовом представлении
    _digit_result = 0

    if not _user_input:
        return

    if INVALID_SQRT_EXPRESSION_RE.match(_user_input):
        # Результат вычисления в виде ошибки
        _result = 'Invalid sqrt expression'

    else:
        # Подготавливаем значение из поля для ввода, формируя корректное выражение для python
        _expression = _user_input.replace('^', '**').replace('sqrt', '**(0.5)').replace(' ', '')

        try:
            # Само вычисление значения выражения было решено сделать на основе функции eval.
            # Оглядываясь назад, я бы сделал иначе.. В итоге подпер костылями и поехало.
            _result = eval(_expression)

            # Отбрасываем точку в случае если в результате тип float вида 12.0
            if int(_result) - _result == 0:
                _result = int(_result)

            _digit_result = _result

        except ZeroDivisionError:
            _result = 'Zero division error'

        except Exception as e:
            _result = 'Invalid operation'
            print(e.__str__())

    print(_user_input, '=', _result)

    # Добавляем в историю результат в текстовом представлении. Это может быть цифра или сообщение об ошибке.
    append_to_history_field(f'{_user_input}\n=\n{_result}')
    # В поле для ввода возвращаем результат в числовом представлении. 0 при ошибке.
    write_in_input_field(str(_digit_result))


# Обработчик нажатия кнопки с символами 0-9.+-()/*
def on_char_button_pressed(_event):
    append_to_input_field(_event.widget.cget("text"))


# Обработка нажатия на любую кнопку для работы с ячейками памяти
def on_memory_button_pressed(_event):
    # Получаем саму кнопку, которая была ажата
    _pressed_button = _event.widget
    # По тексту на кнопке получаем ее тип
    _action_type = ButtonActionType(_pressed_button.cget("text"))
    # Затем обращаемся к памяти для поиска ячейки памяти, к которой привязана эта кнопка
    _memory_cell_index = Memory.get_memory_cell_index(_pressed_button)
    print(f'Pressed {_action_type.name}/{_action_type.value} button in column {_memory_cell_index + 1}')

    # Далее действуем в зависимости от типа нажатой кнопки
    if _action_type == ButtonActionType.clear:
        Memory.write_cell(_memory_cell_index, '0')

    elif _action_type == ButtonActionType.save:
        on_enter_pressed(None)
        _current_value = get_input_field_value() if get_input_field_value() else '0'
        Memory.write_cell(_memory_cell_index, get_input_field_value())

    elif _action_type == ButtonActionType.plus:
        # Записываем текущее значение из поля для ввода в ячейку памяти если в ячейке памяти 0
        if Memory.read_cell(_memory_cell_index) == '0':
            _current_value = get_input_field_value() if get_input_field_value() else '0'
            on_enter_pressed(None)
            Memory.write_cell(_memory_cell_index, get_input_field_value())

        # Подставляем значение из памяти в выражение в поле для ввода
        append_to_input_field('+')
        append_to_input_field(Memory.read_cell(_memory_cell_index))
        # Нажимаем на кнопку = для проведения расчета и записи истории штатным образом
        on_enter_pressed(None)

    elif _action_type == ButtonActionType.read:
        append_to_input_field(Memory.read_cell(_memory_cell_index))

    elif _action_type == ButtonActionType.minus:
        # Записываем текущее значение из поля для ввода в ячейку памяти если в ячейке памяти 0
        if Memory.read_cell(_memory_cell_index) == '0':
            _current_value = get_input_field_value() if get_input_field_value() else '0'
            on_enter_pressed(None)
            Memory.write_cell(_memory_cell_index, _current_value)

        # Подставляем значение из памяти в выражение в поле для ввода
        append_to_input_field('-')
        append_to_input_field(Memory.read_cell(_memory_cell_index))
        # Нажимаем на кнопку = для проведения расчета и записи истории штатным образом
        on_enter_pressed(None)

    else:
        raise ValueError(f'Unexpected action type {_action_type}')


# Обработчик нажатия на кнопку <>. Суммирует все цифры в поле для ввода пока не останется одна
def sum_all_numbers(_event):
    # Жмем = на случай если в поле для ввода в данной момент какое-то выражение.
    # В таком случае операция будет произведена над результатом этого выражения.
    on_enter_pressed(None)
    _input = get_input_field_value()
    _input = str(int(float(_input))).lstrip('-')

    _result = calculate_all_numbers_sum(_input)

    write_in_input_field(str(_result))
    append_to_history_field(f'{"+".join(_input)}...\n=\n{str(_result)}')


# Обработчик нажатия на кнопки sin, cos, tan
def on_sin_cos_tan_pressed(_event):
    # Выполняемая операци определяется на основании подписи кнопки
    _operation = MathOperation(_event.widget.cget("text"))
    on_enter_pressed(None)
    _current_value = get_input_field_value()

    try:
        # Получаем нужную функцию по типу операции
        _result = FUNCTION_BY_OPERATION[_operation](float(_current_value))
        write_in_input_field(str(_result))

    except ValueError as e:
        # В случае ошибки в математической функции пишем ее в историю
        _result = e.__str__()
        write_in_input_field('0')

    append_to_history_field(f'{_operation.value}({_current_value})\n=\n{str(_result)}')


# endregion

# Запись текста в текстовое поле, которое заблокированно для ввода пользователем
def write_in_blocked_field(_text: str, _field):
    _field.config(state='normal')
    _field.delete("1.0", END)
    # Применяем тэг, по которому происходит выравнивание текста по правому краю
    _field.insert("1.0", _text, 'tag-right')
    _field.config(state='disabled')


# Перезаписать историю новыми данными
def write_in_history_field(_text: str):
    global calculator_history_field
    write_in_blocked_field(_text, calculator_history_field)


# Перезаписать поле для ввода новыми данными. Запись происходит через список current_input_expression,
# а UI обновляется в update_input_field_view()
def write_in_input_field(_text: str):
    global current_input_expression

    if _text:
        current_input_expression = [_text]
    else:
        current_input_expression = ['0']

    update_input_field_view()


# Обновление тексового поля для ввода нв UI
def update_input_field_view():
    global current_input_expression
    write_in_blocked_field(''.join(current_input_expression), calculator_input_field)
    print(current_input_expression)


# Добавить значение к уже существующим в поле для ввода
def append_to_input_field(_text: str):
    global current_input_expression

    # Если поле для ввода не пустое и хотят добавить точку, то добавляем
    if current_input_expression and _text == '.':
        current_input_expression[-1] += _text

    # Если поле для ввода не пустое и хотят добавить цифру, в предыдущим знаком была тоже цифра, то...
    elif current_input_expression and \
            _text.isdigit() and \
            current_input_expression[-1].replace('-', '').replace('.', '').isdigit():

        # Если последнее введенное число было 0, то заменяем его, чтобы числа не начинались с нуля.
        # Например: ['8', '-', '0'] после добавления 2 будет ['8', '-', '2'], а вот ['8', '-', '20'] под условие не попадет.
        if current_input_expression[-1] == '0':
            current_input_expression[-1] = _text

        # Иначе добавляем к последнему введенному числу еще одну цифру.
        # Например: ['8', '-', '20'] после добавления 2 будет ['8', '-', '202']
        else:
            current_input_expression[-1] += _text

    # Иначе просто добавляем как новый элемент списка.
    # В данному случае у нас либо рядом два знака, либо число и знак.
    # Либо список пустой, но такого быть не должно, должен подставляться 0.
    else:
        current_input_expression.append(_text)

    update_input_field_view()


# Добавляем к существующей истории новые строки.
def append_to_history_field(_text: str):
    global calculator_history_field
    _current_history = calculator_history_field.get("1.0", END)
    _new_history = f'{_text}\n{_current_history}'
    _history_rows = _new_history.split('\n')

    # Если строк больше допустимого, то обрезаем лишнее.
    if len(_history_rows) > MAX_HISTORY_ROWS:
        _history_rows = _history_rows[0:MAX_HISTORY_ROWS]
        _new_history = '\n'.join(_history_rows)

    write_in_history_field(_new_history)


# Получаем текст из поля для ввода выражения.
def get_input_field_value():
    return calculator_input_field.get("1.0", END).strip().replace(' ', '')


# region Создание GUI.
if __name__ == '__main__':
    window = Tk()
    window.title('Калькулятор. Обычный режим.')
    window.resizable(False, False)

    base_frame = Frame(window)
    base_frame.pack(side=LEFT)

    # Поле для ввода.
    calculator_input_field = Text(base_frame, width=30, height=1, font=("Times New Roman", 14), wrap='no',
                                  state='disabled')
    calculator_input_field.tag_configure('tag-right', justify='right')
    calculator_input_field.grid(row=1, column=1, sticky='WN', columnspan=4)

    # Экран истории со скролл баром.
    calculator_history_field = Text(base_frame, width=30, height=8, font=("Times New Roman", 14), wrap='word',
                                    state='disabled')
    calculator_history_field.tag_configure('tag-right', justify='right')
    calculator_history_field.grid(row=2, column=1, sticky='WN', columnspan=4, rowspan=5)
    input_scrollY = Scrollbar(base_frame, command=calculator_history_field.yview, orient=VERTICAL, width=12)
    input_scrollY.grid(row=2, column=5, sticky='NSE', pady=5, rowspan=5)
    calculator_history_field.config(yscrollcommand=input_scrollY.set)

    # Кнопки базовых символов для ввода.
    _row = 8
    _column = 1
    _i = 0
    # Итерируемся по списку кнопок. Список представляет из себя развернутую панель ввода калькулятора.
    for _char in ['(', ')', 'sqrt', '^', '7', '8', '9', '*', '4', '5', '6', '/', '1', '2', '3', '+', '.', '0', '', '-']:

        # В списке могут быть пустые строки для того чтобы оставить пропуски между кнопкми
        if _char:
            char_button = Button(base_frame, text=_char, width=3, height=1)
            char_button.bind("<Button-1>", on_char_button_pressed)
            char_button.grid(row=_row, column=_column, sticky='W', pady=2, padx=2)

        _i += 1
        # Смещаемся на ряд вниз каждые 4 итерации.
        if not _i % 4:
            _row += 1
            _column = 1
        else:
            _column += 1

    # Создаем специфические кнопки с отдельными обработчиками.
    # Кнопка равно.
    enter_button = Button(base_frame, text='=', width=3, height=1, bg='green')
    enter_button.bind("<Button-1>", on_enter_pressed)
    enter_button.grid(row=12, column=3, sticky='W', pady=2, padx=2)

    # Кнопка <> для вычисления суммы всех цифр числа до последнего.
    delete_last_symbol = Button(base_frame, text='<>', width=3, height=1, bg='red')
    delete_last_symbol.bind("<Button-1>", sum_all_numbers)
    delete_last_symbol.grid(row=7, column=3, sticky='W', pady=2, padx=2)

    # Кнопка CE для удаления последнего введенного символа или числа.
    delete_last_symbol = Button(base_frame, text='CE', width=3, height=1, bg='red')
    delete_last_symbol.bind("<Button-1>", on_ce_pressed)
    delete_last_symbol.grid(row=7, column=2, sticky='W', pady=2, padx=2)

    # Кнопка C для очистки поля ввода.
    delete_all_symbols = Button(base_frame, text='C', width=3, height=1, bg='red')
    delete_all_symbols.bind("<Button-1>", on_c_pressed)
    delete_all_symbols.grid(row=7, column=1, sticky='W', pady=2, padx=2)

    # Кнопка для переключения между обычным и расширенным режимом калькулятора.
    change_mode_btn = Button(base_frame, text='===', width=3, height=1, bg='yellow')
    change_mode_btn.bind("<Button-1>", toggle_calculator_mode)
    change_mode_btn.grid(row=7, column=4, sticky='W', pady=2, padx=2)

    # Рамку для расширенного режима не упаковываем pack(), чтобы она не отображалась сразу при запуске.
    extension_frame = Frame(window)

    # Построчно создаем кнопки для ячеек памяти
    for _i in range(1, Memory.MEMORY_CELLS_COUNT + 1):
        buttons_row = []
        buttons_frame = Frame(extension_frame, bg='blue')
        buttons_frame.grid(row=_i, column=1, padx=2, pady=2, columnspan=6)

        buttons_row.append(Button(buttons_frame, text=ButtonActionType.save.value, width=3, height=1))
        buttons_row.append(Button(buttons_frame, text=ButtonActionType.plus.value, width=3, height=1))
        buttons_row.append(Button(buttons_frame, text=ButtonActionType.minus.value, width=3, height=1))
        buttons_row.append(Button(buttons_frame, text=ButtonActionType.clear.value, width=3, height=1))
        buttons_row.append(Button(buttons_frame, text=ButtonActionType.read.value, width=3, height=1))

        # Проходимся по только созданной строке кнопок и биндим эвент для каждой кнопки
        # А так же регистрируем каждую кнопку в классе Memory
        for _col in range(1, 6):
            _button = buttons_row[_col - 1]
            _button.bind("<Button-1>", on_memory_button_pressed)
            buttons_row[_col - 1].grid(row=_i, column=_col, sticky='W', pady=2, padx=2)

            _action_type = ButtonActionType(_button.cget("text"))
            Memory.append_button(_action_type, _button)

        label = Label(buttons_frame, text=_i, width=1, height=1, bg='blue', font=("Times New Roman", 14), fg='white')
        label.grid(row=_i, column=6, sticky='W', pady=2, padx=2)

    sin_button = Button(extension_frame, text='sin', width=5, height=2, bg='yellow')
    sin_button.bind("<Button-1>", on_sin_cos_tan_pressed)
    sin_button.grid(row=13, column=1, sticky='W', pady=2)

    cos_button = Button(extension_frame, text='cos', width=5, height=2, bg='yellow')
    cos_button.bind("<Button-1>", on_sin_cos_tan_pressed)
    cos_button.grid(row=13, column=2, sticky='W', pady=2)

    tan_button = Button(extension_frame, text='tan', width=5, height=2, bg='yellow')
    tan_button.bind("<Button-1>", on_sin_cos_tan_pressed)
    tan_button.grid(row=13, column=3, sticky='W', pady=2)

    label = Label(extension_frame, text='*measured in radians', height=1,
                  font=("Times New Roman", 10), fg='black')
    label.grid(row=14, column=1, sticky='W', pady=2, padx=2, columnspan=3)

    # В первую ячейку памяти заранее записываю свой ID для удобства
    Memory.write_cell(0, 70165405)
    update_input_field_view()
    window.mainloop()
# endregion
