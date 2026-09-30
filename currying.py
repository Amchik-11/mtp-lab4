"""Повышенное №3: каррирование функции трёх аргументов."""

from collections.abc import Callable
from typing import Any


def curry_three(function: Callable[..., Any]) -> Callable:
    """Преобразовать function(a, b, c) в цепочку (a)(b)(c).

    Обёртка рассчитана на три позиционных аргумента. Совместимость
    сигнатуры и допустимость значений проверяет исходная функция
    при последнем вызове. Ранние этапы сохраняют аргументы в замыканиях.
    """
    if not callable(function):
        raise TypeError("Передайте вызываемую функцию")

    def first(a: Any) -> Callable:
        def second(b: Any) -> Callable:
            def third(c: Any) -> Any:
                return function(a, b, c)
            return third
        return second
    return first


def reading_volume(sessions: int, pages: int, skipped: int) -> int:
    """Пример: число занятий * (страницы за занятие - пропущенные страницы)."""
    return sessions * (pages - skipped)
