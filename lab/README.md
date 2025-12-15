# Лабораторна робота №1
## Тестування, Unit-тести, Mock-об'єкти

### Метою роботи було:
- Вивчити основи unit-тестування на Python
- Опанувати бібліотеки unittest та pytest
- Навчитися використовувати coverage для аналізу покриття коду
 
---

## 1. Вступ - Assert та валідація

На початку ми вивчили механізм `assert` для перевірки умов.

### Що таке assert?
`assert` — це оператор перевірки твердження. Якщо умова хибна, викидається виключення.

Використання:
```python
assert умова, "Повідомлення про помилку"
```

### Практичні приклади

Приклад №1 - валідація у file_module.py:
```python
def get_n_random_words(n: int) -> list:
    if n > len(INITIAL_WORDS):
        print("Неможливо згенерувати стільки слів.")
        raise ValueError("Кількість слів перевищує доступну.")
    elif not isinstance(n, int):
        print("Введено некоректне значення для кількості слів.")
        raise ValueError("n має бути додатним цілим числом.")
    elif n <= 0:
        print("Кількість слів має бути додатним цілим числом.")
        raise ValueError("n має бути додатним цілим числом.")
    else:
        print(f"Генерація {n} випадкових слів.")
    return [w.lower() for w in random.sample(INITIAL_WORDS, n)]
```

Приклад №2 - валідація у main.py:
```python
def check_letters_in_word(letters: Set[str], word: str) -> str:
    if word == "":
        raise ValueError("Слово не має бути порожнім")
    if not isinstance(word, str):
        raise TypeError("Слово має бути рядком")
    if len(letters) == 0:
        raise ValueError("Буква не має бути порожньою")
    if letters - set(string.ascii_lowercase):
        raise ValueError("Літери мають бути латинськими")
    return "".join([l if l in letters else "*" for l in word])
```

### Застосування у нашому проекті

Валідація була застосована для:
- Перевірки українських символів у вводі (у main.py перевіряються латинські букви)
- Контролю списків слів (не порожні, правильні типи даних)
- Перевірки довжини слова для гри

---

## 2. Написання Unit-тестів з unittest

Unit-тести — це тести окремих компонентів програми.

### Основні поняття unittest

`unittest` — вбудована бібліотека Python для тестування:
- `TestCase` — базовий клас для тестових класів
- `setUp()` — виконується перед кожним тестом
- `tearDown()` — виконується після кожного тесту  
- `setUpClass()` — виконується один раз перед усіма тестами
- Методи асерції: `assertEqual()`, `assertTrue()`, `assertRaises()`

### Наша система тестування

Файл: [test_main.py](tests/test_main.py)

Ми створили 4 тестові класи:

**TestWordChoice** — тестування вибору слова:
```python
class TestWordChoice(unittest.TestCase):
    def test_word_in_list(self):
        word = choose_secret_word(WORDS)
        self.assertIn(word, WORDS)

    def test_word_is_string(self):
        word = choose_secret_word(WORDS)
        self.assertIsInstance(word, str)

    def test_word_length(self):
        word = choose_secret_word(WORDS)
        self.assertGreater(len(word), 0)
        self.assertLessEqual(len(word), 20)

    def test_word_not_numeric(self):
        word = choose_secret_word(WORDS)
        self.assertFalse(word.isdigit())

    def test_word_not_empty(self):
        word = choose_secret_word(WORDS)
        self.assertNotEqual(word, "")

    def test_empty_list(self):
        with self.assertRaises(IndexError):
            choose_secret_word([])
```

**TestEnterLetterFromUser** — тестування вводу букв:
```python
class TestEnterLetterFromUser(unittest.TestCase):
    @patch("builtins.input", side_effect=["1", "a"])
    def test_enter_letter_from_user(self, mock_input):
        self.assertEqual(enter_letter_from_user(), "1")
        self.assertEqual(enter_letter_from_user(), "a")
```

**TestCheckLettersInWord** — найдетальніший тест:
Тестування функції пошуку букв у слові:
```python
class TestCheckLettersInWord(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.empty_test_word = ""

    def setUp(self):
        letters_to_guess = set("abcdefghijklmnopqrstuvwxyz")
        self.test_word = "".join(
            random.choices(list(letters_to_guess), k=random.randint(3, 8))
        )
        self.guess_letters = letters_to_guess
        self.no_letters = set()

    def tearDown(self):
        self.test_word = None
        self.guess_letters = None
        self.no_letters = None

    def test_user_entered_cyrillic_letter(self):
        with self.assertRaises(ValueError):
            check_letters_in_word({"а", "б", "в"}, self.test_word)
        result = check_letters_in_word({"a", "b", "c"}, self.test_word)
        self.assertIsInstance(result, str)

    def test_all_letters_guessed(self):
        test_word = "apple"
        self.assertEqual(check_letters_in_word(set(test_word), test_word), test_word)

    def test_no_letters_guessed(self):
        with self.assertRaises(ValueError):
            check_letters_in_word(set(), "banana")

    def test_some_letters_guessed(self):
        self.assertEqual(check_letters_in_word({"a", "n"}, "banana"), "*anana")

    def test_repeated_letters(self):
        self.assertEqual(check_letters_in_word({"b", "a"}, "banana"), "ba*a*a")

    def test_valid_interface_arguments(self):
        for arg in [123, 12.5, None]:
            with self.assertRaises(TypeError):
                check_letters_in_word(self.guess_letters, arg)

    def test_empty_word(self):
        guess_letters = set(["a", "b"])
        with self.assertRaises(ValueError):
            check_letters_in_word(self.guess_letters, self.empty_test_word)

    def test_empty_letters(self):
        with self.assertRaises(ValueError):
            check_letters_in_word(self.no_letters, self.test_word)
```

**TestCheckIfWordGuessed** — тестування перевірки завершення:
```python
class TestCheckIfWordGuessed(unittest.TestCase):
    def setUp(self):
        self.test_word = "test"
        self.all_letters = set(self.test_word)
        self.partial_letters = {"t", "e"}
        self.no_letters = set()
        self.extra_letters = set("testzxy")

    def test_word_fully_guessed(self):
        self.assertTrue(check_if_word_guessed(self.all_letters, self.test_word))

    def test_word_partially_guessed(self):
        self.assertFalse(check_if_word_guessed(self.partial_letters, self.test_word))

    def test_no_letters_guessed(self):
        self.assertFalse(check_if_word_guessed(self.no_letters, self.test_word))

    def test_extra_letters_guessed(self):
        self.assertTrue(check_if_word_guessed(self.extra_letters, self.test_word))
```

### Як запустити unittest тести

```bash
# Запуск всіх тестів в проекті
python -m unittest discover -s tests -v

# Запуск тестів з конкретного файлу
python -m unittest tests.test_main -v

# Запуск конкретного класу
python -m unittest tests.test_main.TestWordChoice -v

# Запуск конкретного тесту
python -m unittest tests.test_main.TestWordChoice.test_word_in_list -v
```

### Додаткові тести функцій

Також є функціональні тести які не входять в класи:

```python
def test_module_import():
    assert isinstance(func_for_module_import(), str)

def test_func_check_if_word_guessed():
    with patch("builtins.print") as mock_print:
        result = check_if_word_guessed({"a", "b", "c"}, "abc")
        mock_print.assert_called_with("Ви вгадали букву !")
        assert result is True
```

---

## 3. PyTest — Інноваційний Підхід до Тестування

### Встановлення та налаштування

```bash
pip install pytest
```

### Порівняння unittest та pytest

| Критерій | unittest | pytest |
|----------|----------|--------|
| Архітектура | Класи з спадкуванням від TestCase | Звичайні функції |
| Способи асерції | Методи типу `self.assertEqual()` | Прямий оператор `assert` |
| Фікстури | `setUp()` та `tearDown()` | Декоратор `@pytest.fixture` |
| Команда запуску | `python -m unittest` | `pytest` |

### Структура тестів на Pytest

Файл: [test_file_module.py](tests/test_file_module.py)

**Тест 1:** Перевірка кількості слів
```python
def test_get_n_random_words():
    """
    Перевіряємо що функція повертає потрібну кількість слів
    """
    for n in range(1, 6):
        words = get_n_random_words(n)
        assert len(words) == n, f"Expected {n} words, got {len(words)}"
```

**Тест 2:** Перевірка обробки помилок
```python
def test_get_n_random_words_raise_value_error():
    """
    Перевіряємо що функція правильно обробляє невалідні аргументи
    """
    invalid_inputs = [-1, 0, 1.5, 2.5, 50]
    for n in invalid_inputs:
        with pytest.raises(ValueError):
            get_n_random_words(n)
```

**Тест 3:** Перевірка виводу функції
```python
def test_get_n_random_words_expect_print_outputs():
    """
    Перевіряємо правильність виводу функції
    """
    with patch("builtins.print") as mock_print:
        for n in range(1, 6):
            get_n_random_words(n)
            mock_print.assert_called_with(f"Генерація {n} випадкових слів.")
```

### Як запустити pytest тести

```bash
# Запуск всіх тестів у проекті
pytest -v

# Запуск тестів з конкретного файлу
pytest tests/test_file_module.py -v

# Запуск конкретного тестового методу
pytest tests/test_file_module.py::test_get_n_random_words -v

# Запуск з детальною інформацією про помилки
pytest -vv --tb=long
```

---

## 4. Mock об'єкти та техніка мокування

Mock об'єкти — це об'єкти що імітують поведінку інших об'єктів. Це дозволяє тестувати код без залежностей від зовнішніх систем.

### Приклади з проекту

#### Мокування input()
```python
@patch("builtins.input", side_effect=["1", "a"])
def test_enter_letter_from_user(self, mock_input):
    self.assertEqual(enter_letter_from_user(), "1")
    self.assertEqual(enter_letter_from_user(), "a")
```

#### Мокування print()
```python
def test_func_check_if_word_guessed():
    with patch("builtins.print") as mock_print:
        result = check_if_word_guessed({"a", "b", "c"}, "abc")
        mock_print.assert_called_with("Ви вгадали букву !")
        assert result is True
```

Декоратор `@patch` замінює функцію на Mock об'єкт, який можна інспектувати та контролювати під час тесту.

---

## 5. Coverage — Аналіз Покриття Коду

### Концепція покриття

Покриття коду — це метрика що показує скільки відсотків вихідного коду виконується під час запуску тестів.

Типи покриття:
- **Line Coverage** — скільки рядків коду було виконано
- **Branch Coverage** — скільки гілок (if/else) було протестовано

### Встановлення необхідних пакетів

```bash
pip install coverage pytest-cov
```

### Способи генерації звітів про покриття

**Способ 1: Використання coverage**
```bash
# Запуск тестів з збиранням даних про покриття
coverage run -m pytest

# Вивід звіту в консоль
coverage report

# Генерація детального HTML звіту
coverage html
```

**Способ 2: Використання pytest-cov**
```bash
# Запуск з параметром покриття
pytest --cov=lab -v

# Генерація HTML звіту
pytest --cov=lab --cov-report=html -v
```

---

## 6. Структура проекту

```
lab/
├── main.py                    # Гра для вгадування слів
├── file_module.py             # Генерація випадкових слів
├── tests/
│   ├── test_main.py          # unittest тести
│   ├── test_file_module.py    # pytest тести
│   └── __init__.py
├── pyproject.toml            # Налаштування проекту
├── 1.ipynb                    # Jupyter notebook
└── README.md
```

---

## 7. Висновки та Результати

### Виконані завдання

1. **Введення в assert та валідацію**
   - Реалізована валідація у двох файлах проекту
   - Розглянуто практичні приклади у функціях
   - Розуміння концепції та сфер застосування

2. **Unit-тестування з unittest**
   - Розроблено 4 тестові класи
   - Написано більше 15 тестових методів
   - Використовано `setUp()`/`tearDown()` та техніку мокування з `@patch`

3. **Unit-тестування з pytest**
   - Написано 3 функціональні тести
   - Застосовано обробку винятків через `pytest.raises()`
   - Досягнуто високої читабельності коду

4. **Аналіз покриття коду (Coverage)**
   - Встановлено бібліотеки `coverage` та `pytest-cov`
   - Навичка генерування звітів про покриття
   - Розуміння важливості покриття коду

### Опановані навички

- ✅ Механізм assert та обробка винятків в Python
- ✅ Структура unittest: TestCase, методи setUp/tearDown, асерції
- ✅ Сучасний підхід з pytest: функції, асерти, обробка помилок
- ✅ Mock-об'єкти та техніка патчування функцій
- ✅ Аналіз line coverage та branch coverage
- ✅ Практична організація тестів у реальному проекті

### Загальна оцінка роботи

**Статус: Виконано успішно!**

Усі поставлені завдання реалізовані. Здобуто комплексні знання в області автоматичного тестування та аналізу якості коду, які є необхідними для професійної розробки програмного забезпечення.
