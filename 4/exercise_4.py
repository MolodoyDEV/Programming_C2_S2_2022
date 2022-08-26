import datetime
import random
from collections import namedtuple
from tkinter import Tk, Entry, Button, Canvas, Label, StringVar
import copy

# Константы
ID = '70165405'
TOTAL_DISKS_COUNT = sum([int(x) for x in ID])
DEFAULT_PROGRESS_PERCENTS = (ID[0:2], ID[2:4], ID[4:6], ID[6:8])

# Именованный кортеж для хранения информации о диске
Disk = namedtuple('Disk', ('color', 'size'))
DISK_HEIGHT = 15
PILLARS_COUNT = 8
PILLAR_WIDTH = 6
PILLAR_HEIGHT = 350
STAND_HEIGHT = 15
CANVAS_SIZE = (1200, 500)
PILLARS_OFFSET = (CANVAS_SIZE[0] - CANVAS_SIZE[0] / PILLARS_COUNT) / PILLARS_COUNT

# Подсчет количества итераций алгоритма ханойских башен
total_disks_moves = 0


# Статический класс для переключения и записи итераций алгоритма ханойских башен
class IterationsManager:
    # В историю сохраняется положение всех дисков на каждой итерации.
    # Выглядит одна запись в истории так: {1: [Disk], 2:[Disk].... 8[Disk]} где цифра - номер шпинделя
    __disks_positions_history = [{}]
    __current_iteration = 0
    __total_iterations_count = 0

    def __init__(self):
        raise Exception('This is a static class!')

    # Общее количество итерация
    @classmethod
    def total_iterations_count(cls) -> int:
        return len(cls.__disks_positions_history) - 1

    # Текущая выбранная итерация
    @classmethod
    def current_iteration_number(cls) -> int:
        return cls.__current_iteration

    # Текущее расположение дисков на шпинделях на текущей выбранной итерации
    @classmethod
    def current_disks_positions_by_pillar(cls) -> dict:
        return cls.__disks_positions_history[cls.current_iteration_number()]

    # Выбрать итерация с номером _iteration_number
    @classmethod
    def select_iteration(cls, _iteration_number: int):
        if 0 > _iteration_number < cls.__total_iterations_count:
            raise Exception(f"Iteration {_iteration_number} not present")

        cls.__current_iteration = _iteration_number

    # Выбрать самую последнюю итерацию из истории
    @classmethod
    def select_last_iteration(cls):
        cls.__current_iteration = len(cls.__disks_positions_history) - 1

    # Выбрать следующую по счетку итерацию в истории
    @classmethod
    def select_next_iteration(cls):
        if cls.__current_iteration + 1 >= len(cls.__disks_positions_history):
            raise StopIteration

        cls.__current_iteration += 1

    # Выбрать предыдущую по счетку итерацию в истории
    @classmethod
    def select_previous_iteration(cls):
        if cls.__current_iteration - 1 < 0:
            raise StopIteration

        cls.__current_iteration -= 1

    # Добавить еще одну итерацию в историю. Необходимо в момент расчета алгоритма ханойских башен для сохранения истории
    @classmethod
    def create_and_select_new_iteration(cls):
        cls.__current_iteration = cls.total_iterations_count() + 1
        _previous_iteration = cls.__disks_positions_history[cls.__current_iteration - 1]
        # cls.__disks_positions_history.append(copy.deepcopy(_previous_iteration)) # работало дольше в 10 раз
        _previous_iteration = {x: copy.copy(y) for x, y in
                               _previous_iteration.items()}  # _previous_iteration = {1: [Disk], 2:[Disk], 3[Disk]....} где цифра - номер шпинделя
        cls.__disks_positions_history.append(_previous_iteration)


# Необходимо вычислить, за какое минимальное количество итераций переместятся все диски на шпиндель номер 1 по следующим
# правилам:
# а) За одну итерацию можно переместить не более одного диска
# б) Диски можно класть только с большего на меньший
# в) Со шпинделя номер 8 можно перекладывать диски только на
# шпиндели 7 и 6
# г) Со шпинделя номер 1 можно перекладывать диски только на
# шпиндели номер 2 и 3
# д) Со шпинделей от 2 по 7 можно перекладывать диски только на
# два соседних шпинделя
def move_all_disks_and_write_history():
    # Рекурсивная функция для переноса дисков с одного шпинделя на другой через третий
    def move_disks(_disks_count, _from, _to, _via):
        global total_disks_moves

        # Одна итерация движения диска
        def move_iteration():
            global total_disks_moves
            if _disks_count <= 0:
                return

            if _from == _to or _from == _via or _to == _via:
                raise Exception(f"Такой перенос невозможен! from:{_from} to:{_to} via:{_via}")

            if 1 > _from > PILLARS_COUNT or 1 > _to > PILLARS_COUNT or 1 > _via > PILLARS_COUNT:
                raise Exception(f"Выход за диапазон допустимых значений! from:{_from} to:{_to} via:{_via}")

            if _from == 1:
                if (_from + 2) < _to or (_from + 2) < _via:
                    raise Exception(
                        f"Со шпинделя номер 1 можно перекладывать диски только на шпиндели 2 и 3! from:{_from} to:{_to} via:{_via}")
            elif _from == 8:
                if _to < (_from - 2) or _via < (_from - 2):
                    raise Exception(
                        f"Со шпинделя номер 8 можно перекладывать диски только на шпиндели 7 и 6! from:{_from} to:{_to} via:{_via}")

            # Создаем новую итерацию в истории
            IterationsManager.create_and_select_new_iteration()
            # Снимаем диск со шпидлея
            _disk_to_move = IterationsManager.current_disks_positions_by_pillar()[_from].pop(-1)

            if IterationsManager.current_disks_positions_by_pillar()[_to]:
                if _disk_to_move.size > IterationsManager.current_disks_positions_by_pillar()[_to][-1].size:
                    raise Exception("Большой диск нельзя класть на маленький!")

            # Надеваем диск на другой шпиндель
            IterationsManager.current_disks_positions_by_pillar()[_to].append(_disk_to_move)
            total_disks_moves += 1

        if _disks_count == 0:
            return

        if _disks_count == 1:
            move_iteration()
            return

        move_disks(_disks_count - 1, _from, _via, _to)
        move_iteration()
        move_disks(_disks_count - 1, _via, _to, _from)

    def move_from_left_to_right():
        _len = len(IterationsManager.current_disks_positions_by_pillar()[3])
        move_disks(_len, 3, 4, 2)
        move_disks(_len, 4, 5, 3)
        move_disks(_len, 5, 6, 4)

        _len = len(IterationsManager.current_disks_positions_by_pillar()[4])
        move_disks(_len, 4, 3, 5)
        move_disks(_len, 3, 2, 4)
        move_disks(_len, 2, 1, 3)

        _len = len(IterationsManager.current_disks_positions_by_pillar()[6])
        move_disks(_len, 6, 5, 7)
        move_disks(_len, 5, 4, 6)
        move_disks(_len, 4, 3, 5)

    print('Processing disk movement..')
    # 10919 итераций.
    # С помощью инструкции return можно остановиться в любом месте и посмотреть как выглядят столбы с дисками.
    # Собираем диски в несколько кучек и сдвигаем их в правую сторону, ближе к первому столбу.
    move_disks(len(IterationsManager.current_disks_positions_by_pillar()[1]), 1, 2, 3)
    move_disks(len(IterationsManager.current_disks_positions_by_pillar()[2]), 2, 1, 3)

    move_disks(len(IterationsManager.current_disks_positions_by_pillar()[3]), 3, 4, 2)
    move_disks(len(IterationsManager.current_disks_positions_by_pillar()[4]), 4, 3, 5)
    move_disks(len(IterationsManager.current_disks_positions_by_pillar()[3]), 3, 2, 4)

    move_disks(len(IterationsManager.current_disks_positions_by_pillar()[5]), 5, 6, 4)
    move_disks(len(IterationsManager.current_disks_positions_by_pillar()[6]), 6, 5, 7)
    move_disks(len(IterationsManager.current_disks_positions_by_pillar()[5]), 5, 4, 6)
    move_disks(len(IterationsManager.current_disks_positions_by_pillar()[4]), 4, 3, 5)

    move_disks(len(IterationsManager.current_disks_positions_by_pillar()[7]), 7, 8, 6)
    move_disks(len(IterationsManager.current_disks_positions_by_pillar()[8]), 8, 6, 7)
    move_disks(len(IterationsManager.current_disks_positions_by_pillar()[6]), 6, 5, 7)
    move_disks(len(IterationsManager.current_disks_positions_by_pillar()[5]), 5, 4, 6)

    # Начинаем перебрасывать самые маленькие диски за самые большие
    _len = len(IterationsManager.current_disks_positions_by_pillar()[1])
    move_disks(_len, 1, 3, 2)
    move_disks(_len, 3, 4, 2)
    move_disks(_len, 4, 5, 3)
    move_disks(_len, 5, 6, 4)
    move_disks(_len, 6, 7, 5)
    move_disks(_len, 7, 8, 6)

    _len = len(IterationsManager.current_disks_positions_by_pillar()[2])
    move_disks(_len, 2, 3, 1)
    move_disks(_len, 3, 4, 2)
    move_disks(_len, 4, 5, 3)
    move_disks(_len, 5, 6, 4)
    move_disks(_len, 6, 7, 5)

    _len = len(IterationsManager.current_disks_positions_by_pillar()[3])
    move_disks(_len, 3, 4, 2)
    move_disks(_len, 4, 5, 3)
    move_disks(_len, 5, 6, 4)

    # Перекладываем самые большие диски на первый столб.
    _len = len(IterationsManager.current_disks_positions_by_pillar()[4])
    move_disks(_len, 4, 3, 5)
    move_disks(_len, 3, 2, 4)
    move_disks(_len, 2, 1, 3)

    # Освобождаем место для перемещения остальных 3х кучек слева направо.
    _len = len(IterationsManager.current_disks_positions_by_pillar()[8])
    move_disks(_len, 8, 6, 7)
    move_disks(_len, 6, 5, 7)
    move_disks(_len, 5, 4, 6)
    move_disks(_len, 4, 3, 5)

    _len = len(IterationsManager.current_disks_positions_by_pillar()[7])
    move_disks(_len, 7, 8, 6)

    _len = len(IterationsManager.current_disks_positions_by_pillar()[6])
    move_disks(_len, 6, 5, 7)
    move_disks(_len, 5, 4, 6)

    # Переносим кучки направо
    move_from_left_to_right()

    _len = len(IterationsManager.current_disks_positions_by_pillar()[8])
    move_disks(_len, 8, 6, 7)
    move_disks(_len, 6, 5, 7)
    move_disks(_len, 5, 4, 6)

    move_from_left_to_right()

    move_disks(_len, 3, 2, 4)
    move_disks(_len, 2, 1, 3)
    print("Done!")


def show_next_iteration(_event):
    try:
        IterationsManager.select_next_iteration()
        redraw_disks()
    except StopIteration:
        print('This is the last iteration!')
        error_label_text.set('This is the last iteration!')


def show_previous_iteration(_event):
    try:
        IterationsManager.select_previous_iteration()
        redraw_disks()
    except StopIteration:
        print('This is the first iteration!')
        error_label_text.set('This is the first iteration!')


def show_end_of_iterations(_event):
    IterationsManager.select_last_iteration()
    redraw_disks()


def show_start_of_iterations(_event):
    IterationsManager.select_iteration(0)
    redraw_disks()


# Показываем промежуточную терацию по проценту
def show_intermediate_iteration(_event, _percent):
    _percent = _percent.get()
    print('Percent', _percent)
    if _percent.replace('.', '').isdigit():
        _percent = float(_percent)
        if _percent > 100:
            error_label_text.set(f'Invalid percent value! Percent must be between 0 and 100, got {_percent}')
            print(f'-Invalid percent value! Percent must be between 0 and 100, got {_percent}')
        else:
            _requested_iteration = (IterationsManager.total_iterations_count() / 100) * _percent
            _requested_iteration = round(_requested_iteration, 3)

            if int(_requested_iteration) - _requested_iteration == 0:
                _requested_iteration = int(_requested_iteration)

            elif int(_requested_iteration.__ceil__()) > IterationsManager.total_iterations_count():
                _requested_iteration = int(_requested_iteration)

            print('-Requested iteration', _requested_iteration)

            IterationsManager.select_iteration(_requested_iteration)
            redraw_disks()

    else:
        print(f'-Invalid percent value! {_percent}')
        error_label_text.set(f'Invalid percent value! Expected digits, got {_percent}')


# Перерисовываем все диски на экране в соответствии с их положением на выбранной итерации
def redraw_disks():
    # Удаляем все нарисованные диски
    canvas.delete('disks')
    error_label_text.set('')
    # Выводим номер выбранной итерации на экран
    current_iteration_text.set(IterationsManager.current_iteration_number())

    # Если выбрана промежуточная итерация, то тут будет кортеж: перемещаемый диск и две позиции, откуда и куда он перемещается
    _flying_disk_and_position = None

    if isinstance(IterationsManager.current_iteration_number(), float):
        # Получаем номера соседних целых итераций
        _first_iteration = IterationsManager.current_iteration_number().__floor__()
        _second_iteration = IterationsManager.current_iteration_number().__ceil__()

        # Выбираем первую итерацию и получаем расположение дисков на ней
        IterationsManager.select_iteration(_first_iteration)
        _fist_iteration_disks_state = IterationsManager.current_disks_positions_by_pillar()

        # Выбираем вторую итерацию и получаем расположение дисков на ней
        IterationsManager.select_iteration(_second_iteration)
        _second_iteration_disks_state = IterationsManager.current_disks_positions_by_pillar()
        _positions = []
        _flying_disk = None

        # Проходимся циклом по первой итерации и сравниваем ее со второй. Ищем диск, который был перемещен
        _i = 1
        while _i < len(_fist_iteration_disks_state):

            # Ищем шпиндели, диски на которых откличаются. Таких должно быть два
            if _fist_iteration_disks_state[_i] != _second_iteration_disks_state[_i]:
                if not _flying_disk:
                    # Диск, который был перемещен, будет в разнице между шпинделем откуда и шпинделем куда
                    _flying_disk = list(
                        set(_fist_iteration_disks_state[_i]).difference(set(_second_iteration_disks_state[_i])))
                _positions.append(_i)

            _i += 1

        if not _flying_disk:
            raise Exception(
                f"Не удалось найти перемещенный диск на итерации {IterationsManager.current_iteration_number()}")

        else:
            # Наконец создаем кортеж
            _flying_disk_and_position = (_flying_disk[0], *_positions)

    # Проходимся по всем шпинделям на выбранной целой итерации, не важно floor или ceil
    for _pillar, _disks in IterationsManager.current_disks_positions_by_pillar().items():

        # Проходимся по всем дискам на шпинделе
        _i = 1
        while _i <= len(_disks):
            _disk = _disks[_i - 1]

            # Если диск соответствует диску, который был перемещен на дробной итерации, то изображаем его в воздухе
            # Сравнение производим по рамеру т.к он уникален
            if _flying_disk_and_position and _disk.size == _flying_disk_and_position[0].size:
                _first_position = _flying_disk_and_position[1]
                _second_position = _flying_disk_and_position[2]

                # Высчитываем где должен находиться летающий диск
                _flying_disk_center = PILLARS_OFFSET * (
                        PILLARS_COUNT - ((_first_position + _second_position) / 2) + 1)
                _flying_disk_height = CANVAS_SIZE[1] - 400 - DISK_HEIGHT

                # Рисуем линии от диска до шпинделей
                canvas.create_line(_flying_disk_center, _flying_disk_height,
                                   PILLARS_OFFSET * (PILLARS_COUNT - _first_position + 1) + PILLAR_WIDTH / 2,
                                   CANVAS_SIZE[1] - STAND_HEIGHT - DISK_HEIGHT,
                                   fill=_disk.color, tags='disks', dash=2, width=5)

                canvas.create_line(_flying_disk_center, _flying_disk_height,
                                   PILLARS_OFFSET * (PILLARS_COUNT - _second_position + 1) + PILLAR_WIDTH / 2,
                                   CANVAS_SIZE[1] - STAND_HEIGHT - DISK_HEIGHT,
                                   fill=_disk.color, tags='disks', dash=2, width=5)

                # Задаем параметры для рисования дискаы
                _pillar_center = _flying_disk_center
                _disk_height = _flying_disk_height

            else:
                # Задаем параметры для рисования дискаы
                _pillar_center = PILLARS_OFFSET * (PILLARS_COUNT - _pillar + 1) + PILLAR_WIDTH / 2
                _disk_height = CANVAS_SIZE[1] - STAND_HEIGHT - DISK_HEIGHT * _i

            # Рисуем диск
            canvas.create_rectangle(_pillar_center - _disk.size / 2,
                                    _disk_height,
                                    _pillar_center + _disk.size / 2,
                                    _disk_height + DISK_HEIGHT,
                                    fill=_disk.color, tags='disks')

            # Пишем размер диска на самом диске
            canvas.create_text((_pillar_center, _disk_height + DISK_HEIGHT / 2),
                               text=_disk.size, font=("Times New Roman", 10), fill='white', tags='disks')
            _i += 1


# region Создание GUI.
if __name__ == '__main__':
    window = Tk()
    window.title('Ханойские башни на максималках.')

    # Создаем канвас
    canvas = Canvas(window, width=CANVAS_SIZE[0], height=CANVAS_SIZE[1], bg='pink')

    # Рисуем шпиндели
    for _pillar_position in range(1, PILLARS_COUNT + 1):
        _pillar_number = PILLARS_COUNT + 1 - _pillar_position
        # Задаем начальное количество дисков на шпинделе по ID
        _disks_on_pillar_count = int(ID[_pillar_number - 1])
        IterationsManager.current_disks_positions_by_pillar()[_pillar_number] = []

        # Создаем диски и сохраняем их текущую позицию как начальную
        for _i in range(0, _disks_on_pillar_count):
            _disk_width = _pillar_number * 10 + (_disks_on_pillar_count - _i)

            # Создаем конкретный диск и добавляем в историю. Цвет диска выбирается случайно
            IterationsManager.current_disks_positions_by_pillar()[_pillar_number].append(
                Disk("#" + ("%06x" % random.randint(0, 16777215)), _disk_width))

        _canvas_width = PILLARS_OFFSET * _pillar_position

        # Сам шпиндель
        canvas.create_rectangle(_canvas_width,
                                CANVAS_SIZE[1] - PILLAR_HEIGHT,
                                _canvas_width + PILLAR_WIDTH,
                                CANVAS_SIZE[1],
                                fill="brown")

    # Подложка под шпинделями
    canvas.create_rectangle(0, CANVAS_SIZE[1] - STAND_HEIGHT, CANVAS_SIZE[0], CANVAS_SIZE[1], fill="brown", )

    # Нумеруем шпиндели от 8 до 1 слева направо
    for _pillar_position in range(1, PILLARS_COUNT + 1):
        _pillar_number = PILLARS_COUNT + 1 - _pillar_position
        _canvas_width = PILLARS_OFFSET * _pillar_position
        canvas.create_text((_canvas_width + PILLAR_WIDTH / 2, CANVAS_SIZE[1] - 7),
                           text=_pillar_number, font=("Times New Roman", 12, 'bold'), fill='yellow')

    canvas.grid(row=2, column=1, padx=4, pady=4, rowspan=7, columnspan=8)

    error_label_text = StringVar(value='')
    error_label = Label(window, width=5, font=("Times New Roman", 14), fg='red', textvariable=error_label_text)
    error_label.grid(row=1, column=1, sticky='EW', padx=10, pady=20, columnspan=8)

    # Создаем поля для ввода промежуточных итераций и кнопки под ними
    _iterations = 0
    for _i in range(3, 7):
        _text = StringVar(value=DEFAULT_PROGRESS_PERCENTS[_iterations])
        _iterations += 1
        _progress_input = Entry(window, width=5, font=("Times New Roman", 14), textvariable=_text)
        _progress_input.grid(row=9, column=_i, sticky='EW', padx=10, pady=2)

        _progress_select_bth = Button(window, text=f'П.{_iterations}', width=5)
        # При нажатии на кнопку вызываем функцию show_intermediate_iteration, передавая в нее ячейку с введенным прогрессом
        _progress_select_bth.bind("<Button-1>",
                                  lambda event, arg=_progress_input: show_intermediate_iteration(event, arg))
        _progress_select_bth.grid(row=10, column=_i, sticky='EW', padx=10, pady=2)

    to_start_button = Button(window, text='Начало', width=15)
    to_start_button.bind("<Button-1>", show_start_of_iterations)
    to_start_button.grid(row=9, column=2, sticky='EW', padx=10, pady=2, rowspan=2)

    to_end_button = Button(window, text='Окончание', width=15)
    to_end_button.bind("<Button-1>", show_end_of_iterations)
    to_end_button.grid(row=9, column=7, sticky='EW', padx=10, pady=2, rowspan=2)

    previous_button = Button(window, text='<<', width=5)
    previous_button.bind("<Button-1>", show_previous_iteration)
    previous_button.grid(row=11, column=3, sticky='EW', padx=10, pady=20)

    next_button = Button(window, text='>>', width=5)
    next_button.bind("<Button-1>", show_next_iteration)
    next_button.grid(row=11, column=4, sticky='EW', padx=10, pady=20)

    current_iteration_text = StringVar(value=0)
    _current_iteration_label = Label(window, width=10, font=("Times New Roman", 14),
                                     textvariable=current_iteration_text)
    _current_iteration_label.grid(row=1, column=2, sticky='N')
    _current_iteration_label_text = Label(window, text='Итерация:', font=("Times New Roman", 14))
    _current_iteration_label_text.grid(row=1, column=1, sticky='N')

    _start_time = datetime.datetime.now()

    # Запускаем алгоритм для расчета и сохранения всех движений дисков из начального состояния в конечное
    move_all_disks_and_write_history()

    # Тест 1: 0.171038 sec
    # Тест 2: 0.083018 sec
    # Тест 3: 0.08602 sec
    print('Elapsed seconds on loading', (datetime.datetime.now() - _start_time).total_seconds())

    # Показываем начальное состояние дисков при старте программы
    show_start_of_iterations(None)

    print('Total iterations', total_disks_moves)
    window.mainloop()
