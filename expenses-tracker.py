import pandas as pd
import numpy as np
from datetime import datetime
import argparse


def help_message():
    print("""
Commands:
  add --description "Description" --amount <amount>           > Add a new expense
  update <id> --description "Description" --amount <amount>   > Update the expense
                        --category "Category"
  delete <id>                                                 > Delete the expense
  list                                                        > List all expenses
  list --year|--month|--category                              > Filter by date/category
  summary --year|--month|--category                           > Sum by date/category           
  exit                                                        > Exit the program
""")
    

warning_color = '\033[91m' # the color the warning messages will be (currently red)
program_color = '\033[33m' # the color that 'task-cli' will be printed in (currently yellow)
reset_color = '\033[0m' # resets the terminal color to the default one (white)

try:
    expenses = pd.read_csv('expenses.csv', parse_dates=['Date'])
    if expenses.empty or expenses.columns.tolist() != ['ID', 'Date', 'Description', 'Amount', 'Category']:
        raise ValueError(f'{warning_color}CSV file is faulty or empty{reset_color}')
except (ValueError, FileNotFoundError):
    expenses = pd.DataFrame(columns=['ID', 'Date', 'Description', 'Amount', 'Category'])
    expenses.to_csv('expenses.csv', index=False)
    help_message()

def save():
    global expenses
    expenses.to_csv('expenses.csv', index=False)

def add(desc, amount, category=None):
    global expenses
    desc = desc.strip()
    date = datetime.today().date()
    expenses.loc[len(expenses)] = [int(expenses['ID'].max() + 1) if not expenses['ID'].empty and pd.notna(expenses['ID'].max()) else 0, date, desc, amount, category if category else 'Other']
    save()

def update(id, desc=None, amount=None, category=None):
    global expenses
    id = int(id)

    if not expenses[expenses['ID'] == id].empty:
        if desc is None and amount is None and category is None:
            print(f'{warning_color}Please provide the description and/or the amount and/or the the category.{reset_color}')
        else:
            if desc:
                desc = desc.strip()
                expenses.loc[expenses['ID'] == id, 'Description'] = desc
                save()
            if amount:
                amount = float(amount)
                expenses.loc[expenses['ID'] == id, 'Amount'] = amount
                save()
            if category:
                category = category.strip()
                expenses.loc[expenses['ID'] == id, 'Category'] = category
                save()
    else:
        print(f'{warning_color}No expenses found at ID: {id}{reset_color}')

def delete(id):
    id = int(id)
    global expenses
    if not expenses[expenses['ID'] == id].empty:
        expenses = expenses[expenses['ID'] != id]
        save()
    else:
        print(f'{warning_color}No expenses found at ID: {id}{reset_color}')
    
def list_expenses(category=None, month=None, year=None):
    df = expenses.copy()

    if category:
        df = df[df['Category'].str.lower() == category.lower()]
    if month:
        df = df[pd.to_datetime(df['Date']).dt.month == int(month)]
    if year:
        df = df[pd.to_datetime(df['Date']).dt.year == int(year)]

    if df.empty:
        print(f"{warning_color}No matching expenses found.{reset_color}")
    else:
        print(f'{program_color}' + df.to_string(index=False) + f'{reset_color}')
            
def summary(month=None, year=None, category=None):
    df = expenses.copy()
    if month:
        df = df[pd.to_datetime(df['Date']).dt.month == int(month)]
    if year:
        df = df[pd.to_datetime(df['Date']).dt.year == int(year)]
    if category:
        category = category.strip()
        df = df[df['Category'].str.lower() == category.lower()]        
        
    print(f"{program_color}Total expenses: {reset_color}{df['Amount'].sum():.2f}")


def main():
    parser = argparse.ArgumentParser(description='Expense Tracker CLI')
    subparsers = parser.add_subparsers(dest='command', required=True)

    parser_add = subparsers.add_parser('add', help='Add a new expense')
    parser_add.add_argument('--description', required=True, help='Description of the Expense')
    parser_add.add_argument('--amount', required=True, type=float, help='Amount associated with the expense')
    parser_add.add_argument('--category', help='Category of the expense')

    parser_update = subparsers.add_parser('update', help='Updates the expense at the given ID with the description or the amount provided')
    parser_update.add_argument('id', type=int, help='ID of the expense you want to update')
    parser_update.add_argument('--description', help="New description")
    parser_update.add_argument('--amount', type=float, help='New amount')
    parser_update.add_argument('--category', help='New category')

    parser_delete = subparsers.add_parser('delete', help='Delete the expense')
    parser_delete.add_argument('id', type=int, help='ID of the expense you want to delete')

    parser_list = subparsers.add_parser('list', help='List all expenses')  
    parser_list.add_argument('--category', help="Filter by category")
    parser_list.add_argument('--month', type=int, help="Filter by month (1-12)")
    parser_list.add_argument('--year', type=int, help="Filter by year")
    

    parser_summary = subparsers.add_parser('summary', help='Returns the sum of all the expenses')  
    parser_summary.add_argument('--month', type=int, help='Returns the sum of expensess in the given month')
    parser_summary.add_argument('--year', type=int, help='Returns the sum of expenses in the given year')
    parser_summary.add_argument('--category', help='Returns the sum of all expenses in the given category')

    parser_help = subparsers.add_parser('help', help='Show help message')

    args = parser.parse_args()

    if args.command == 'add':
        print(f'{program_color}Added {args.description}{reset_color}')
        add(args.description, args.amount, args.category)

    elif args.command == 'update':
        print(f'{program_color}Updated the expense at ID: {args.id}{reset_color}')
        update(args.id, args.description, args.amount, args.category)

    elif args.command == 'delete':
        if expenses[expenses["ID"] == args.id].empty:
            print(f"{warning_color}No expense found at ID {args.id}.{reset_color}")
        else:
            print(f'{warning_color}Deleted "{expenses[expenses["ID"] == args.id]["Description"].values[0]}"{reset_color}')
            delete(args.id)

    elif args.command == 'list':
        list_expenses(category=args.category, month=args.month, year=args.year)

    elif args.command == 'summary':
        summary(args.month, args.year, args.category)

    elif args.command == 'help':
        help_message()

if __name__ == '__main__':
    main()