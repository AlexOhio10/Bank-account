import sys
from datetime import datetime

# Impor modul yang sesuai dengan sistem operasi
if sys.platform == 'win32':
    import msvcrt
else:
    import termios
    import tty

def get_masked_input(prompt=""):
    """Helper function to read input and display asterisks (*) cross-platform (Windows & macOS/Linux)."""
    print(prompt, end="", flush=True)
    chars = []
    
    if sys.platform == 'win32':
        while True:
            key = msvcrt.getch()
            if key in {b'\r', b'\n'}:
                print()
                break
            elif key == b'\x08':  # Backspace on Windows
                if chars:
                    chars.pop()
                    print('\b \b', end='', flush=True)
            else:
                try:
                    char_str = key.decode('utf-8')
                    chars.append(char_str)
                    print('*', end='', flush=True)
                except UnicodeDecodeError:
                    pass
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in ('\r', '\n'):
                    print('\r\n', end='', flush=True)
                    break
                elif ch in ('\x7f', '\b'):  # Backspace on macOS/Linux
                    if chars:
                        chars.pop()
                        print('\b \b', end='', flush=True)
                elif ch == '\x03':  # Ctrl+C handling
                    raise KeyboardInterrupt
                else:
                    chars.append(ch)
                    print('*', end='', flush=True)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
    return "".join(chars)

class BankAccount:
    total_accounts = 0

    def __init__(self, name, fingerprint_id):
        self.name = name
        self.__fingerprint_id = fingerprint_id  # Storing the "fingerprint" credential
        self.__balance = 0
        self.history = []
        self.failed_attempts = 0
        self.is_locked = False

        BankAccount.total_accounts += 1
        self.account_number = BankAccount.total_accounts

    def verify_fingerprint(self, fingerprint_id):
        if self.is_locked:
            print("Account is locked due to too many failed biometric scans.")
            return False

        if fingerprint_id == self.__fingerprint_id:
            self.failed_attempts = 0
            return True
        else:
            self.failed_attempts += 1
            remaining = 3 - self.failed_attempts
            if self.failed_attempts >= 3:
                self.is_locked = True
                print("Too many failed scans! Your account has been locked.")
            else:
                print(f"Fingerprint mismatch. {remaining} attempt(s) remaining before lockout.")
            return False

    def deposit(self, amount):
        if round(amount, 2) != amount:
            print("Invalid amount. Only 2 decimal places are allowed.")
            return

        if amount > 0:
            self.__balance += amount
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.history.append(f"[{timestamp}] Deposited: +${amount:.2f}")
            print("Deposit successful!")
            print(f"Your new balance is: {self.__balance:.2f}")
        else:
            print("Invalid amount.")

    def withdraw(self, amount):
        if round(amount, 2) != amount:
            print("Invalid amount. Only 2 decimal places are allowed.")
            return

        if amount > 0 and amount <= self.__balance:
            self.__balance -= amount
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.history.append(f"[{timestamp}] Withdrew: -${amount:.2f}")
            print("Withdrawal successful!")
            print(f"Your new balance is: {self.__balance:.2f}")
        else:
            print("Not enough money or invalid amount.")

    def check_balance(self):
        print(f"Your balance is: {self.__balance:.2f}")

    def show_history(self):
        print(f"\n===== TRANSACTION HISTORY FOR {self.name.upper()} =====")
        if not self.history:
            print("No transactions yet.")
        else:
            for transaction in self.history:
                print(transaction)


print("===== CREATE BANK ACCOUNT (BIOMETRIC SETUP) =====")

name = input("Enter your name: ")
print("Please register your fingerprint credential.")
fingerprint = get_masked_input("Scan your fingerprint (enter code/pattern): ")
repeat_fingerprint = get_masked_input("Confirm your fingerprint scan: ")

account = None

if fingerprint != repeat_fingerprint:
    print("Fingerprint scans do not match!")
    print("Account was not created.")
elif len(fingerprint) < 4:
    print("Fingerprint credential is too short. Must be at least 4 characters.")
    print("Account was not created.")
else:
    account = BankAccount(name, fingerprint)
    print("\nAccount created successfully with biometric registration!")
    print("Welcome,", account.name)
    print("Your account number is:", account.account_number)

# Proceed to login loop only if account was successfully created
if account:
    login_successful = False

    while not login_successful and not account.is_locked:
        print("\n===== BIOMETRIC LOGIN =====")
        login_name = input("Enter your name: ")
        login_fingerprint = get_masked_input("Scan your fingerprint: ")

        # Check name and biometric credentials
        if login_name == account.name and account.verify_fingerprint(login_fingerprint):
            print("\nBiometric authentication successful!")
            print("Welcome back,", account.name)
            login_successful = True

            # Main bank menu loop
            while True:
                print("\n===== BANK MENU =====")
                print("1. Check Balance")
                print("2. Deposit Money")
                print("3. Withdraw Money")
                print("4. View Transaction History")
                print("5. Exit")

                choice = input("Choose an option: ")

                if choice == "1":
                    account.check_balance()

                elif choice == "2":
                    try:
                        amount = float(input("Enter amount to deposit: "))
                        account.deposit(amount)
                    except ValueError:
                        print("Invalid input. Please enter a valid number.")

                elif choice == "3":
                    try:
                        amount = float(input("Enter amount to withdraw: "))
                        account.withdraw(amount)
                    except ValueError:
                        print("Invalid input. Please enter a valid number.")

                elif choice == "4":
                    account.show_history()

                elif choice == "5":
                    print("Thank you for using our bank!")
                    break

                else:
                    print("Invalid choice.")
        else:
            if not account.is_locked:
                print("Authentication failed. Please try scanning again.")

    if account.is_locked:
        print("\nProgram terminated due to biometric lockout.")
else:
    print("\nExiting program due to account creation failure.")
