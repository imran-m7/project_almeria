# Imran Mujkanović and Sara Avdić

"""
Personal Expense Tracker
A comprehensive terminal-based expense tracker with modular design, persistent storage, and advanced features.
"""
import os
import json
import csv
from datetime import datetime
from colorama import init, Fore

# Initialize colorama
init(autoreset=True)

# Const
EXPENSES_FILE = "expenses.txt"
DEFAULT_CATEGORIES = [
    "Food", "Transportation", "Entertainment", "Utilities", "Health", "Shopping", "Education", "Other"
]
DATE_FORMAT = "%Y-%m-%d"

# Data Structures
expenses = {cat: 0.0 for cat in DEFAULT_CATEGORIES}
expense_history = []  # List of tuples: (date, category, amount, description)
budgets = {cat: None for cat in DEFAULT_CATEGORIES}  # Optional budgets per category

# ---------------------- Data Operations ----------------------
def add_expense(category, amount, description=""):
    """
    Add a new expense to a category, update history, and validate input.
    Returns a confirmation message.
    """
    if category not in expenses:
        return f"{Fore.RED}Invalid category. Please choose from the list."
    try:
        amount = float(amount)
        if amount <= 0:
            return f"{Fore.RED}Amount must be positive."
    except ValueError:
        return f"{Fore.RED}Invalid amount. Please enter a number."
    today = datetime.now().strftime(DATE_FORMAT)
    record = (today, category, amount, description)
    expense_history.append(record)
    expenses[category] += amount
    return f"{Fore.GREEN}Expense added: {amount:.2f} to {category}."

def view_expenses_by_category():
    """
    Display all categories with current totals in a formatted table.
    """
    print(f"\n{Fore.CYAN}{'Category':<20}{'Total Spent':>15}")
    print(f"{Fore.CYAN}{'-'*35}")
    empty = True
    for cat, total in expenses.items():
        if total > 0:
            print(f"{cat:<20}{total:>15.2f}")
            empty = False
    if empty:
        print(f"{Fore.YELLOW}No expenses recorded yet.")

def calculate_total_expenses():
    """
    Sum all expenses across categories and display formatted output.
    """
    total = sum(expenses.values())
    print(f"\n{Fore.MAGENTA}Total Expenses: {Fore.YELLOW}${total:.2f}")
    return total

def find_highest_spending_category():
    """
    Identify category with maximum spending. Handle ties.
    """
    max_amount = max(expenses.values())
    if max_amount == 0:
        print(f"{Fore.YELLOW}No expenses to analyze.")
        return None, 0.0
    top_cats = [cat for cat, amt in expenses.items() if amt == max_amount]
    print(f"\n{Fore.BLUE}Highest Spending Category:")
    for cat in top_cats:
        print(f"{cat}: ${max_amount:.2f}")
    return top_cats, max_amount

def view_expense_history(filter_category=None, start_date=None, end_date=None):
    """
    Display chronological expense list, optionally filtered by category or date range.
    """
    print(f"\n{Fore.CYAN}{'Date':<12}{'Category':<18}{'Amount':>10}{'Description':<30}")
    print(f"{Fore.CYAN}{'-'*70}")
    filtered = []
    for rec in expense_history:
        rec_date, rec_cat, rec_amt, rec_desc = rec
        if filter_category and rec_cat != filter_category:
            continue
        if start_date and rec_date < start_date:
            continue
        if end_date and rec_date > end_date:
            continue
        filtered.append(rec)
        print(f"{rec_date:<12}{rec_cat:<18}{rec_amt:>10.2f}{rec_desc:<30}")
    if not filtered:
        print(f"{Fore.YELLOW}No expenses found for the given filter.")

def save_data_to_file(filename=EXPENSES_FILE):
    """
    Write all expense data to a text file in CSV format. Handle errors.
    """
    try:
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["date", "category", "amount", "description"])
            for rec in expense_history:
                writer.writerow(rec)
        # Save budgets and category totals as JSON
        meta = {
            "expenses": expenses,
            "budgets": budgets
        }
        with open(filename + ".meta", 'w', encoding='utf-8') as mf:
            json.dump(meta, mf)
    except Exception as e:
        print(f"{Fore.RED}Error saving data: {e}")

def load_data_from_file(filename=EXPENSES_FILE):
    """
    Read expense data from file and populate data structures. Handle errors.
    """
    global expenses, expense_history, budgets
    if not os.path.exists(filename):
        print(f"{Fore.YELLOW}No previous data found. Starting fresh.")
        return
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            for row in reader:
                if len(row) < 4:
                    continue
                rec_date, rec_cat, rec_amt, rec_desc = row
                rec_amt = float(rec_amt)
                expense_history.append((rec_date, rec_cat, rec_amt, rec_desc))
                if rec_cat in expenses:
                    expenses[rec_cat] += rec_amt
                else:
                    expenses[rec_cat] = rec_amt
        # Load meta (budgets, totals)
        meta_file = filename + ".meta"
        if os.path.exists(meta_file):
            with open(meta_file, 'r', encoding='utf-8') as mf:
                meta = json.load(mf)
                expenses.update(meta.get("expenses", {}))
                budgets.update(meta.get("budgets", {}))
    except Exception as e:
        print(f"{Fore.RED}Error loading data: {e}")

# ---------------------- Advanced Features ----------------------
def set_budget(category, amount):
    """Set a budget for a category."""
    if category not in budgets:
        print(f"{Fore.RED}Invalid category.")
        return
    try:
        amount = float(amount)
        if amount <= 0:
            print(f"{Fore.RED}Budget must be positive.")
            return
        budgets[category] = amount
        print(f"{Fore.GREEN}Budget for {category} set to ${amount:.2f}.")
    except ValueError:
        print(f"{Fore.RED}Invalid amount.")

def view_budgets():
    """Display budgets and spending per category."""
    print(f"\n{Fore.CYAN}{'Category':<20}{'Budget':>12}{'Spent':>12}{'Remaining':>12}")
    print(f"{Fore.CYAN}{'-'*56}")
    for cat in budgets:
        bud = budgets[cat]
        spent = expenses.get(cat, 0.0)
        rem = bud - spent if bud is not None else "-"
        bud_str = f"${bud:.2f}" if bud else "-"
        rem_str = f"${rem:.2f}" if bud else "-"
        print(f"{cat:<20}{bud_str:>12}{spent:>12.2f}{rem_str:>12}")

def monthly_summary(year, month):
    """Show summary for a given month."""
    print(f"\n{Fore.CYAN}Monthly Summary for {year}-{month:02d}")
    print(f"{Fore.CYAN}{'-'*40}")
    total = 0.0
    for rec in expense_history:
        rec_date, rec_cat, rec_amt, _ = rec
        rec_ym = datetime.strptime(rec_date, DATE_FORMAT)
        if rec_ym.year == year and rec_ym.month == month:
            print(f"{rec_date} | {rec_cat:<15} | ${rec_amt:>8.2f}")
            total += rec_amt
    print(f"{Fore.MAGENTA}Total: ${total:.2f}")

def weekly_summary(year, week):
    """Show summary for a given ISO week."""
    print(f"\n{Fore.CYAN}Weekly Summary for {year} Week {week}")
    print(f"{Fore.CYAN}{'-'*40}")
    total = 0.0
    for rec in expense_history:
        rec_date, rec_cat, rec_amt, _ = rec
        rec_dt = datetime.strptime(rec_date, DATE_FORMAT)
        if rec_dt.isocalendar()[:2] == (year, week):
            print(f"{rec_date} | {rec_cat:<15} | ${rec_amt:>8.2f}")
            total += rec_amt
    print(f"{Fore.MAGENTA}Total: ${total:.2f}")

def search_expenses(keyword):
    """Search expenses by keyword in description."""
    print(f"\n{Fore.CYAN}Search results for '{keyword}':")
    found = False
    for rec in expense_history:
        if keyword.lower() in rec[3].lower():
            print(f"{rec[0]} | {rec[1]:<15} | ${rec[2]:>8.2f} | {rec[3]}")
            found = True
    if not found:
        print(f"{Fore.YELLOW}No matching expenses found.")

def export_report(filename="expense_report.txt"):
    """Export a formatted report of all expenses."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Expense Report\n")
            f.write("="*40 + "\n")
            for rec in expense_history:
                f.write(f"{rec[0]}, {rec[1]}, ${rec[2]:.2f}, {rec[3]}\n")
        print(f"{Fore.GREEN}Report exported to {filename}.")
    except Exception as e:
        print(f"{Fore.RED}Error exporting report: {e}")

def remove_all_expenses():
    """Remove all expenses and reset totals and history to zero."""
    global expenses, expense_history
    for cat in expenses:
        expenses[cat] = 0.0
    expense_history.clear()
    print(f"{Fore.GREEN}All expenses have been removed and totals reset to zero.")

# ---------------------- User Interface ----------------------
def print_menu():
    print(f"\n{Fore.GREEN}{'='*40}")
    print(f"{Fore.GREEN}Personal Expense Tracker")
    print(f"{Fore.GREEN}{'='*40}")
    print(f"{Fore.YELLOW}1. Add Expense")
    print(f"2. View Expenses by Category")
    print(f"3. View Total Expenses")
    print(f"4. Find Highest Spending Category")
    print(f"5. View Expense History")
    print(f"6. Set/View Budgets")
    print(f"7. Monthly Summary")
    print(f"8. Weekly Summary")
    print(f"9. Search Expenses")
    print(f"10. Export Report")
    print(f"11. Remove All Expenses")
    print(f"0. Exit")
    print(f"{Fore.GREEN}{'='*40}")

def get_category_from_input(user_input, categories):
    """
    Convert user input to a valid category name.
    Accepts case-insensitive names or category number (1-based).
    Returns the matched category or None if invalid.
    """
    user_input = user_input.strip()
    if user_input.isdigit():
        idx = int(user_input) - 1
        if 0 <= idx < len(categories):
            return categories[idx]
    for cat in categories:
        if user_input.lower() == cat.lower():
            return cat
    return None

def main():
    load_data_from_file()
    print(f"{Fore.CYAN}Welcome to the Personal Expense Tracker!")
    while True:
        print_menu()
        choice = input(f"{Fore.YELLOW}Select an option: ").strip()
        if choice == '1':
            cat_list = list(expenses.keys())
            print(f"\n{Fore.CYAN}Available categories:")
            for i, c in enumerate(cat_list, 1):
                print(f"  {i}. {c}")
            cat_input = input("Category (name or number): ").strip()
            cat = get_category_from_input(cat_input, cat_list)
            if not cat:
                print(f"{Fore.RED}Invalid category. Please try again.")
                continue
            amt = input("Amount: ").strip()
            desc = input("Description (optional): ").strip()
            msg = add_expense(cat, amt, desc)
            print(msg)
            save_data_to_file()
        elif choice == '2':
            view_expenses_by_category()
        elif choice == '3':
            calculate_total_expenses()
        elif choice == '4':
            find_highest_spending_category()
        elif choice == '5':
            print(f"\n{Fore.CYAN}Filter by category? (leave blank for all)")
            cat = input("Category: ").strip()
            cat = cat if cat else None
            print(f"Filter by date range? (YYYY-MM-DD)")
            start = input("Start date (leave blank): ").strip()
            end = input("End date (leave blank): ").strip()
            start = start if start else None
            end = end if end else None
            view_expense_history(cat, start, end)
        elif choice == '6':
            print(f"\n{Fore.CYAN}1. Set Budget\n2. View Budgets")
            sub = input("Select: ").strip()
            if sub == '1':
                cat_list = list(budgets.keys())
                print(f"\n{Fore.CYAN}Available categories:")
                for i, c in enumerate(cat_list, 1):
                    print(f"  {i}. {c}")
                cat_input = input("Category (name or number): ").strip()
                cat = get_category_from_input(cat_input, cat_list)
                if not cat:
                    print(f"{Fore.RED}Invalid category. Please try again.")
                    continue
                amt = input("Budget amount: ").strip()
                set_budget(cat, amt)
                save_data_to_file()
            else:
                view_budgets()
        elif choice == '7':
            y = input("Year (YYYY): ").strip()
            m = input("Month (1-12): ").strip()
            try:
                y = int(y)
                m = int(m)
                monthly_summary(y, m)
            except ValueError:
                print(f"{Fore.RED}Invalid year or month.")
        elif choice == '8':
            y = input("Year (YYYY): ").strip()
            w = input("Week number (1-53): ").strip()
            try:
                y = int(y)
                w = int(w)
                weekly_summary(y, w)
            except ValueError:
                print(f"{Fore.RED}Invalid year or week.")
        elif choice == '9':
            kw = input("Keyword to search: ").strip()
            search_expenses(kw)
        elif choice == '10':
            fname = input("Filename (default: expense_report.txt): ").strip()
            fname = fname if fname else "expense_report.txt"
            export_report(fname)
        elif choice == '11':
            confirm = input(f"{Fore.RED}Are you sure you want to remove ALL expenses? This cannot be undone. (y/n): ").strip().lower()
            if confirm == 'y':
                remove_all_expenses()
                save_data_to_file()
        elif choice == '0':
            print(f"{Fore.CYAN}Saving data and exiting...")
            save_data_to_file()
            print(f"{Fore.GREEN}Goodbye!")
            calculate_total_expenses()
            break
        else:
            print(f"{Fore.RED}Invalid selection. Please try again.")

if __name__ == "__main__":
    main()
