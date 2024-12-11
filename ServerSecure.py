import socket
import threading
import time
import pyDes

HOST = '0.0.0.0'
PORT = 59429
wowkey = '1689'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            encrypted_message = client.recv(1024)
            print(encrypted_message)
            decrypted_message = pyDes.triple_des(wowkey.ljust(24)).decrypt(encrypted_message, padmode=2)
            print(decrypted_message)
            broadcast(decrypted_message)
        except:
            index = clients.index(client)
            clients.remove(client)
            nickname = nicknames[index]
            broadcast(f"{nickname} left the server!\n".encode('utf-8'))
            client.close()
            nicknames.remove(nickname)
            break

def send_online_users():
    while True:
        online_users = ", ".join(nicknames)
        message = f"Online Users: {online_users}\n"
        broadcast(message.encode('utf-8'))
        time.sleep(5)  # Update interval

def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}!")
        
        try:
            client.send("NICK".encode('utf-8'))
            nickname = client.recv(1024).decode("utf-8")
        except ConnectionResetError:
            print(f"Connection with {str(address)} was reset by peer.")
            continue
        
        if nickname:
            nicknames.append(nickname)
            clients.append(client)

            print(f"Nickname of the client is {nickname}")
            broadcast(f"{nickname} connected to the server!\n".encode("utf-8"))
            client.send("Connected to server\n".encode("utf-8"))

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()


print("Server Running...")
threading.Thread(target=send_online_users).start()  # Start thread for sending online users
receive()
