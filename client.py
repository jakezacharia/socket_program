import socket

def main():
    
    # create socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # connect to server
    s.connect(('localhost', 12000))
    
    ###### TESTING SECTION ######
    ## TESTING DATA TRANSFER TO SERVER
    s.send("Test Data")
    ## RECIEVE DATA FROM SERVER
    response = s.recv(1024)
    print(response)
    ###### TESTING SECTION ######
    
    s.close()    
    
    # create functions here to be called by client, acess server.py, and modify values
    # in this case, we want to create functions for users to access the sever and send/recieve transactions of BTC
    
if __name__ == "__main__":
    main()