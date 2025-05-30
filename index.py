import datetime
import random
import time
import os
from getpass import getpass

class Account:
    def __init__(self, card_number, pin, balance=0):
        self.card_number = card_number
        self.pin = pin
        self.balance = balance
        self.transactions = []
        self.failed_attempts = 0
        self.is_blocked = False
    
    def deposit(self, amount):
        if amount <= 0:
            return False, "Invalid deposit amount"
        
        self.balance += amount
        transaction = {
            'type': 'deposit',
            'amount': amount,
            'date': datetime.datetime.now(),
            'balance': self.balance
        }
        self.transactions.append(transaction)
        return True, f"Deposit successful. New balance: ${self.balance:.2f}"
    
    def withdraw(self, amount):
        if amount <= 0:
            return False, "Invalid withdrawal amount"
        if amount > self.balance:
            return False, "Insufficient funds"
        
        self.balance -= amount
        transaction = {
            'type': 'withdrawal',
            'amount': amount,
            'date': datetime.datetime.now(),
            'balance': self.balance
        }
        self.transactions.append(transaction)
        return True, f"Withdrawal successful. New balance: ${self.balance:.2f}"
    
    def get_balance(self):
        return self.balance
    
    def get_transaction_history(self, count=10):
        return self.transactions[-count:]
    
    def change_pin(self, new_pin):
        if len(new_pin) != 4 or not new_pin.isdigit():
            return False, "PIN must be 4 digits"
        
        self.pin = new_pin
        return True, "PIN changed successfully"
    
    def verify_pin(self, pin):
        if self.is_blocked:
            return False, "Card is blocked. Please contact customer service."
        
        if pin == self.pin:
            self.failed_attempts = 0
            return True, "PIN verified"
        else:
            self.failed_attempts += 1
            if self.failed_attempts >= 3:
                self.is_blocked = True
                return False, "Card blocked due to too many failed attempts. Contact customer service."
            return False, f"Incorrect PIN. {3 - self.failed_attempts} attempts remaining"

class ATMSystem:
    def __init__(self):
        self.accounts = {}
        self.current_account = None
        self.admin_pin = "9999"  # Default admin PIN
        self.initialize_demo_accounts()
        self.daily_withdrawal_limit = 500
        self.daily_deposit_limit = 10000
    
    def initialize_demo_accounts(self):
        # Create some demo accounts
        demo_accounts = [
            ("1234567890123456", "1234", 1000),
            ("2345678901234567", "2345", 2500),
            ("3456789012345678", "3456", 500),
            ("4567890123456789", "4567", 10000),
            ("5678901234567890", "5678", 750)
        ]
        
        for card, pin, balance in demo_accounts:
            self.accounts[card] = Account(card, pin, balance)
    
    def authenticate_card(self, card_number):
        if len(card_number) != 16 or not card_number.isdigit():
            return False, "Invalid card number. Must be 16 digits."
        
        if card_number in self.accounts:
            return True, "Card number valid"
        else:
            return False, "Card not found"
    
    def verify_pin(self, card_number, pin):
        account = self.accounts.get(card_number)
        if not account:
            return False, "Account not found"
        
        return account.verify_pin(pin)
    
    def start_session(self, card_number):
        self.current_account = self.accounts.get(card_number)
        return self.current_account is not None
    
    def end_session(self):
        self.current_account = None
    
    def get_current_account(self):
        return self.current_account
    
    def check_daily_limit(self, transaction_type, amount):
        if transaction_type == 'withdrawal':
            today_withdrawals = sum(
                t['amount'] for t in self.current_account.transactions 
                if t['type'] == 'withdrawal' and t['date'].date() == datetime.date.today()
            )
            if today_withdrawals + amount > self.daily_withdrawal_limit:
                return False, f"Daily withdrawal limit exceeded (${self.daily_withdrawal_limit})"
        
        elif transaction_type == 'deposit':
            today_deposits = sum(
                t['amount'] for t in self.current_account.transactions 
                if t['type'] == 'deposit' and t['date'].date() == datetime.date.today()
            )
            if today_deposits + amount > self.daily_deposit_limit:
                return False, f"Daily deposit limit exceeded (${self.daily_deposit_limit})"
        
        return True, "Within daily limits"
    
    def add_new_account(self, card_number, pin, initial_balance=0):
        if len(card_number) != 16 or not card_number.isdigit():
            return False, "Invalid card number. Must be 16 digits."
        if len(pin) != 4 or not pin.isdigit():
            return False, "PIN must be 4 digits."
        if initial_balance < 0:
            return False, "Initial balance cannot be negative."
        if card_number in self.accounts:
            return False, "Card number already exists."
        
        self.accounts[card_number] = Account(card_number, pin, initial_balance)
        return True, "Account created successfully"
    
    def verify_admin(self, pin):
        return pin == self.admin_pin

class ATMInterface:
    def __init__(self):
        self.atm_system = ATMSystem()
        self.current_card = None
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        print("\033[92m")  # Green color
        print("=" * 50)
        print(" " * 15 + "ATM SIMULATION SYSTEM")
        print("=" * 50)
        print("\033[0m")  # Reset color
    
    def display_menu(self, options):
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        print("0. Exit" if 'Exit' not in options else "")
    
    def get_input(self, prompt, mask=False):
        if mask:
            return getpass(prompt)
        return input(prompt)
    
    def card_authentication(self):
        self.clear_screen()
        self.display_header()
        print("Please insert your card (enter card number)")
        print("Enter 'admin' for administrator menu")
        card_number = self.get_input("Card Number: ").strip()
        
        if card_number.lower() == 'admin':
            self.admin_menu()
            return False
        
        valid, message = self.atm_system.authenticate_card(card_number)
        if not valid:
            print(f"\033[91mError: {message}\033[0m")
            time.sleep(2)
            return False
        
        self.current_card = card_number
        return True
    
    def admin_menu(self):
        self.clear_screen()
        self.display_header()
        print("ADMINISTRATOR MENU")
        pin = self.get_input("Enter admin PIN: ", mask=True)
        
        if not self.atm_system.verify_admin(pin):
            print("\033[91mInvalid admin PIN\033[0m")
            time.sleep(2)
            return
        
        while True:
            self.clear_screen()
            self.display_header()
            print("ADMINISTRATOR MENU")
            options = [
                "Add New Account",
                "View All Accounts",
                "Exit Admin Menu"
            ]
            self.display_menu(options)
            
            choice = self.get_input("Enter your choice: ")
            
            if choice == '1':
                self.add_new_account()
            elif choice == '2':
                self.view_all_accounts()
            elif choice == '3' or choice == '0':
                return
            else:
                print("\033[91mInvalid choice. Please try again.\033[0m")
                time.sleep(1)
    
    def add_new_account(self):
        self.clear_screen()
        self.display_header()
        print("ADD NEW ACCOUNT")
        
        while True:
            card_number = self.get_input("Enter 16-digit card number: ").strip()
            if len(card_number) != 16 or not card_number.isdigit():
                print("\033[91mInvalid card number. Must be 16 digits.\033[0m")
                continue
            
            if card_number in self.atm_system.accounts:
                print("\033[91mCard number already exists.\033[0m")
                continue
            break
        
        while True:
            pin = self.get_input("Enter 4-digit PIN: ", mask=True)
            if len(pin) != 4 or not pin.isdigit():
                print("\033[91mPIN must be 4 digits.\033[0m")
                continue
            break
        
        while True:
            initial_balance = self.get_input("Enter initial balance (default 0): ").strip()
            if not initial_balance:
                initial_balance = 0
                break
            try:
                initial_balance = float(initial_balance)
                if initial_balance < 0:
                    print("\033[91mBalance cannot be negative.\033[0m")
                    continue
                break
            except ValueError:
                print("\033[91mInvalid amount. Please enter a number.\033[0m")
        
        success, message = self.atm_system.add_new_account(card_number, pin, initial_balance)
        if success:
            print(f"\033[92m{message}\033[0m")
            print(f"Card Number: {card_number}")
            print(f"PIN: {pin}")
            print(f"Initial Balance: ${initial_balance:.2f}")
        else:
            print(f"\033[91m{message}\033[0m")
        
        self.get_input("\nPress Enter to continue...")
    
    def view_all_accounts(self):
        self.clear_screen()
        self.display_header()
        print("ALL ACCOUNTS\n")
        
        if not self.atm_system.accounts:
            print("No accounts found.")
        else:
            print(f"{'Card Number':<20} {'Balance':<15} {'Status':<10}")
            print("-" * 45)
            for card, account in self.atm_system.accounts.items():
                status = "Blocked" if account.is_blocked else "Active"
                print(f"{card[:4]}********{card[-4:]:<20} ${account.balance:<14.2f} {status:<10}")
        
        self.get_input("\nPress Enter to continue...")
    
    def pin_verification(self):
        attempts = 0
        while attempts < 3:
            self.clear_screen()
            self.display_header()
            print(f"Card: {self.current_card[:4]}********{self.current_card[-4:]}")
            pin = self.get_input("Enter your 4-digit PIN: ", mask=True)
            
            valid, message = self.atm_system.verify_pin(self.current_card, pin)
            if valid:
                self.atm_system.start_session(self.current_card)
                return True
            else:
                print(f"\033[91m{message}\033[0m")
                time.sleep(2)
                attempts += 1
        
        print("\033[91mToo many failed attempts. Your card has been blocked.\033[0m")
        time.sleep(3)
        return False
    
    def main_menu(self):
        while True:
            self.clear_screen()
            self.display_header()
            account = self.atm_system.get_current_account()
            print(f"Card: {self.current_card[:4]}********{self.current_card[-4:]}")
            print("\nMain Menu:")
            options = [
                "Balance Inquiry",
                "Cash Withdrawal",
                "Cash Deposit",
                "Transaction History",
                "Change PIN",
                "Exit"
            ]
            self.display_menu(options)
            
            choice = self.get_input("Enter your choice: ")
            
            if choice == '1':
                self.balance_inquiry()
            elif choice == '2':
                self.cash_withdrawal()
            elif choice == '3':
                self.cash_deposit()
            elif choice == '4':
                self.transaction_history()
            elif choice == '5':
                self.change_pin()
            elif choice == '6' or choice == '0':
                print("Thank you for using our ATM. Goodbye!")
                self.atm_system.end_session()
                time.sleep(2)
                break
            else:
                print("\033[91mInvalid choice. Please try again.\033[0m")
                time.sleep(1)
    
    def balance_inquiry(self):
        self.clear_screen()
        self.display_header()
        account = self.atm_system.get_current_account()
        balance = account.get_balance()
        print(f"Your current balance is: \033[94m${balance:.2f}\033[0m")
        self.get_input("\nPress Enter to return to main menu...")
    
    def cash_withdrawal(self):
        account = self.atm_system.get_current_account()
        
        while True:
            self.clear_screen()
            self.display_header()
            print("Cash Withdrawal")
            print("\nQuick Amounts:")
            quick_amounts = [20, 40, 60, 80, 100, 200]
            for i, amount in enumerate(quick_amounts, 1):
                print(f"{i}. ${amount}")
            print("7. Enter custom amount")
            print("0. Back to main menu")
            
            choice = self.get_input("Enter your choice: ")
            
            if choice == '0':
                return
            
            if choice in ['1', '2', '3', '4', '5', '6']:
                amount = quick_amounts[int(choice)-1]
            elif choice == '7':
                try:
                    amount = float(self.get_input("Enter withdrawal amount: $"))
                    if amount <= 0:
                        print("\033[91mAmount must be positive.\033[0m")
                        time.sleep(1)
                        continue
                except ValueError:
                    print("\033[91mInvalid amount. Please enter a number.\033[0m")
                    time.sleep(1)
                    continue
            else:
                print("\033[91mInvalid choice. Please try again.\033[0m")
                time.sleep(1)
                continue
            
            # Check daily limits
            limit_ok, limit_msg = self.atm_system.check_daily_limit('withdrawal', amount)
            if not limit_ok:
                print(f"\033[91m{limit_msg}\033[0m")
                time.sleep(2)
                continue
            
            # Process withdrawal
            success, message = account.withdraw(amount)
            if success:
                print(f"\033[92m{message}\033[0m")
                print("Please take your cash.")
            else:
                print(f"\033[91m{message}\033[0m")
            
            self.get_input("\nPress Enter to continue...")
            return
    
    def cash_deposit(self):
        account = self.atm_system.get_current_account()
        
        self.clear_screen()
        self.display_header()
        print("Cash Deposit")
        
        try:
            amount = float(self.get_input("Enter deposit amount: $"))
            if amount <= 0:
                print("\033[91mAmount must be positive.\033[0m")
                time.sleep(1)
                return
        except ValueError:
            print("\033[91mInvalid amount. Please enter a number.\033[0m")
            time.sleep(1)
            return
        
        # Check daily limits
        limit_ok, limit_msg = self.atm_system.check_daily_limit('deposit', amount)
        if not limit_ok:
            print(f"\033[91m{limit_msg}\033[0m")
            time.sleep(2)
            return
        
        # Process deposit
        success, message = account.deposit(amount)
        if success:
            print(f"\033[92m{message}\033[0m")
            print("Please insert your cash.")
            # Simulate cash counting
            print("Processing...", end='', flush=True)
            for _ in range(3):
                time.sleep(0.5)
                print(".", end='', flush=True)
            print("\nDeposit processed successfully.")
        else:
            print(f"\033[91m{message}\033[0m")
        
        self.get_input("\nPress Enter to continue...")
    
    def transaction_history(self):
        account = self.atm_system.get_current_account()
        transactions = account.get_transaction_history()
        
        self.clear_screen()
        self.display_header()
        print("Transaction History (Last 10 transactions)\n")
        
        if not transactions:
            print("No transactions found.")
        else:
            print(f"{'Date':<25} {'Type':<12} {'Amount':<12} {'Balance':<12}")
            print("-" * 60)
            for t in reversed(transactions):
                date_str = t['date'].strftime("%Y-%m-%d %H:%M:%S")
                print(f"{date_str:<25} {t['type']:<12} ${t['amount']:<11.2f} ${t['balance']:<11.2f}")
        
        self.get_input("\nPress Enter to return to main menu...")
    
    def change_pin(self):
        account = self.atm_system.get_current_account()
        
        self.clear_screen()
        self.display_header()
        print("Change PIN")
        
        # Verify current PIN first
        current_pin = self.get_input("Enter current PIN: ", mask=True)
        valid, message = account.verify_pin(current_pin)
        if not valid:
            print(f"\033[91m{message}\033[0m")
            time.sleep(2)
            return
        
        # Get new PIN
        new_pin = self.get_input("Enter new 4-digit PIN: ", mask=True)
        confirm_pin = self.get_input("Confirm new PIN: ", mask=True)
        
        if new_pin != confirm_pin:
            print("\033[91mPINs do not match.\033[0m")
            time.sleep(2)
            return
        
        success, message = account.change_pin(new_pin)
        if success:
            print(f"\033[92m{message}\033[0m")
        else:
            print(f"\033[91m{message}\033[0m")
        
        time.sleep(2)
    
    def run(self):
        while True:
            if self.card_authentication():
                if self.pin_verification():
                    self.main_menu()
            
            # After session ends or authentication fails
            self.current_card = None
            choice = input("\nWould you like to start a new session? (y/n): ").lower()
            if choice != 'y':
                print("Thank you for using our ATM. Goodbye!")
                break

if __name__ == "__main__":
    atm = ATMInterface()
    atm.run()