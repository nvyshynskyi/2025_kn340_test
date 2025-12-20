# Звіт до лабораторної роботи №2

## Тема: Автоматизація з GitHub Actions та CI/CD

![CI Pipeline](https://img.shields.io/badge/GitHub%20Actions-Automated-blue) ![Status](https://img.shields.io/badge/status-complete-success)

---

## Вступ

На цій лабораторній роботі я ознайомився з GitHub Actions — потужним інструментом для автоматизації тестування та розгортання. Завдання включало створення workflow файлів, налаштування різноманітних тригерів та інтеграцію з системами контролю якості коду.

---

## 1. Теоретичні основи GitHub Actions

### Що таке GitHub Actions?

GitHub Actions — це вбудована платформа безперервної інтеграції (CI) та доставки (CD), яка дозволяє автоматизувати будь-який етап розробки прямо у вашому репозиторії GitHub.

### Архітектура та основні компоненти:

| Компонент | Опис |
|-----------|------|
| **Workflow** | YAML файл (`.github/workflows/`) з описом автоматизації |
| **Event** | Тригер, що запускає workflow (push, PR, schedule, manual) |
| **Runner** | Виртуальна машина (ubuntu, windows, macOS), де виконуються кроки |
| **Job** | Незалежна задача, що складається з декількох кроків |
| **Step** | Окремий крок у job'і (команда або готова Action) |
| **Action** | Готовий компонент для частих операцій |

---

## 2. Практичне створення Workflow файлу

### 2.1 Начальний етап

Почав з того, що перейшов до вкладки **Actions** в своєму GitHub репозиторії та обрав шаблон **Python application**. Натиснув кнопку **Configure** для редагування файлу у web-інтерфейсі GitHub.

Наш проект являє собою гру у вгадування слів з наступною структурою:

**Основні модулі:**
- `file_module.py` – генерує випадкові слова через функцію `get_n_random_words(n: int) -> list`
- `main.py` – основна логіка гри:
  - `choose_secret_word()` – вибір слова для вгадування
  - `check_letters_in_word()` – перевірка букв у слові
  - `check_if_word_guessed()` – перевірка чи слово вгадане

**Тести:**
- `tests/test_file_module.py` – pytest тести для модуля генерації слів
- `tests/test_main.py` – unittest та pytest тести для основної гри

Шаблон автоматично створює базовий workflow файл:

```yaml
name: Python application
on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]
permissions:
  contents: read
jobs:
  build:
    runs-on: ubuntu-latest
```

### 2.2 Модифікація базового файлу

Переніс workflow файл до папки `.github/workflows/` з назвою `ci-cd.yml` та почав його поліпшувати.

#### Крок 1: Додав Support для Poetry

Оскільки наш проект використовує Poetry для управління залежностями:

```yaml
- name: Set up Poetry
  uses: Gr1N/setup-poetry@v9

- name: Install dependencies
  working-directory: ./lab
  run: poetry install --with dev
```

#### Крок 2: Додав Job для перевірки коду

Створив окремий job `code-quality` для лінтування:

```yaml
run-linters:
  needs: start
  name: Start running Linters
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Set up Python "3.13"
      uses: actions/setup-python@v6
      with:
        python-version: "3.13"
    - name: Setup Poetry
      uses: Gr1N/setup-poetry@v9
    - name: Install dependencies
      working-directory: ./lab
      env: 
        POETRY_VIRTUALENVS_CREATE: false
      run: |
        python -m pip install --upgrade pip
        poetry install --with dev
    - name: Lint with flake8
      working-directory: ./lab
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    - name: Run black formatter check
      working-directory: ./lab
      run: |
        black --check .
```

#### Крок 3: Додав Job для запуску тестів

```yaml
run-tests:
  needs: start
  name: Start running Tests
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Set up Python "3.13"
      uses: actions/setup-python@v6
      with:
        python-version: "3.13"
    - name: Setup Poetry
      uses: Gr1N/setup-poetry@v9        
    - name: Install dependencies
      working-directory: ./lab
      env: 
        POETRY_VIRTUALENVS_CREATE: false
      run: |
        python -m pip install --upgrade pip
        poetry install --with dev
    - name: Test with pytest
      working-directory: ./lab
      run: |
        pytest --cov --junitxml=junit.xml -o junit_family=legacy -v
    - name: Generate Report
      working-directory: ./lab
      run: |
        coverage report
```

---

## 3. Налаштування тригерів та подій

### 3.1 Базові тригери

```yaml
on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]
```

Workflow запускається:
- При кожному push в основну гілку
- При відкритті або оновленні pull request

Це гарантує, що код завжди проходить перевірку перед мерженням.

### 3.2 Ручний запуск (workflow_dispatch)

```yaml
workflow_dispatch:
  inputs:
    debug_mode:
      description: 'Увімкнути режим debug'
      required: false
      default: 'false'
```

Це дозволяє запускати workflow вручну з передачею параметрів. Дуже корисно для:
- Перепусту тестів на старих коммітах
- Налагодження
- Тестування нових версій Python без розробки

### 3.3 Запуск за розписанням (Cron)

```yaml
schedule:
  - cron: '0 7 * * tue'  # Щовівторка о 7:00 UTC
```

Мій workflow запускається автоматично щовівторка о 7 ранку за UTC, що дозволяє:
- Стежити за залежностями та їхніми оновленнями
- Виявляти потенційні проблеми на старих версіях
- Мати регулярні звіти про стан кодової бази

**Розшифровка Cron виразу:**
- `0` – хвилини (0 = на початку години)
- `7` – години (7 = 7:00 AM)
- `*` – день місяця (будь-який)
- `*` – місяць (будь-який)  
- `tue` – день тижня (вівторок)

Для налаштування використовую [CronTab GURU](https://crontab.guru/) — зручний інструмент для тестування Cron виразів.

---

## 4. Продвинуті можливості

### 4.1 Залежності між Jobs (Dependency Graph)

Граф виконання моїх jobs:

```
start (стартова точка)
  ├── run-linters (залежить від start)
  └── run-tests (залежить від start)
```

Використовую директиву `needs`:

```yaml
run-linters:
  needs: start
  # ... решта конфігурації

run-tests:
  needs: start
  # ... решта конфігурації
```

Це гарантує порядок виконання та дозволяє економити ресурси — якщо перший job не пройшов, наступні не запускаються.

### 4.2 Умовне виконання кроків

```yaml
- name: Send Slack notification on failure
  if: failure()
  run: echo "Workflow failed!"

- name: Commit coverage report
  if: github.event_name == 'push'
  run: git add . && git commit -m "Update coverage report"
```

Умови дозволяють:
- Виконувати різні кроки залежно від результату попередніх
- Відправляти сповіщення про помилки
- Запускати різні стратегії залежно від типу события

### 4.3 Використання Artifacts (опціонально)

GitHub Actions дозволяє зберігати результати виконання workflow для подальшого використання. За замовчуванням наш workflow створює звіти, які видалються після певного часу.

Для експорту звітів:

```yaml
- name: Upload coverage report
  uses: actions/upload-artifact@v4
  with:
    name: coverage-report
    path: ./lab/coverage.xml
```

Artifacts дозволяють:
- Зберігати результати тестів та звіти
- Скачувати їх з Actions вкладки
- Використовувати в наступних workflow

У нашому проекті важливі файли, які генеруються:
- `junit.xml` – звіт про тести
- `coverage.json` – статистика покриття
- `.coverage` – деталізований звіт покриття

---

## 5. Інтеграція з Codecov

### Процес налаштування:

1. Зареєструвався на [codecov.io](https://codecov.io/)
2. Авторизувався через GitHub
3. Дозволив Codecov доступ до мого репозиторію
4. Додав крок для завантаження звіту у workflow:

```yaml
- name: Test with pytest
  working-directory: ./lab
  run: |
    pytest --cov --junitxml=junit.xml -o junit_family=legacy -v

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    files: ./lab/coverage.xml
    directory: ./lab
    flags: unittests
    name: codecov-coverage
```

### Локальне виконання:

Для локального запуску тестів з покриттям:

```bash
cd lab
poetry install --with dev
poetry run pytest --cov --junitxml=junit.xml -o junit_family=legacy -v
poetry run coverage report
```

Це генерує звіти у форматах:
- **XML** (`.coverage`) та лог `coverage.json` – для завантаження на Codecov
- **Terminal** – висновок у терміналі
- **junit.xml** – для GitHub Actions інтеграції

### Результати:

Codecov надає детальну статистику:
- Загальне покриття коду (%)
- Покриття по файлам (`main.py`, `file_module.py`)
- Покриття по функціях (наприклад, `get_n_random_words()`, `check_letters_in_word()`)
- Порівняння з попередніми версіями
- Бажаний рівень покриття

---

## 6. Демонстрація статусу проекту

### Додавання Workflow Badge

Для додавання badge'у до README:

1. Перейти до **Actions** → вибрати Workflow
2. Натиснути **...** → **Create status badge**
3. Скопіювати згенерований код

Приклад для мого проекту:

```markdown
![CI/CD Pipeline](https://github.com/username/repo/actions/workflows/ci-cd.yml/badge.svg?branch=main)
```

---

## 7. Практичні результати та висновки

### Досягнутих результатів:

✅ **Створено workflow файл** з повною CI/CD інтеграцією  
✅ **Налаштовано 3 основні jobs** (notify, code-quality, run-tests)  
✅ **Реалізовано 4 типи тригерів** (push, PR, manual, schedule)  
✅ **Виконано лінтування коду** через flake8 та black  
✅ **Запущено автоматичне тестування** з вимірюванням покриття  
✅ **Інтегровано Codecov** для моніторингу покриття  
✅ **Додано статусні badge'и** до README файлу  

### Що я вивчив:

1. **GitHub Actions** — архітектура та використання
2. **YAML синтаксис** для конфігурації workflows
3. **CI/CD концепції** та практичне застосування
4. **Тестування та контроль якості** автоматизація
5. **Інтеграція зовнішніх сервісів** (Codecov, GitHub)
6. **Управління залежностями** через Poetry в CI
7. **Моніторинг та звітування** про стан проекту

### Проблеми та їх вирішення:

| Проблема | Рішення |
|----------|---------|
| Poetry не встановлювався | Додав версію Python та обрав правильний Action |
| Тести не знаходили модулі | Встановив `working-directory: ./lab` |
| Codecov не завантажував звіти | Переконався, що шлях до файла правильний |

### Практичні поради:

- **Кешування залежностей**: Використовуй actions/cache для прискорення
- **Паралельне виконання**: Jobs виконуються паралельно за замовчуванням
- **Ресурси**: GitHub надає 2000 хвилин/місяць для публічних репозиторіїв
- **Тестування локально**: Використовуй `act` для локального запуску workflows

---

## Висновки

Лабораторна робота дала мені комплексне розуміння GitHub Actions та CI/CD процесів. Тепер я можу:

- Налаштовувати автоматичне тестування для своїх проектів
- Контролювати якість коду за допомогою лінтерів
- Відстежувати покриття тестами через Codecov
- Демонструвати стан проекту через badge'и
- Раціонально використовувати ресурси GitHub Actions

Ця робота показала мені, що автоматизація є критичною частиною сучасної розробки. Вона економить час, попереджує помилки та дозволяє фокусуватися на написанні якісного коду.

**Роботу завершено успішно! ✅**