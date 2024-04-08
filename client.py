import pickle
import socket

class User:
    tx_start_values = {"A": 100, "B": 200, "C": 300, "D": 400}  # starting transaction ID values for each user

    def __init__(self, username, balance, transactions):
        self.username = username
        self.balance = balance
        self.transactions = transactions

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def update_transaction_status(self, tx_id, status):
        for transaction in self.transactions:
            if transaction["tx_id"] == tx_id:
                transaction["status"] = status
                break

    def get_next_tx_id(self):
        payer_transactions = [t for t in self.transactions if t["payer"] == self.username]
        if payer_transactions:
            return max(t["tx_id"] for t in payer_transactions) + 1
        else:
            return self.tx_start_values[self.username]
        
def create_transaction(user):
    # Collect user input
    payee1 = input("Enter payee1: ")
    amount_received1 = int(input("Enter amount received by payee1: "))
    payee2 = input("Enter payee2: ")
    amount_received2 = int(input("Enter amount received by payee2: "))

    # get the next transaction ID
    tx_id = max([tx['tx_id'] for tx in user.transactions if tx['payer'] == user.username], default=0) + 1
    if tx_id == 1:
        tx_id = {"A": 100, "B": 200, "C": 300, "D": 400}[user.username]

    # get the amount to transfer
    amount_transferred = amount_received1 + (amount_received2 if amount_received2 else 0)

    # create the transaction
    transaction = {
        "tx_id": tx_id,
        "payer": user.username,
        "amount_transferred": amount_transferred,
        "payee1": payee1,
        "amount_received1": amount_received1,
        "payee2": payee2,
        "amount_received2": amount_received2,
        "status": "temporary"
    }
    return transaction

def send_transaction(s, user, transaction):
    # store the transaction in the user's transactions
    user.transactions.append(transaction)

    # send the transaction to the server
    s.send(pickle.dumps({"action": "transaction", "transaction": transaction}))

    # receive the response from the server
    response = pickle.loads(s.recv(1024))

    # update the user's balance and the transaction status
    user.balance = response['balance']
    transaction['status'] = response['status']

    print(f"Transaction {transaction['tx_id']} {response['status']}. Your current balance is {user.balance}.")

# login function to authenticate user
def login(s):
    # prompt user to enter username and password
    username = input("Enter username: ")
    password = input("Enter password: ")

    # send authentication data to server
    auth_data = pickle.dumps({"username": username, "password": password})
    s.send(auth_data)

    # receive response from server
    response = pickle.loads(s.recv(1024))
    if response["message"] == "Authentication successful":
        print("Welcome to your wallet!")
        print(f"Your balance is {response['balance']}")
        print("Your transaction history:")
        print("{:<20} {:<20} {:<20} {:<20} {:<20}".format('tx_id', 'payer', 'amount_transferred', 'payee1', 'amount_received1'))
        for transaction in response['transactions']:
            print("{:<20} {:<20} {:<20} {:<20} {:<20}".format(transaction['tx_id'], transaction['payer'], transaction['amount_transferred'], transaction['payee1'], transaction['amount_received1']))
            
        # create User object with the received data and return it
        user = User(username, response['balance'], response['transactions'])
        return user
    else:
        print("User does not exist")
        print("1. Try again")
        print("2. Exit")
        option = input("Enter option: ")
        if option == "1":
            return login(s)  # recursive call
        else:
            print("Exiting...")
            return None

# function to handle the authenticated session for user, called when user successfully logs in
def handle_authenticated_session(s, user):
    while True:
        # prompt user to select an option
        # each option switch case calls a predefined function
        # keep the code here minimal, allows easier debugging + maintenance/improvements
        print("1. Make a transaction")
        print("2. Fetch and display the list of transactions")
        print("3. Quit the program")
        option = input("Enter option: ")

        if option == "1":
            # call create_transaction function
            transaction = create_transaction(user)
            # append transaction to users list of transactions
            user.add_transaction(transaction)
            # send transaction data to server
            transaction_data = pickle.dumps({"action": "transaction", "transaction": transaction})
            s.send(transaction_data)
            response = pickle.loads(s.recv(1024))
            user.update_transaction_status(transaction["tx_id"], response["status"])
            user.balance = response['balance']  # update user's balance
            print(response["message"])
        elif option == "2":
            # fetch and display transactions
            print("Your transaction history:")
            print("{:<20} {:<20} {:<20} {:<20} {:<20}".format('tx_id', 'payer', 'amount_transferred', 'payee1', 'amount_received1'))
            for transaction in user.transactions:
                print("{:<20} {:<20} {:<20} {:<20} {:<20}".format(transaction['tx_id'], transaction['payer'], transaction['amount_transferred'], transaction['payee1'], transaction['amount_received1']))
        elif option == "3":
            # quit the program
            print("Exiting...")
            s.close()
            return False
        else:
            print("Invalid option. Please try again.")
            
def main():
    # create socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # connect to server
    s.connect(('localhost', 12000))
    
    user = login(s)
    
    # client wallet interface begins here
    if user:
        handle_authenticated_session(s, user)
    else:
        s.close()

if __name__ == "__main__":
    main()