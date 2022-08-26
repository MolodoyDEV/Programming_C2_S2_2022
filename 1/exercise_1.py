import re

# Объявляем константы
INPUT_FILE_NAME = 'resource_1.txt'
OUTPUT_FILE_NAME = 'result_1.txt'
PUNCTUATION_MARKS_RE = re.compile('[!#$%&\"\'*+-.^_`|~:()\[\]{}]')

if __name__ == '__main__':
    # Читаем входные данные из файла
    with open(INPUT_FILE_NAME, 'r', encoding='UTF-8') as _file:
        _input_data = _file.read().strip()

    # Удаляем пунктуационные символы чтобы оставить только "чистые" слова
    _input_data = PUNCTUATION_MARKS_RE.sub('', _input_data)
    # Создаем список слов
    _input_data = _input_data.split()

    # Записываем уникальные слова в словарь и считаем их количество
    _count_by_word = {}

    for _word in _input_data:
        if _word in _count_by_word:
            _count_by_word[_word] += 1
        else:
            _count_by_word[_word] = 1

    # Получаем из словаря список кортежей (ключ, значение) и сортируем этот список по ключам, которые лежат в кортежах
    _sorted_tuples = sorted(_count_by_word.items(), key=lambda x: x[0])
    # Еще раз сортируем список, но в этот раз по значениям, которые лежат в кортежах
    _sorted_tuples = sorted(_sorted_tuples, key=lambda x: x[1], reverse=True)
    # Формируем список из кортежей, преобразованых в строку
    _output_data = [f'{x} {y}' for x, y in _sorted_tuples]
    # Превращаем список в строку
    _output_data = '\n'.join(_output_data)
    print(_output_data)
    # Пишем в файл
    with open(OUTPUT_FILE_NAME, 'w', encoding='UTF-8') as _file:
        _file.write(_output_data)
