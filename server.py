import socket
import threading
import pickle

def main():
    # initialize list of users and confirmed transactions
    users = []
    confirmed_transactions = []
    
    # class definitions for transactions and users
    class Transaction:
        def __init__(self, sender, receivers, amount):
            self.sender = sender
            self.receivers = receivers
            self.amount = amount

        def __str__(self):
            recievers_str = ", ".join(self.receivers)
            return f"{self.sender} sent {self.amount} to {self.receivers}"

    class User:
        def __init__(self, name, password, balance):
            self.name = name
            self.password = password
            self.balance = balance
            self.transactions = []  # each user has a list of transactions

        def __str__(self):
            return self.name + " " + self.password + " " + str(self.balance)
        
    # predefined users for testing
    # for ease of use, we are setting usernames and passwords to be the same
    users.append(User("A", "A", 10))
    users.append(User("B", "B", 10))
    users.append(User("C", "C", 10))
    users.append(User("D", "D", 10))
    
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
                if u.name == username and u.password == password:
                    user = u
                    break
            
            if user:
                # send a success message back to the client along with the user's balance and transaction history
                response = {"message": "Authentication successful", "balance": user.balance, "transactions": [str(t) for t in user.transactions]}
                client_socket.send(pickle.dumps(response))
            else:
                # send an error message back to the client
                response = {"message": "Authentication failed. Please try again."}
                client_socket.send(pickle.dumps(response))    
    while True:
        client, addr = s.accept()
        
        print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))
        
        # spin up our client thread to handle incoming data
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()



if __name__ == "__main__":
    main()