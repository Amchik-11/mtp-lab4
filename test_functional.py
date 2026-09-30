"""Проверки функциональных решений и запуска примеров."""

from itertools import islice
import os
from pathlib import Path
import random
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from calculations import add_numbers
from currying import curry_three, reading_volume
from streams import fibonacci_numbers, numbers_in_range, sensor_data


class SumChecks(unittest.TestCase):
    def test_values(self):
        for data, expected in [([], 0), ([12, 8, -3, 5], 22), ([-9], -9)]:
            saved = data.copy()
            self.assertEqual(add_numbers(data), expected)
            self.assertEqual(data, saved)

    def test_iterator(self):
        self.assertEqual(add_numbers(i * 2 for i in range(5)), 20)

    def test_invalid(self):
        for value in (True, 2.5, "3"):
            with self.assertRaises(TypeError):
                add_numbers([value])


class StreamChecks(unittest.TestCase):
    def test_fibonacci_prefix(self):
        self.assertEqual(list(fibonacci_numbers(8)), [0, 1, 1, 2, 3, 5, 8, 13])
        self.assertEqual(list(fibonacci_numbers(0)), [])
        self.assertEqual(list(fibonacci_numbers(1)), [0])

    def test_resume_and_exhaustion(self):
        stream = fibonacci_numbers(5)
        self.assertEqual(next(stream), 0)
        self.assertEqual(list(islice(stream, 2)), [1, 1])
        self.assertEqual(list(stream), [2, 3])
        with self.assertRaises(StopIteration):
            next(stream)

    def test_fibonacci_recurrence(self):
        values = list(fibonacci_numbers(50))
        for position in range(2, 50):
            expected = values[position - 2] + values[position - 1]
            self.assertEqual(values[position], expected)

    def test_invalid_sizes(self):
        for size in (-1, True, 2.5):
            streams = (fibonacci_numbers(size), numbers_in_range(1, 3, size))
            for stream in streams:
                with self.assertRaises((ValueError, TypeError)):
                    next(stream)

    def test_random_bounds_and_seed(self):
        values = list(numbers_in_range(-2, 6, 100, 3))
        self.assertEqual(len(values), 100)
        self.assertTrue(all(-2 <= value <= 6 for value in values))
        self.assertEqual(values, list(numbers_in_range(-2, 6, 100, 3)))
        reference = random.Random(3)
        self.assertEqual(values, [reference.randint(-2, 6) for _ in values])

    def test_random_edge_cases(self):
        self.assertEqual(list(numbers_in_range(4, 4, 3)), [4, 4, 4])
        self.assertEqual(list(numbers_in_range(1, 3, 0)), [])
        with self.assertRaises(ValueError):
            next(numbers_in_range(3, 1, 2))
        with self.assertRaises(TypeError):
            next(numbers_in_range(True, 3, 2))

    def test_sensor_continues(self):
        stream = sensor_data(10)
        sample = list(islice(stream, 500))
        self.assertEqual([row["sequence"] for row in sample],
                         list(range(1, 501)))
        self.assertTrue(all(-10 <= row["temperature"] <= 35 for row in sample))
        self.assertTrue(all(0 <= row["humidity"] <= 100 for row in sample))
        self.assertEqual(next(stream)["sequence"], 501)

    def test_sensor_repeatability(self):
        left = sensor_data(7)
        right = sensor_data(7)
        for _ in range(20):
            self.assertEqual(next(left), next(right))

    def test_sensor_returns_new_objects(self):
        stream = sensor_data(7)
        first = next(stream)
        first["humidity"] = -999
        second = next(stream)
        self.assertIsNot(first, second)
        self.assertGreaterEqual(second["humidity"], 0)

    def test_global_random_untouched(self):
        state = random.getstate()
        list(numbers_in_range(1, 9, 20, 4))
        list(islice(sensor_data(5), 20))
        self.assertEqual(state, random.getstate())


class CurryingChecks(unittest.TestCase):
    def test_reading_example(self):
        self.assertEqual(curry_three(reading_volume)(5)(20)(2), 90)
        self.assertEqual(reading_volume(5, 20, 2), 90)

    def test_partial_functions_are_reusable(self):
        first = curry_three(lambda a, b, c: a + b + c)(10)
        second = first(20)
        self.assertEqual(second(1), 31)
        self.assertEqual(second(2), 32)
        self.assertEqual(first(30)(4), 44)

    def test_deferred_execution(self):
        calls = []

        def record(a, b, c):
            calls.append((a, b, c))
            return a * b * c

        two = curry_three(record)(2)(3)
        self.assertEqual(calls, [])
        self.assertEqual(two(4), 24)
        self.assertEqual(calls, [(2, 3, 4)])

    def test_strings(self):
        join = curry_three(lambda prefix, word, suffix: prefix + word + suffix)
        self.assertEqual(join("[")("книга")("]"), "[книга]")

    def test_invalid_callable_and_arity(self):
        with self.assertRaises(TypeError):
            curry_three(3)
        with self.assertRaises(TypeError):
            curry_three(lambda a: a)(1)(2)(3)
        with self.assertRaises(TypeError):
            curry_three(reading_volume)(1, 2)


class LaunchChecks(unittest.TestCase):
    def execute(self, *arguments):
        script = Path(__file__).resolve().parent / "main.py"
        with TemporaryDirectory() as folder:
            return subprocess.run(
                [sys.executable, str(script), *arguments], cwd=folder,
                timeout=10, capture_output=True, text=True, encoding="utf-8",
                env=dict(os.environ, PYTHONIOENCODING="utf-8"),
            )

    def test_default_finishes(self):
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stderr)
        for text in ("reduce: 22", "F5 = 5", "5 * (20 - 2) = 90",
                     "'sequence': 6"):
            self.assertIn(text, result.stdout)

    def test_custom_and_zero(self):
        result = self.execute("--example", "sum", "--numbers", "-10", "3")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("reduce: -7", result.stdout)
        result = self.execute("--size", "0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("'sequence':", result.stdout)

    def test_invalid_input(self):
        for arguments in (("--size", "-1"), ("--start", "9", "--stop", "1"),
                          ("--numbers", "text")):
            result = self.execute(*arguments)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
