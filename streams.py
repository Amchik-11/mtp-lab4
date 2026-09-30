"""Задания на генераторы: Фибоначчи, числа и бесконечные данные."""

from collections.abc import Iterator
import random

from calculations import require_integer


def check_size(size: int) -> None:
    require_integer(size)
    if size < 0:
        raise ValueError("Количество не может быть отрицательным")


def fibonacci_numbers(size: int) -> Iterator[int]:
    """Среднее №5: лениво выдать size чисел, начиная с 0 и 1."""
    check_size(size)
    pair = (0, 1)
    for _ in range(size):
        yield pair[0]
        pair = (pair[1], pair[0] + pair[1])


def numbers_in_range(
    start: int, stop: int, size: int, seed: int | None = None,
) -> Iterator[int]:
    """Среднее №9: size случайных целых чисел, обе границы включены."""
    require_integer(start)
    require_integer(stop)
    check_size(size)
    if start > stop:
        raise ValueError("Начало диапазона больше конца")
    source = random.Random(seed)
    remaining = size
    while remaining:
        yield source.randrange(start, stop + 1)
        remaining -= 1


def sensor_data(seed: int | None = None) -> Iterator[dict]:
    """Повышенное №7: бесконечный поток случайных показаний датчика.

    Температура: от -10 до 35 градусов, влажность: от 0 до 100 процентов.
    Каждый элемент — новый словарь; состояние random локально генератору.
    """
    source = random.Random(seed)
    sequence = 0
    while True:
        sequence += 1
        yield {
            "sequence": sequence,
            "temperature": round(source.uniform(-10, 35), 1),
            "humidity": source.randint(0, 100),
        }
