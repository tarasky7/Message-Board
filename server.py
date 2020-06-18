from socket import *
import sys
import pickle
import threading

INPUT_NUM = 1

msg_list = []

TERMINATE = False

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('', 0))

def find_socket(sock_type):
    '''Find a valid port number for socket

    Parameters:
    sock_type -- specify UDP or TCP type

    Returns:
    test_socket -- the socket with random port number
    '''

    test_socket = socket(AF_INET, sock_type)
    test_socket.bind(('', 0))
    return test_socket

def transactionUDP(r_socket, r_port, msg_list):
    '''Transaction phase on server side

    Parameters:
    r_socket -- the UDP socket
    r_port -- the port number
    msg_list -- the list of all messages

    Returns:
    ret_code -- if the message from client is "GET", return 0;
                if it's "TERMINATE", return -1; for others, return 1
    '''

    message, client_address = r_socket.recvfrom(2048)
    msg = message.decode()
    ret_code = 0
    if msg == "GET":
        ret_msg = msg_list.copy()
        ret_msg.append("NO MSG")
        r_socket.sendto(str(ret_msg).encode(), client_address)
    else:
        next_msg = str(r_port) + ": " + str(msg)
        msg_list.append(next_msg)
        if msg == "TERMINATE":
            ret_code = -1
        else:
            ret_code = 1
    
    return ret_code

class ClientThread(threading.Thread):
    def __init__(self, client_address, client_socket, req_code, server_address, n_port):
        threading.Thread.__init__(self)
        self.csocket = client_socket
        self.req_code = req_code
        self.client_address = client_address
        self.server_address = server_address
        self.n_port = n_port
        print("New connection added: ", client_address)
    def run(self):
        msg = ''
        cli_req_code = int(self.csocket.recv(1024).decode())
        if cli_req_code != self.req_code:
            self.csocket.send("0".encode())
            self.csocket.close()
            return
        
        r_socket = find_socket(SOCK_DGRAM)
        r_port = r_socket.getsockname()[1]
        print("r_port is {0}".format(r_port))
        self.csocket.send(str(r_port).encode())
        self.csocket.close()

        ret_code = 0
        while ret_code == 0:
            ret_code = transactionUDP(r_socket, r_port, msg_list)

        if ret_code == -1:
            global TERMINATE
            TERMINATE = True
            link_to_self(self.server_address, self.n_port)

def link_to_self(server_address, n_port):
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_address, n_port))
    client_socket.send("0".encode())
    client_socket.close()

def main():
    if len(sys.argv) - 1 == INPUT_NUM:
        req_code = int(sys.argv[1])
    else:
        print("Invalid Arguments: should input " + INPUT_NUM + " parameters")
        quit()

    hostname = gethostname()
    ip_address = gethostbyname(hostname)
    print(f"Hostname: {hostname}")
    print(f"IP Address: {ip_address}")

    n_port = server_socket.getsockname()[1]

    prompt = "SERVER_PORT: " + str(n_port) + "\n"

    log_file = open("server.txt", "r+")
    try:
        log_file.write(prompt)
    finally:
        log_file.close()

    print(prompt)

    while True:
        server_socket.listen(1)
        connection_socket, addr = server_socket.accept()
        if TERMINATE == True:
            break
        newthread = ClientThread(addr, connection_socket, req_code, ip_address, n_port)
        newthread.start()
    
    server_socket.close()

if __name__ == "__main__":
    main()