from typing import List, Dict, Any, Literal
import datetime
from decimal import Decimal
import re
import csv
import sys


class BudgetTracker:
    """Основной класс клиента"""

    COMMANDS = [
        ('help', 'Показать список всех команд и их описания'),
        ('balance', 'Показать ваш баланс и список транзакций'),
        ('add', 'Добавить транзакцию'),
        ('patch', 'Изменить транзакцию'),
        ('search',
         '"-c" - категория, "-d" - дата, "-a" - сумма\n'
         'поиск транзакции по категории, дате или сумме'),
        ('exit', 'выйти из клиента')
    ]

    def help() -> str:
        """Выводит все доступные комманды"""
        text = "Доступные комманды:\n"
        for command, description in BudgetTracker.COMMANDS:
            text += f"\n  {command:64}- {description}"

        return text

    def _get_all_data() -> List[Dict] | None:
        """Считывает все данные из файла"""
        try:
            with open('database.csv', 'r', encoding='UTF-8') as f:
                data: List[List, Any] = f.read().splitlines()
        # Если файла нет - создаём его
        except FileNotFoundError:
            with open('database.csv', 'w', encoding='UTF-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'id', 'date', 'category', 'amount',
                    'description', 'balance'])
            return

        if len(data) < 2:
            return

        # Записываем все данные в список в виде словарей
        data_list = []
        for param in list(map(lambda x: x.split(','), data[1:])):
            id: int = int(param[0])
            date: datetime.date = datetime.date(int(param[1].split('.')[2]),
                                                int(param[1].split('.')[1]),
                                                int(param[1].split('.')[0]),)
            category: Literal['доход', 'расход'] = param[2]
            amount: Decimal = Decimal(param[3])
            description: str = param[4]
            balance: Decimal = Decimal(param[5])

            data_list.append(
                {'id': id, 'date': date, 'category': category,
                 'amount': amount, 'description': description,
                 'balance': balance}
            )
        return data_list

    def balance() -> str:
        """
        Получая данные из файла выводит баланс и записи
        """
        data: List[Dict] = BudgetTracker._get_all_data()
        if not data:
            return 'Записей не найдено'

        text: str = f"\n\nБаланс — {data[-1].get('balance', None)}\n\n"

        # Разбиваем записи на доходы и расходы для корректного отображения
        income: List[Dict] | None = list(
            filter(lambda x: x['category'] == 'доход', data))
        expenses: List[Dict] | None = list(
            filter(lambda x: x['category'] == 'расход', data))

        # Добавляем все записи циклом в переменную "text"
        for i in range(max(len(income), len(expenses))):
            income_value = income[i] if i < len(income) else ''
            expense_value = expenses[i] if i < len(expenses) else ''

            text += (
                f"{'ID: '+str(income_value['id'])
                    if income_value else '':<64}| "
                f"{'ID: '+str(expense_value['id'])
                    if expense_value else '':<64}\n"

                f"{'Дата: '+income_value['date'].strftime("%d.%m.%Y")
                    if income_value else '':<64}| "
                f"{'Дата: '+expense_value['date'].strftime("%d.%m.%Y")
                    if expense_value else '':<64}\n"

                f"{'Категория: '+income_value['category']
                    if income_value else '':<64}| "
                f"{'Категория: '+expense_value['category']
                    if expense_value else '':<64}\n"

                f"{'Сумма: '+str(income_value['amount'])
                    if income_value else '':<64}| "
                f"{'Сумма: '+str(expense_value['amount'])
                    if expense_value else '':<64}\n"

                f"{'Описание: '+income_value['description']
                    if income_value else '':<64}| "
                f"{'Описание: '+expense_value['description']
                    if expense_value else '':<64}\n\n"
            )

        return text

    def _validate_date(date: str) -> bool:
        """
        Проверка даты на корректный формат с помощью регулярного выражения и
        модуля datetime
        """
        date_regex = r'^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[012])\.\d{4}$'

        if not re.match(date_regex, date):
            return False

        # Проверка для того, чтобы нельзя было ввести 30 февраля, например
        day, month, year = map(int, date.split('.'))
        try:
            datetime.datetime(year, month, day)
        except ValueError:
            return False

        return True

    def _validate_amount(amount: str) -> bool:
        """Проверка суммы на корректный формат"""
        amount_regex = r'^\d+(\.\d+)?$'

        if re.match(amount_regex, amount):
            return True
        else:
            return False

    def add_transaction() -> str:
        """Adds a transaction"""
        # Цикл для получения и валидации даты
        while True:
            date: str = input('Введите дату в данном формате - дд.мм.гггг: ')
            if BudgetTracker._validate_date(date):
                break
            else:
                print("Некорректный формат или дата не существует.")

        # Цикл для получения и валидации категории
        while True:
            category: str = input("Введите категорию - доход/расход: ").lower()
            if BudgetTracker._validate_category(category):
                break
            else:
                print('Некорректный формат категории.')

        # Цикл для получения и валидации суммы
        while True:
            amount_str: str = input(
                'Введите сумму. Только положительные числа.\n'
                '(. для плавающей запятой): ')
            if BudgetTracker._validate_amount(amount_str):
                amount: Decimal = round(Decimal(amount_str), 2)
                break
            else:
                print("Некорректный формат суммы.")

        # Цикл для получения описания
        while True:
            description: str = input('Введите описание '
                                     'не более 64 символов: ')
            if len(description) > 64:
                print('Превышен лимит символов.')
            else:
                break

        transactions: List[Dict] | None = BudgetTracker._get_all_data()

        if transactions:
            latest_transaction: Dict = BudgetTracker._get_all_data()[-1]
            # Рассчитываем баланс исходя из последней записи
            balance: Decimal = (
                BudgetTracker._get_all_data()[-1]['balance'] + amount
                if category == 'доход'
                else BudgetTracker._get_all_data()[-1]['balance'] - amount)

            id_: int = latest_transaction['id'] + 1

            data_list = [
                id_, date, category, amount, description, round(balance, 2)
                ]

            with open(
                    'database.csv', 'a', encoding='UTF-8'
                    ) as file:
                writer = csv.writer(file)
                writer.writerow(data_list)
            return BudgetTracker.balance()

        # В случае если нет записей в файле
        else:
            id_ = 1
            balance: Decimal = (
                round(Decimal(amount), 2)
                if category == 'доход'
                else round(Decimal(-amount), 2)
                )

            data_list = [
                id_, date, category, amount, description, balance
                ]

            with open(
                    'database.csv', 'a', encoding='UTF-8'
                    ) as file:
                writer = csv.writer(file)
                writer.writerow(data_list)
            return BudgetTracker.balance()

    def patch_transaction() -> str | None:
        """Изменение записи (много копипасты)"""
        all_transactions: List[Dict] = BudgetTracker._get_all_data()
        if not all_transactions:
            return 'Отсутствуют записи для редактирования.'

        # Получаем id
        while True:
            try:
                id_: int = int(input('Введите ID записи: '))
            except ValueError:
                print('Недопустимое значение. Введите число.')
                continue

            id_found = False
            for trans in all_transactions:
                if trans['id'] == id_:
                    id_found = True
                    selected_trans: Dict = trans
                    break
            if id_found:
                break
            else:
                print('ID not found. Try again')

        # Получаем дату и форматируем для будущей проверки
        while True:
            date: str = input("Введите дату в данном формате - дд.мм.гггг: "
                              "\nОставьте пустым чтобы пропустить: ")
            if date == '':
                date: str = selected_trans['date'].strftime("%d.%m.%Y")
                break
            elif BudgetTracker._validate_date(date):
                break
            else:
                print("Некорректный формат или дата не существует.")
        date: datetime.date = datetime.date(int(date.split('.')[2]),
                                            int(date.split('.')[1]),
                                            int(date.split('.')[0]),)

        # Получаем категорию
        while True:
            category: str = input(
                "Введите категорию - доход/расход."
                "\nОставьте пустым чтобы пропустить: ").lower()
            if BudgetTracker._validate_category(category):
                break
            elif category == '':
                category: str = selected_trans['category']
                break
            else:
                print('Некорректный формат категории.')

        # Получаем сумму
        while True:
            amount_str: str = input(
                'Введите сумму. Только положительные числа.\n'
                '(. для плавающей запятой)\n'
                'Оставьте пустым чтобы пропустить: ')
            if amount_str == '':
                amount: Decimal = selected_trans['amount']
                break
            elif BudgetTracker._validate_amount(amount_str):
                amount: Decimal = round(Decimal(amount_str), 2)
                break
            else:
                print("Некорректный формат суммы.")

        # Получаем описание
        while True:
            description: str = input('Введите описание '
                                     'не более 64 символов\n'
                                     'Оставьте пустым чтобы пропустить: ')
            if description == '':
                description: str = selected_trans['description']
                break
            elif len(description) > 64:
                print('Превышен лимит символов..')
            else:
                break

        patched_transaction: Dict = {
            'id': id_, 'date': date, 'category': category,
            'amount': amount, 'description': description,
            'balance': 0
        }

        # Рассчитываем баланс исходя из предыдущей записи
        index = all_transactions.index(selected_trans)
        if index == 0:
            balance = amount if category == 'доход' else -amount
        else:
            balance = all_transactions[index - 1]['balance'] + \
                      (amount if category == 'доход' else -amount)

        patched_transaction['balance'] = round(balance, 2)

        # Проверяем наличие изменений
        if patched_transaction == selected_trans:
            return BudgetTracker.balance()

        # Заменяем старую запись на новую
        all_transactions.pop(index)
        all_transactions.insert(index, patched_transaction)

        # Расчитываем баланс для всех последующих записей
        if len(all_transactions) > 1:
            for i in range(index + 1, len(all_transactions)):
                all_transactions[i]['balance'] = \
                    all_transactions[i - 1]['balance'] + (
                        all_transactions[i]['amount']
                        if all_transactions[i]['category'] == 'доход'
                        else -all_transactions[i]['amount'])
        else:
            all_transactions = [patched_transaction]

        # Записываем данные заново в файл
        with open('database.csv', 'w', encoding='UTF-8') as file:
            writer = csv.writer(file)
            head = [
                'id', 'date', 'category', 'amount', 'description', 'balance'
                ]
            writer.writerow(head)
            for index, trans in enumerate(all_transactions):
                data = [
                    all_transactions[index]['id'],
                    all_transactions[index]['date'].strftime("%d.%m.%Y"),
                    all_transactions[index]['category'],
                    all_transactions[index]['amount'],
                    all_transactions[index]['description'],
                    all_transactions[index]['balance'],
                ]
                writer.writerow(data)
        return BudgetTracker.balance()

    def _validate_category(category: str) -> bool:
        """Валидатор параметра 'категория'"""
        if category == 'доход' or category == 'расход':
            return True
        return False

    def _filter_transactions(
                            all_trans: List[Dict[int, Any]],
                            option: Literal['-c', '-d', '-a'] | None = None,
                            value: str | None = None) -> list:
        """Основной метод для фильтрации по запросу"""

        try:
            match option:
                # Проверка на параметр "категория"
                case '-c':
                    # Валидация значения
                    if BudgetTracker._validate_category(value.lower()):
                        filtered_transactions: List[Dict[int, Any]] | list = [
                            trans for trans in all_trans
                            if trans['category'] == value.lower()
                        ]
                        # Возврат отфильтрованных данных или [] при успехе
                        return filtered_transactions
                    else:
                        print('Неверное значение для параметра "-c".')
                        raise ValueError

                # Проверка на параметр "дата"
                case '-d':
                    # Валидация значения
                    if BudgetTracker._validate_date(value):
                        filtered_transactions: List[Dict[int, Any]] | list = [
                            trans for trans in all_trans
                            if trans['date'].strftime("%d.%m.%Y") == value
                        ]
                        # Возврат отфильтрованных данных или [] при успехе
                        return filtered_transactions
                    else:
                        print('Неверное значение для параметра "-d".')
                        raise ValueError

                # Проверка на параметр "сумма"
                case '-a':
                    # Валидация значения
                    if BudgetTracker._validate_amount(value.lower()):
                        filtered_transactions: List[Dict[int, Any]] | list = [
                            trans for trans in all_trans
                            if trans['amount'] == Decimal(value)
                        ]
                        # Возврат отфильтрованных данных или [] при успехе
                        return filtered_transactions
                    else:
                        print('Неверное значение для параметра "-a".')
                        raise ValueError

                # Возврат ошибки, если ничего не сошлось
                case _:
                    print('Параметр не введен или введён неверно.')
                    raise ValueError
        # Отлавливаем ошибку, которую вызвали при неверно введенных данных
        except ValueError:
            while True:
                filter_: str = input('Введите фильтр для поиска.\n'
                                     'категория/дата/сумма: ').lower()
                match filter_:
                    # Проверка на параметр "категория"
                    case 'категория':
                        filter_option = '-c'
                        filter_value: str = input(
                            'Введите категорию. доход/расход: ')
                        if BudgetTracker._validate_category(filter_value):
                            # Снова вызываем эту же функцию подставив значнеиия
                            return BudgetTracker._filter_transactions(
                                all_trans,
                                filter_option,
                                filter_value)
                        else:
                            print('Неверное значение для фильтра "категория"')
                            continue

                    # Проверка на параметр "дата"
                    case 'дата':
                        filter_option = '-d'
                        filter_value: str = input(
                            'Введите дату. Формат - дд.мм.гггг: ')
                        if BudgetTracker._validate_date(filter_value):
                            # Снова вызываем эту же функцию подставив значнеиия
                            return BudgetTracker._filter_transactions(
                                all_trans,
                                filter_option,
                                filter_value)
                        else:
                            print('Неверное значение для фильтра "дата"')
                            continue

                    # Проверка на параметр "сумма"
                    case 'сумма':
                        filter_option = '-a'
                        filter_value: str = input(
                            'Введите сумму. Только положительные числа.\n'
                            '(. для плавающей запятой): ')
                        if BudgetTracker._validate_amount(filter_value):
                            # Снова вызываем эту же функцию подставив значнеиия
                            return BudgetTracker._filter_transactions(
                                all_trans,
                                filter_option,
                                filter_value)
                        else:
                            print('Неверное значение для фильтра "сумма"')
                            continue

                    case _:
                        print('Параметр не введен или введён неверно.')

    def search_transactions(option: Literal['-c', '-d', '-a'] | None = None,
                            value: str | None = None) -> str:
        """Поиск записей по параметру или без него"""
        all_transactions: List[Dict] = BudgetTracker._get_all_data()
        if not all_transactions:
            return "Нет данных для поиска."

        # Вызываем функцию для возврата отфильтрованных значений
        filtered_transactions: List[Dict, Any] | List = (
            BudgetTracker._filter_transactions(
                all_transactions, option, value
            )
        )

        if not filtered_transactions:
            return 'Не найдено записей по заданному фильтру'

        text = '\n\nОтфильтрованные записи:\n\n'
        for trans in filtered_transactions:
            text += (f"ID: {trans['id']}\n"
                     f"Дата: {trans['date'].strftime('%d.%m.%Y')}\n"
                     f"Категория: {trans['category']}\n"
                     f"Сумма: {trans['amount']}\n"
                     f"Описание: {trans['description']}\n\n")

        return text

    def exit():
        """Выход из программы"""
        print('\nОстановка программы...')
        sys.exit()

    @classmethod
    def main(cls) -> None:
        """Основная функция для работы с клиентом"""
        print('Клиент запущен! Введите "help" для просмотра всех комманд')
        while True:
            input_: str = input('Введите комманду: ')
            try:
                command: str = input_.split(' ')[0]
                option: str = input_.split(' ')[1]
                value: str = input_.split(' ')[2]
            except IndexError:
                command: str = input_
            match command:
                case 'help':
                    print(BudgetTracker.help())
                case 'balance':
                    print(BudgetTracker.balance())
                case 'add':
                    print(BudgetTracker.add_transaction())
                case 'patch':
                    print(BudgetTracker.patch_transaction())
                case 'search':
                    try:
                        print(BudgetTracker.search_transactions(
                            option, value
                        ))
                    except UnboundLocalError:
                        print(BudgetTracker.search_transactions())
                case 'exit':
                    BudgetTracker.exit()
                case _:
                    print(f'Неизвестная команда "{input_}"')


if __name__ == "__main__":
    print(BudgetTracker.main())
