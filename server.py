import socket
import threading
import pickle

def main():
    # initialize list of users and confirmed transactions
    users = []
    confirmed_transactions = []
    
    # class definitions for transactions and users
    class Transaction:
        def __init__(self, tx_id, payer, amount_transferred, payee1, amount_received1, payee2=None, amount_received2=None):
            self.tx_id = tx_id
            self.payer = payer
            self.amount_transferred = amount_transferred
            self.payee1 = payee1
            self.amount_received1 = amount_received1
            self.payee2 = payee2
            self.amount_received2 = amount_received2
            self.status = "temporary"
            
        def __str__(self):
            recievers_str = ", ".join(self.receivers)
            return f"{self.sender} sent {self.amount} to {self.receivers}"

    class User:
        def __init__(self, username, password, balance, transactions):
            self.username = username
            self.password = password
            self.balance = balance
            self.transactions = transactions

        def validate_credentials(self, username, password):
            return self.username == username and self.password == password

        def update_balance(self, amount):
            self.balance += amount

        def add_transaction(self, transaction):
            self.transactions.append(transaction)

        def update_transaction_status(self, tx_id, status):
            for transaction in self.transactions:
                if transaction["tx_id"] == tx_id:
                    transaction["status"] = status
                    break
        
    # predefined users for testing
    # for ease of use, we are setting usernames and passwords to be the same
    users.append(User("A", "A", 10, []))
    users.append(User("B", "B", 10, []))
    users.append(User("C", "C", 10, []))
    users.append(User("D", "D", 10, []))
    
    # initialize socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # binding socket to localhost
    s.bind(('localhost', 12000))
    # listen for incoming connections
    s.listen(1)

    
    def handle_client(client_socket):
        while True:
            request = client_socket.recv(1024)
            if not request:
                break  # client disconnected

            print("[*] Received %s" % request)
            
            # decode the received data
            data = pickle.loads(request)
            
            # extract the username and password from the data
            username = data['username']
            password = data['password']
            
            # check if the user exists and the password is correct
            user = None
            for u in users:
                if u.username == username and u.password == password:
                    user = u
                    break
            
            if user:
                # send a success message back to the client along with the user's balance and transaction history
                response = {"message": "Authentication successful", "balance": user.balance, "transactions": [str(t) for t in user.transactions]}
                client_socket.send(pickle.dumps(response))
                
                # handle the authenticated session
                while True:
                    request = client_socket.recv(1024)
                    if not request:
                        break  # client disconnected
                    
                    data = pickle.loads(request)
                    
                    if data['action'] == 'transaction':
                        print(f"Received a transaction request from {username}")
                        # handle transaction
                        transaction = data['transaction']
                        payee1 = transaction['payee1']
                        amount_received1 = int(transaction['amount_received1'])
                        payee2 = transaction.get('payee2')  # get payee2 if it exists, otherwise None
                        amount_received2 = int(transaction.get('amount_received2'))  # get amount_received2 if it exists, otherwise None

                        # check if the payees exist
                        payee_users = []
                        for payee in [payee1, payee2]:
                            if payee is not None:
                                for u in users:
                                    if u.username == payee:
                                        payee_users.append(u)
                                        break
        
                        if len(payee_users) == len([payee for payee in [payee1, payee2] if payee is not None]):
                            # process the transaction
                            total_amount = amount_received1
                            if amount_received2 is not None:
                                total_amount += amount_received2
                            if user.balance >= total_amount:
                                user.balance -= total_amount
                                for i, payee_user in enumerate(payee_users):
                                    amount_received = amount_received1 if i == 0 else amount_received2
                                    payee_user.balance += amount_received
                                user.add_transaction(transaction)
                                print(f"Transaction {transaction['tx_id']} successful. Your current balance is {user.balance}.")
                                response = {"message": "Transaction successful", "status": "confirmed", "balance": user.balance}
                            else:
                                print(f"Transaction {transaction['tx_id']} failed. Insufficient balance. Your current balance is {user.balance}.")
                                response = {"message": "Transaction failed. Insufficient balance.", "status": "failed", "balance": user.balance}
                        else:
                            response = {"message": "Transaction failed. One or more payees do not exist.", "status": "failed", "balance": user.balance}

                        client_socket.send(pickle.dumps(response))
                        print(f"Sent transaction status to {user.username}")
            else:
                # send an error message back to the client
                response = {"message": "Authentication failed. Please try again."}
                print(f"Authentication failed for {user.username}")
                client_socket.send(pickle.dumps(response))
    while True:
        client, addr = s.accept()
        
        print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))
        
        # spin up our client thread to handle incoming data
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

if __name__ == "__main__":
    main()