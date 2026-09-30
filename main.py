"""Примеры функционального программирования, вариант 3."""

import argparse
from itertools import islice

from calculations import add_numbers
from currying import curry_three, reading_volume
from streams import fibonacci_numbers, numbers_in_range, sensor_data


def main() -> None:
    parser = argparse.ArgumentParser(description="ЛР №4 — Морозова Анастасия")
    parser.add_argument(
        "--example",
        choices=("all", "sum", "fib", "random", "curry", "sensor"),
        default="all",
    )
    parser.add_argument("--size", type=int, default=6)
    parser.add_argument("--start", type=int, default=10)
    parser.add_argument("--stop", type=int, default=30)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument(
        "--numbers", type=int, nargs="*", default=[12, 8, -3, 5]
    )
    args = parser.parse_args()
    if args.size < 0:
        parser.error("Количество должно быть неотрицательным")
    if args.example in ("all", "random") and args.start > args.stop:
        parser.error("Начало диапазона больше конца")

    print("Морозова Анастасия Алексеевна, группа 221341, вариант 3, ЛР №4")
    if args.example in ("all", "sum"):
        print("\nСреднее №3 — reduce:", add_numbers(args.numbers))
    if args.example in ("all", "fib"):
        print("\nСреднее №5 — генератор Фибоначчи:")
        for position, value in enumerate(fibonacci_numbers(args.size), 1):
            print(f"F{position - 1} = {value}")
    if args.example in ("all", "random"):
        print("\nСреднее №9 — числа в диапазоне:")
        values = numbers_in_range(args.start, args.stop, args.size, args.seed)
        print(list(values))
    if args.example in ("all", "curry"):
        print("\nПовышенное №3 — каррирование:")
        per_five_sessions = curry_three(reading_volume)(5)
        per_twenty_pages = per_five_sessions(20)
        print("5 * (20 - 2) =", per_twenty_pages(2))
        print("Повторное использование, 5 * (20 - 4) =", per_twenty_pages(4))
        print("Прямой вызов:", reading_volume(5, 20, 2))
    if args.example in ("all", "sensor"):
        print("\nПовышенное №7 — фрагмент бесконечного потока:")
        for item in islice(sensor_data(args.seed), args.size):
            print(item)


if __name__ == "__main__":
    main()
