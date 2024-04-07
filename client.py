import socket
import pickle

def main():
    
    # create socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # connect to server
    s.connect(('localhost', 12000))
    
    # client wallet interface begins here
    authenticated = False
    while not authenticated:
        # prompt user to enter username and password
        username = input("Enter username: ")
        password = input("Enter password: ")

        # send authentication data to server
        # pickle the data as a dictionary before sending
        auth_data = pickle.dumps({"username": username, "password": password})
        s.send(auth_data)

        # receive response from server
        response = pickle.loads(s.recv(1024))
        if response == "Authentication successful":
            print("Welcome to your wallet!")
            authenticated = True
        else:
            print("User does not exist")
            
if __name__ == "__main__":
    main()