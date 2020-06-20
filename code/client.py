from socket import *
import sys
import pickle

INPUT_NUM = 4

def negotiaitonTCP(server_address, n_port, req_code):
    '''Negotiation Phase communication over TCP

    Parameters:
    server_address -- the server address
    n_port -- negotiation port number of the server
    req_code -- request code for negotiation

    Returns:
    r_port -- random port number of the transaction
    '''

    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_address, n_port))

    client_socket.send(str(req_code).encode())
    r_port = int(client_socket.recv(1024).decode())
    client_socket.close()
    
    return r_port

def transactionUDP(server_address, r_port, msg):
    '''Transaction Phase communication over UDP

    Parameters:
    server_address -- the server address
    r_port -- random port number of the transaction
    msg -- the message to be sent

    Returns:
    None 
    '''

    client_socket = socket(AF_INET, SOCK_DGRAM)

    client_socket.sendto("GET".encode(),(server_address, r_port))
    messages, _ = client_socket.recvfrom(2048)
    message_list = eval(messages.decode())
    print(*message_list, sep = "\n")

    client_socket.sendto(msg.encode(), (server_address, r_port))

    input("Press Enter to continue...")
    client_socket.close()

def log_port(r_port, msg):
    '''Write the line <r_port> to that file with the messages in order

    Parameters:
    r_port -- random port number of the transaction
    msg -- the message to be sent

    Returns:
    None
    '''

    existed = False

    file = open("client.txt", "a+")

    try:
        for line in file:
            crt_port = line.split(":")[0]
            if crt_port == r_port:
                existed = True
                break
        
        if existed == False:
            next_line = str(r_port) + ": " + str(msg) + "\n"
            file.write(next_line)
    finally:
        file.close()

def main():
    if len(sys.argv) - 1 == INPUT_NUM:
        server_address = sys.argv[1]
        n_port = int(sys.argv[2])
        req_code = int(sys.argv[3])
        msg = str(sys.argv[4])
    else:
        print("Invalid Arguments: should input " + INPUT_NUM + " parameters")
        quit()
    
    r_port = negotiaitonTCP(server_address, n_port, req_code)

    if r_port == 0:
        print("Invalid req_code")
        quit()
    
    transactionUDP(server_address, r_port, msg)

    log_port(r_port, msg)

if __name__ == "__main__":
    main()