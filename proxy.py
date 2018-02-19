import socket, sys, signal
import _thread
from urllib.parse import urlparse

blocked = []

config = {
            "HOST" : "0.0.0.0",
            "PORT" : 8080,
            "MAX_CONNECTIONS" : 20,
            "BUFFER_SIZE" : 4092,     # max number of bytes that can be received at once
         }

# Function to initialise sockets, ports etc.
def init(number):

         # Shutdown on Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    continueOn = True
    print("Serving on: " + str(config['PORT']))

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        # create socket
        s.bind((config['HOST'], config['PORT']))                     # binds to listener
        s.listen(config['MAX_CONNECTIONS'])          # enables to server to accept up to 20 connections

    except socket.error as e:                        # error-checking
        print(str(e))
        print("Failed to initialise socket.")
        sys.exit(1)

    # listens to clients
    while number <= config['MAX_CONNECTIONS'] and continueOn:
        if (number < config['MAX_CONNECTIONS']):
            number = number + 1
            conn, client_address = s.accept()  # accepts a connection, conn becomes new socket obj

            # create thread to handle request
            _thread.start_new_thread(proxy, (conn, client_address, config['BUFFER_SIZE']))


            '''
            while True:
                if(input()==".exit"):
                    sys.exit(3)
                else:
                    break
            '''

            print("New connection. Total number of connections: " + str(number))

    sys.exit()

def signal_handler(signal, frame):
    print("Interruption.")
    sys.exit(0)

# function to handle request from browser
def proxy(conn, client_address, buffer_size):

    data = conn.recv(buffer_size)                # get type of request from browser

    first_line = data.decode().split('\n')[0]    # parse the first line
    url = first_line.split(' ')[1]               # get URL

    type = ""

    if url.startswith("http"):
        type = "http"

    elif url.startswith("https") and first_line=="CONNECT":
        type = "https"

    print(type)


    for i in range(0,len(blocked)):                             # check if site is already blocked
        if blocked[i] in url:
            print("Blocked: ", first_line, client_address)
            conn.close()
            sys.exit(1)


    print("Request: ", first_line, client_address)

    # get webserver and port
    http_position = url.find("://")

    if(http_position==-1):
        temp = url

    elif(type == "http"):
        # get the rest of the URL
        temp = url[(http_position+3):]

    else:
        # get the rest of the URL
        temp = url[(http_position + 4):]


    # find the port position if any
    port_position = temp.find(":")

    #find end of web server
    webserver_position = temp.find("/")
    if webserver_position == -1:
        webserver_position = len(temp)

    webserver = ""
    port = -1

    print(port_position)
    print(webserver_position)

    '''
    parsed_url = urlparse(url)
    if parsed_url.port == -1 or parsed_url.host < parsed_url.port:
        if type == "https":
            port = 443
        else:
            port = 80
        webserver = temp [:webserver_position]

    else:
        port = parsed_url.port
        webserver = temp[:port_position]

    '''

    # THIS NEEDS TO BE FIXED
    # default port
    print(port_position)
    print(webserver_position)


    if(port_position == -1 or webserver_position < port_position):
        if(type == "https"):
            port = 443
        else:
            port = 80
        webserver = temp[:webserver_position]
    else:
        port = int((temp[(port_position+1):])[:webserver_position-port_position-1])
        webserver = temp[:port_position]

    print(port_position)
    print(webserver_position)
    


    print("Connect to: ", webserver, port)

    # create socket to connect to the web server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((webserver,port))
    s.send(data) # send request to web server

    while True:
        try:
            server_data = s.recv(buffer_size)

        except socket.error:
            print("Connection timeout")
            s.close()
            conn.close()

        if(len(server_data)>0):
            conn.send(server_data) # send to browser
        else:
            break



    s.close()
    conn.close()

def block_URL():
    url = input("What URL do you want to block? \n")
    blocked.append(url)
    print(url + " is now blocked.")

def main():
    number = 0
    init(number)

    '''
    while True:
        intro = input("Would you like to start your proxy server? y/n \n")
        if(intro == "y"):
            init(number)
        elif(intro == "n"):
            print("The program will now exit.")
            sys.exit()
        else:
            print("Please type y/n.")
    '''

if __name__ == '__main__':
    main()