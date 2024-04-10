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
    # get the next transaction ID
    tx_id = user.get_next_tx_id()

    # get the amount to transfer
    amount_transferred = input("How much do you want to transfer? ")
    while not amount_transferred.isdigit():
        print("Invalid input. Please enter a number.")
        amount_transferred = input("How much do you want to transfer? ")
    amount_transferred = int(amount_transferred)

    # get Payee1
    payee_options = [chr(ord('A') + i) for i in range(4) if chr(ord('A') + i) != user.username]
    print("Who will be Payee1?")
    for i, payee in enumerate(payee_options, start=1):
        print(f"{i}.{payee}")
    payee1_choice = input()
    while not payee1_choice.isdigit() or int(payee1_choice) < 1 or int(payee1_choice) > len(payee_options):
        print("Invalid input. Please enter a number corresponding to the options.")
        payee1_choice = input()
    payee1 = payee_options[int(payee1_choice) - 1]

    # get amount received by Payee1
    amount_received1 = input("How much Payee1 will receive? ")
    while not amount_received1.isdigit() or int(amount_received1) > amount_transferred:
        print(f"Invalid input. Please enter a number less than or equal to {amount_transferred}.")
        amount_received1 = input("How much Payee1 will receive? ")
    amount_received1 = int(amount_received1)

    # create the transaction
    transaction = {
        "tx_id": tx_id,
        "payer": user.username,
        "amount_transferred": amount_transferred,
        "payee1": payee1,
        "amount_received1": amount_received1,
        "status": "temporary"
    }

    # if there's remaining amount, get Payee2
    if amount_received1 < amount_transferred:
        payee_options.remove(payee1)
        print("Who will be Payee2?")
        for i, payee in enumerate(payee_options, start=1):
            print(f"{i}.{payee}")
        payee2_choice = input()
        while not payee2_choice.isdigit() or int(payee2_choice) < 1 or int(payee2_choice) > len(payee_options):
            print("Invalid input. Please enter a number corresponding to the options.")
            payee2_choice = input()
        payee2 = payee_options[int(payee2_choice) - 1]

        # calculate amount received by Payee2
        amount_received2 = amount_transferred - amount_received1
        print(f"Payee2 will receive {amount_received2}")

        # add Payee2 to the transaction
        transaction['payee2'] = payee2
        transaction['amount_received2'] = amount_received2

    return transaction

def send_transaction(s, user, transaction):
    
    # add transaction to user list of txns
    user.add_transaction(transaction)
    # send txn to the server
    s.send(pickle.dumps({
        "action": "update_transaction_status",
        "username": user.username,
        "tx_id": transaction["tx_id"],
        "status": transaction["status"]
    }))
    # receive the response from the server
    response = pickle.loads(s.recv(1024))
    # update the user's balance and the transaction status
    user.balance = response['balance']
    transaction['status'] = response['status']

    # if the transaction is confirmed, send it to the server to be added to the list of confirmed transactions
    if transaction['status'] == 'confirmed':
        s.send(pickle.dumps({
            "action": "update_transaction_status",
            "username": user.username,
            "tx_id": transaction["tx_id"],
            "status": transaction["status"]
        }))
    elif transaction['status'] == 'rejected':
        # if the transaction failed, store the failed transaction history on client-side
        user.add_transaction(transaction)
       

    print(f"Transaction {transaction['tx_id']} {response['status']}. Your current balance is {user.balance}.")
    
    #  dont need this anymore lol, just fetching txns from server during login session
# def fetch_and_display_transactions(s, user):
#     # send request to the server
#     s.send(pickle.dumps({"action": "fetch_transactions", "username": user.username}))
#     # receive the response from the server
#     response = pickle.loads(s.recv(1024))
#     # update the user's balance and transactions
#     user.balance = response['balance']
#     user.transactions = response['transactions']
#     # display the transactions
#     for transaction in user.transactions:
#         print(f"Transaction ID: {transaction['tx_id']}")
#         print(f"Payer: {transaction['payer']}")
#         print(f"Amount Transferred: {transaction['amount_transferred']}")
#         print(f"Payee1: {transaction['payee1']}")
#         print(f"Amount Received1: {transaction['amount_received1']}")
#         if 'payee2' in transaction:
#             print(f"Payee2: {transaction['payee2']}")
#             print(f"Amount Received2: {transaction['amount_received2']}")
#         print(f"Status: {transaction['status']}")
#         print("------------------------")
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
        user = User(
            username=username,
            balance=response["balance"],
            transactions=response["transactions"]
        )
        print("=====================================")
        print("Authentication successful")
        print(f"Your balance is {user.balance} BTC")
        print("Your transaction history:")
        print("{:<20} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20}".format('tx_id', 'payer', 'amount_transferred', 'payee1', 'amount_received1', 'payee2', 'amount_received2', 'status'))
        for transaction in user.transactions:
            if transaction['payer'] == user.username or transaction['payee1'] == user.username or (transaction['payee2'] and transaction['payee2'] == user.username):
                print("{:<20} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20}".format(transaction['tx_id'], transaction['payer'], transaction['amount_transferred'], transaction['payee1'], transaction['amount_received1'], transaction.get('payee2', 'N/A'), transaction.get('amount_received2', 'N/A'), transaction.get('status', 'N/A')))    
        return user
    elif response["message"] == "Authentication failed.":
        print("=====================================")
        print("User Authentication failed.")
        print("1. Try again")
        print("2. Exit")
        print("=====================================")
        option = input("Enter option: ")
        if option == "1":
            return login(s)  # recursive call
        else:
            print("Exiting...")
            return None
    else:
        print("Unknown response from server. Exiting...")
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
        print("=====================================")

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
            print(f"Your balance is {user.balance} BTC.")
            print("Your transaction history:")
            print("{:<20} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20}".format('tx_id', 'payer', 'amount_transferred', 'payee1', 'amount_received1', 'payee2', 'amount_received2', 'status'))
            for transaction in user.transactions:
                if transaction['payer'] == user.username or transaction['payee1'] == user.username or (transaction['payee2'] and transaction['payee2'] == user.username):
                    print("{:<20} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20}".format(transaction['tx_id'], transaction['payer'], transaction['amount_transferred'], transaction['payee1'], transaction['amount_received1'], transaction.get('payee2', 'N/A'), transaction.get('amount_received2', 'N/A'), transaction.get('status', 'N/A')))    
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