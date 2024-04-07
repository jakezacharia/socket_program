import pickle
import socket

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
        for transaction in response['transactions']:
            print(transaction)
        return True
    else:
        print("User does not exist")
        print("1. Try again")
        print("2. Exit")
        option = input("Enter option: ")
        if option == "1":
            return login(s)  # recursive call
        else:
            print("Exiting...")
            return False

def main():
    # create socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # connect to server
    s.connect(('localhost', 12000))
    
    # client wallet interface begins here
    if login(s):
        # continue with authenticated session
        pass  # replace with your code
    else:
        s.close()

if __name__ == "__main__":
    main()