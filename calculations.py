"""Среднее №3: свёртка последовательности с помощью reduce."""

from collections.abc import Iterable
from functools import reduce
from operator import add


def require_integer(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("Требуется целое число")


def add_numbers(values: Iterable[int]) -> int:
    """Сумма целых чисел; начальный ноль определяет ответ для пустого ввода."""
    def checked(value: int) -> int:
        require_integer(value)
        return value

    return reduce(add, map(checked, values), 0)
