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

            if income_value and expense_value:
                text += (
                    f"{income_value['date'].strftime("%d.%m.%Y"):<64}| "
                    f"{expense_value['date'].strftime("%d.%m.%Y"):<64}\n"
                    f"{income_value['category']:<64}| "
                    f"{expense_value['category']:<64}\n"
                    f"{income_value['amount']:<64}| "
                    f"{expense_value['amount']:<64}\n"
                    f"{income_value['description']:<64}| "
                    f"{expense_value['description']:<64}\n\n"
                )
            elif income_value and not expense_value:
                text += (
                    f"{income_value['date'].strftime("%d.%m.%Y"):<64}| "
                    f"{expense_value:<64}\n"
                    f"{income_value['category']:<64}| "
                    f"{expense_value:<64}\n"
                    f"{income_value['amount']:<64}| "
                    f"{expense_value:<64}\n"
                    f"{income_value['description']:<64}| "
                    f"{expense_value:<64}\n\n"
                )
            else:
                text += (
                    f"{income_value:<64}| "
                    f"{expense_value['date'].strftime("%d.%m.%Y"):<64}\n"
                    f"{income_value:<64}| "
                    f"{expense_value['category']:<64}\n"
                    f"{income_value:<64}| "
                    f"{expense_value['amount']:<64}\n"
                    f"{income_value:<64}| "
                    f"{expense_value['description']:<64}\n\n"
                )

        return text

    def validate_date(date: str) -> bool:
        date_regex = r'^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[012])\.\d{4}$'

        if not re.match(date_regex, date):
            return False

        day, month, year = map(int, date.split('.'))
        try:
            datetime.datetime(year, month, day)
        except ValueError:
            return False

        return True

    def validate_amount(amount: str) -> bool:
        amount_regex = r'^\d+(\.\d+)?$'

        if re.match(amount_regex, amount):
            return True
        else:
            return False

    def add_transaction() -> str:
        """Adds a transaction"""
        while True:
            date: str = input("Enter a date with this format - <dd.mm.yyyy>: ")
            if BudgetTracker.validate_date(date):
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
            if BudgetTracker.validate_amount(amount_str):
                break
            else:
                print("Invalid amount format.")
        amount: Decimal = round(Decimal(amount_str), 2)

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


    def main() -> None:
        print('Client started! Type "help" for all commands')
        while True:
            pass


if __name__ == "__main__":
    print(BudgetTracker.balance())
