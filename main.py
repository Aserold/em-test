from typing import List, Dict, Any, Literal
import datetime
from decimal import Decimal
import re
import csv


class BudgetTracker:
    """Main client class"""

    COMMANDS = [
        ('help', 'list all commands and descriptions'),
        ('balance', 'show your balance aswell as your transactions'),
        ('add', 'add a transaction'),
        ('patch', 'change a transaction'),
        ('search',
         'search for a transaction based on a category, date or amount'),
        ('exit', 'exit client')
    ]

    def help() -> None:
        """Print all available commands with their descriptions"""
        text = "Available commands:\n"
        for command, description in BudgetTracker.COMMANDS:
            text += f"\n  {command:64}- {description}"

        return text

    def get_all_data() -> List[Dict] | None:
        """Read all data from the file"""
        with open('database.csv', 'r', encoding='UTF-8') as f:
            data: List[List, Any] = f.read().splitlines()

        if len(data) < 2:
            return

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
        Uses data from the file to display the balance, income and expenses
        """
        data: List[Dict] = BudgetTracker.get_all_data()
        text: str = f"\n\nTotal balance — {data[-1].get('balance', None)}\n\n"

        income: List[Dict] | None = list(
            filter(lambda x: x['category'] == 'доход', data))
        expenses: List[Dict] | None = list(
            filter(lambda x: x['category'] == 'расход', data))

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
        date_regex = r'^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[012])\.\d{4}$'

        if not re.match(date_regex, date):
            return False

        day, month, year = map(int, date.split('.'))
        try:
            datetime.datetime(year, month, day)
        except ValueError:
            return False

        return True

    def _validate_amount(amount: str) -> bool:
        amount_regex = r'^\d+(\.\d+)?$'

        if re.match(amount_regex, amount):
            return True
        else:
            return False

    def add_transaction() -> str:
        """Adds a transaction"""
        while True:
            date: str = input("Enter a date with this format - <dd.mm.yyyy>: ")
            if BudgetTracker._validate_date(date):
                break
            else:
                print("Invalid date format or date does not exist."
                      "Please enter in dd.mm.yyyy format.")

        while True:
            category: str = input("Enter a category - доход/расход: ").lower()
            match category:
                case 'доход':
                    break
                case 'расход':
                    break
                case _:
                    print('Incorrect format.')

        while True:
            amount_str: str = input("Enter the amount of the transaction. "
                                    "(Only positive number, use '.' "
                                    "for a floating point): ")
            if BudgetTracker._validate_amount(amount_str):
                amount: Decimal = round(Decimal(amount_str), 2)
                break
            else:
                print("Invalid amount format.")

        while True:
            description: str = input('Enter the description '
                                     'under 64 symbols: ')
            if len(description) > 64:
                print('Description too long.')
            else:
                break

        transactions: List[Dict] | None = BudgetTracker.get_all_data()

        if transactions:
            latest_transaction: Dict = BudgetTracker.get_all_data()[-1]

            balance: Decimal = (
                BudgetTracker.get_all_data()[-1]['balance'] + amount
                if category == 'доход'
                else BudgetTracker.get_all_data()[-1]['balance'] - amount)

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
        """Change a transaction"""
        all_transactions: List[Dict] = BudgetTracker.get_all_data()
        if not all_transactions:
            print('No transactions to patch.')
            return

        # Получаем id
        while True:
            try:
                id_: int = int(input('Enter ID of the transaction: '))
            except ValueError:
                print('Invalid value. Please enter a valid number.')
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
            date: str = input("Enter a date with this format - <dd.mm.yyyy>."
                              "\nLeave empty to skip: ")
            if date == '':
                date: str = selected_trans['date'].strftime("%d.%m.%Y")
                break
            elif BudgetTracker._validate_date(date):
                break
            else:
                print("Invalid date format or date does not exist."
                      "Please enter in dd.mm.yyyy format.")
        date: datetime.date = datetime.date(int(date.split('.')[2]),
                                            int(date.split('.')[1]),
                                            int(date.split('.')[0]),)

        # Получаем категорию
        while True:
            category: str = input("Enter a category - доход/расход."
                                  "\nLeave empty to skip: ").lower()
            match category:
                case 'доход':
                    break
                case 'расход':
                    break
                case '':
                    category: str = selected_trans['category']
                    break
                case _:
                    print('Incorrect format.')

        # Получаем сумму
        while True:
            amount_str: str = input("Enter the amount of the transaction. \n"
                                    "(Only positive number, use '.' "
                                    "for a floating point).\n"
                                    "Leave empty to skip: ")
            if amount_str == '':
                amount: Decimal = selected_trans['amount']
                break
            elif BudgetTracker._validate_amount(amount_str):
                amount: Decimal = round(Decimal(amount_str), 2)
                break
            else:
                print("Invalid amount format.")

        # Получаем описание
        while True:
            description: str = input('Enter the description '
                                     'under 64 symbols.\n'
                                     'Leave empty to skip: ')
            if description == '':
                description: str = selected_trans['description']
                break
            elif len(description) > 64:
                print('Description too long.')
            else:
                break

        # Рассчитываем баланс исходя из предыдущей записи
        for index, trans in enumerate(all_transactions):
            if trans == selected_trans and index != 1:
                balance: Decimal = (
                    all_transactions[index-1]['balance'] + amount
                    if category == 'доход'
                    else all_transactions[index-1]['balance'] - amount)
            elif trans == selected_trans and index == 1:
                balance: Decimal = (
                    amount if category == 'доход'
                    else - amount)

        patched_transaction: Dict = {
            'id': id_, 'date': date, 'category': category,
            'amount': amount, 'description': description,
            'balance': round(balance, 2)
        }

        # Проверяем наличие изменений
        if patched_transaction == selected_trans:
            return BudgetTracker.balance()

        # Расчитываем баланс для всех последующих записей
        transaction_found = False
        for index, trans in enumerate(all_transactions):
            if trans == selected_trans:
                all_transactions[index] = patched_transaction
                transaction_found = True

            if transaction_found:
                balance: Decimal = (
                    all_transactions[index-1]['balance'] + amount
                    if category == 'доход'
                    else all_transactions[index-1]['balance'] - amount)
                all_transactions[index]['balance'] = balance

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

    def main() -> None:
        print('Client started! Type "help" for all commands')
        while True:
            pass


if __name__ == "__main__":
    print(BudgetTracker.patch_transaction())
