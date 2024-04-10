import socket
import threading
import pickle

def main():
    # initialize list of users and confirmed transactions
    users = []
    
    # class definitions for transactions and users
    class Transaction:
        def __init__(self, tx_id, payer, amount_transferred, payee1, amount_received1, payee2=None, amount_received2=None, status=None):
            self.tx_id = tx_id
            self.payer = payer
            self.amount_transferred = amount_transferred
            self.payee1 = payee1
            self.amount_received1 = amount_received1
            self.payee2 = payee2
            self.amount_received2 = amount_received2
            self.status = status
            
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
                
    def get_username(users, current_username):
        for user in users:
            if user.username == current_username:
                return user
        return None
        
    def get_all_usernames_except_current(users, current_username):
        return [user.username for user in users if user.username != current_username]       
        
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
            
            #login authentication
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
                # login successful
                # send a success message back to the client along with the user's balance and transaction history
                response = {
                    "message": "Authentication successful",
                    "balance": user.balance,
                    "transactions": [t for t in user.transactions if t["payer"] == username or t["payee1"] == username or (t["payee2"] and t["payee2"] == username) and t["status"] == "confirmed"]                }
                client_socket.send(pickle.dumps(response))
                # 
                while True:
                    request = client_socket.recv(1024)
                    if not request:
                        break  # client disconnected
                    data = pickle.loads(request)
                    
                    # ============= TRANSACTION HANDLING =============
                    # check data being sent via socket, run functions based on passed data
                    # if user selects option 1 "transaction":
                    if data['action'] == 'transaction':
                        print(f"Received a transaction request from {username}")
                        # handle transaction
                        transaction = data['transaction']
                        payer = get_username(users, transaction['payer'])
                        payee1 = get_username(users, transaction['payee1'])
                        payee2 = get_username(users, transaction['payee2']) if 'payee2' in transaction else None
                        # check payer balance
                        if payer.balance < transaction['amount_transferred']:
                            # if balance is insufficient, update transaction status to failed
                            response = {
                                "status": "rejected", 
                                "balance": payer.balance,
                                "message": "Transaction rejected due to insufficient balance."
                                }
                            payer.update_transaction_status(transaction['tx_id'], "rejected")
                        else:
                            payer.balance -= transaction['amount_transferred']
                            payee1.balance += transaction['amount_received1']
                            if payee2:
                                payee2.balance += transaction['amount_received2']
                            payer.add_transaction(transaction)
                            response = {
                                "status": "confirmed", 
                                "balance": payer.balance,
                                "message": f"Transaction successful. User {payer.username} balance: {payer.balance}."
                                }
                            payer.update_transaction_status(transaction['tx_id'], "confirmed")
                        client_socket.send(pickle.dumps(response))
                        print(f"Sent transaction status to {user.username}")
                    # if user selects option 2 "get_transactions", show all CONFIRMED transactions
                    # as we are showing unconfirmed/failed txns on client side only
                    elif data['action'] == 'add_confirmed_transaction':
                        print(f"Received a confirmed transaction from {username}")
                        transaction = data['transaction']
                        user = get_username(transaction['payer'])
                        user.add_transaction(transaction)
                        print(f"Added transaction {transaction['tx_id']} to confirmed transactions")
                    elif data["action"] == "update_transaction_status":
                        # find the user
                        for user in users:
                            if user.username == request["username"]:
                                # update the transaction status
                                user.update_transaction_status(request["tx_id"], request["status"])
                                break
                    elif data['action'] == 'fetch_transactions':
                        username = data['username']
                        user = get_username(users, username)
                        if user:
                            # send the user's current balance and transactions
                            s.send(pickle.dumps({"balance": user.balance, "transactions": user.transactions}))
                        else:
                            # send an error message if the user is not found
                            s.send(pickle.dumps({"error": "User not found"}))

            else:
                # send an error message back to the client
                response = {"message": "Authentication failed."}
                if user is not None:
                    print(f"Authentication failed for {user.username}")
                else:
                    print("Authentication failed.")
                client_socket.send(pickle.dumps(response))
    while True:
        client, addr = s.accept()
        
        print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))
        
        # spin up our client thread to handle incoming data
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

if __name__ == "__main__":
    main()