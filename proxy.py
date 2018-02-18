import socket, sys, signal
import _thread
import ssl, smtplib

global numbers
blocked = []

# Function to initialise sockets, ports etc.
def init(number):

    max_no_connections = 5
    continueOn = True


    buffer_size = 4096  # max number of bytes that can be received at once


    host = "0.0.0.0"
    port = 8080
    print("Serving on: " + str(port))

    # Shutdown on Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket


    try:
        s.bind((host, port))                               # binds to listener

    except socket.error as e:                              # error-checking
        print(str(e))

    s.listen(max_no_connections)  # enables to server to accept up to 5 connections

    while number <= max_no_connections and continueOn:
        if (number < max_no_connections):
            number = number + 1
            conn, client_address = s.accept()  # accepts a connection, conn becomes new socket obj

            # create thread to handle request
            _thread.start_new_thread(threading, (conn, client_address, buffer_size))

            print("New connection. Total number of connections: " + str(number))

def signal_handler(signal, frame):
    print("Interruption.")
    sys.exit(0)

# function to handle request from browser
def threading(conn, client_address, buffer_size):

    # get data from client address
    data = conn.recv(buffer_size)

    # parse the first line
    first_line = data.decode().split('\n')[0]
    print(first_line)
    # get URL
    url = first_line.split(' ')[1]

    for i in range(0,len(blocked)):
        if blocked[i] in url:
            print("Blocked: ", first_line, client_address)
            conn.close()
            sys.exit(1)


    print("Request: ", first_line, client_address)

    # get webserver and port
    http_position = url.find("://")

    if(http_position==-1):
        temp = url
    else:
        # get the rest of the URL
        temp = url[(http_position+3):]

    # find the port position if any
    port_position = temp.find(":")

    #find end of web server
    webserver_position = temp.find("/")
    if webserver_position == -1:
        webserver_position = len(temp)

    webserver = ""
    port = -1

    # default port
    if(port_position == -1 or webserver_position < port_position):
        port = 80
        webserver = temp[:webserver_position]
    else:
        port = int((temp[(port_position+1):])[:webserver_position-port_position-1])
        webserver = temp[:port_position]

    print("Connect to: ", webserver, port)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((webserver,port))
    s.send(data)

    while True:
        server_data = s.recv(buffer_size)

        if(len(server_data)>0):
            conn.send(server_data)

        else:
            break

    s.close()
    conn.close()

def main():
    number = 0
    while True:
        intro = input("Would you like to start your proxy server? y/n \n")
        if(intro == "y"):
            init(number)
        elif(intro == "n"):
            print("The program will now exit.")
            sys.exit()
        else:
            print("Please type y/n.")

if __name__ == '__main__':
    main()