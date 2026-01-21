import unittest
from main import factorial

class TestFactorial(unittest.TestCase):
    def test_positive_numbers(self):
        # Тестуємо факторіал для позитивних чисел
        self.assertEqual(factorial(0), 1)
        self.assertEqual(factorial(1), 1)
        self.assertEqual(factorial(5), 120)
        self.assertEqual(factorial(6), 720)

    def test_negative_numbers(self):
        # Тестуємо некоректний ввід (від'ємні числа)
        with self.assertRaises(ValueError):
            factorial(-1)
        with self.assertRaises(ValueError):
            factorial(-10)

    def test_large_numbers(self):
        # Тестуємо факторіал для великих входів
        self.assertEqual(factorial(10), 3628800)

if __name__ == "__main__":
    unittest.main()