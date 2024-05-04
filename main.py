from typing import List, Dict, Any, Literal
import datetime
from decimal import Decimal


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

    def get_all_data() -> List[Dict[str, Any]] | None:
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
        data: List[Dict[str, Any]] = BudgetTracker.get_all_data()
        text: str = f'Total balance — {data[-1].get('balance', None)}\n\n'

        income: List[Dict[str, Any]] | None = list(
            filter(lambda x: x['category'] == 'доход', data))
        expenses: List[Dict[str, Any]] | None = list(
            filter(lambda x: x['category'] == 'расход', data))

        for i in range(max(len(income), len(expenses))):
            income_value = income[i] if i < len(income) else ''
            expense_value = expenses[i] if i < len(expenses) else ''
            text += (
                f"{income_value['date'].strftime("%d.%m.%Y"):<64}| "
                f"{expense_value['date'].strftime("%d.%m.%Y"):<64}\n"
                f"{income_value['category']:<64}| "
                f"{expense_value['category']:<64}\n"
                f"{income_value['amount']:<64}| "
                f"{expense_value['amount']:<64}\n"
                f"{income_value['description']:<64}| "
                f"{expense_value['description']:<64}\n"
            )

        return text

    def main() -> None:
        print('Client started! Type "help" for all commands')
        while True:
            pass


if __name__ == "__main__":
    BudgetTracker.main()
