def factorial(n: int) -> int:
    """
    Обчислення факторіалу числа.

    :param n: Невід'ємне ціле число
    :return: Факторіал числа
    """
    if n < 0:
        raise ValueError("Факторіал для від'ємних чисел не визначено")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result