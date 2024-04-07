import socket
import threading
import pickle

def main():
    # server.py program will store two lists
    # 1) list of users
    users = []
    # 2) list of confirmed transactions (TXs)
    confirmed_transactions = []
    
    # create user class that stores name, password, and current BTC balance
    class User:
        def __init__(self, name, password, balance):
            self.name = name
            self.password = password
            self.balance = balance
            
        def __str__(self):
            return self.name + " " + self.password + " " + str(self.balance)
        
    #predefined users
    users.append(User("A", "A", 10))
    users.append(User("B", "B", 10))
    users.append(User("C", "C", 10))
    users.append(User("D", "D", 10))
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



if __name__ == "__main__":
    main()