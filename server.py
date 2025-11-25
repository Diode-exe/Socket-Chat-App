import socket 
from _thread import *
from collections import defaultdict as df
import time
import threading
import logging
import datetime

class Server:
    def __init__(self):
        self.rooms = df(list)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.settimeout(1.0)


    def accept_connections(self, ip_address, port):
        self.server.bind((ip_address, int(port)))
        self.server.listen(100)
        self.server.settimeout(1.0)  # set 1 second timeout

        print(f"Server listening on {ip_address}:{port}...")

        while True:
            try:
                connection, address = self.server.accept()
                print(f"{address[0]}:{address[1]} Connected")
                start_new_thread(self.clientThread, (connection,))
            except socket.timeout:
                pass  # loop back, allows Ctrl+C to work
            except KeyboardInterrupt:
                print("Server shutting down...")
                self.server.close()
                break


    
    def clientThread(self, connection):
        user_id = connection.recv(1024).decode().replace("User ", "")
        room_id = connection.recv(1024).decode().replace("Join ", "")

        if room_id not in self.rooms:
            connection.send("New Group created".encode())
        else:
            connection.send("Welcome to chat room".encode())

        self.rooms[room_id].append(connection)

        while True:
            try:
                message = connection.recv(1024)
                print(f"Received: {str(message.decode())}")  # Debug print
                if message:
                    decoded_msg = message.decode()
                    
                    if decoded_msg == "FILE":
                        self.broadcastFile(connection, room_id, user_id)
                    
                    elif decoded_msg == "!rooms":
                        print("Room list requested")  # Debug print
                        self.sendRoomList(connection)
                    
                    else:
                        message_to_send = "<" + str(user_id) + "> " + decoded_msg
                        self.broadcast(message_to_send, connection, room_id)

                else:
                    self.remove(connection, room_id)
                    break
            except Exception as e:
                print(repr(e))
                print("Client disconnected earlier")
                break
            
    
    def broadcastFile(self, connection, room_id, user_id):
        file_name = connection.recv(1024).decode()
        lenOfFile = connection.recv(1024).decode()
        for client in self.rooms[room_id]:
            if client != connection:
                try: 
                    client.send("FILE".encode())
                    time.sleep(0.1)
                    client.send(file_name.encode())
                    time.sleep(0.1)
                    client.send(lenOfFile.encode())
                    time.sleep(0.1)
                    client.send(user_id.encode())
                except:
                    client.close()
                    self.remove(client, room_id)

        total = 0
        print(file_name, lenOfFile)
        while str(total) != lenOfFile:
            data = connection.recv(1024)
            total = total + len(data)
            for client in self.rooms[room_id]:
                if client != connection:
                    try: 
                        client.send(data)
                        # time.sleep(0.1)
                    except:
                        client.close()
                        self.remove(client, room_id)
        print("Sent")

    def writeToFile(self, connection, room_id, message: str):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("msgLog.txt", "a") as file:
                file.write(f"[{timestamp}] [Room {room_id}] {connection.getpeername()}: {message}\n")
        except Exception as e:
            logging.error(f'Error writing to log file: {e}')

    def broadcast(self, message_to_send, connection, room_id):
        for client in self.rooms[room_id]:
            if client != connection:
                try:
                    client.send(message_to_send.encode())
                    self.writeToFile(connection, room_id, message_to_send)
                except:
                    client.close()
                    self.remove(client, room_id)

    
    def remove(self, connection, room_id):
        if connection in self.rooms[room_id]:
            self.rooms[room_id].remove(connection)

    def sendRoomList(self, connection):
        """Sends the current list of rooms to the client who requested it."""
        try:
            print(f"sendRoomList called. Current rooms: {list(self.rooms.keys())}")  # Debug
            rooms_list = list(self.rooms.keys())
            if rooms_list:
                # Join room names with commas, or any separator you like
                message = "ROOM_LIST:" + ",".join(rooms_list)
            else:
                message = "ROOM_LIST:No rooms available"
            
            print(f"Sending message: '{message}'")  # Debug
            connection.send(message.encode())
            print("Message sent successfully")  # Debug
        except Exception as e:
            print(f"Error sending room list: {e}")

if __name__ == "__main__":
    ip_address = "0.0.0.0"
    port = 12345

    print(f"Server started on IP {ip_address}:{port}")

    s = Server()
    threading.Thread(target=s.accept_connections, args=(ip_address, port), daemon=True).start()

    try:
        while True:
            time.sleep(1)  # keep main thread alive
    except KeyboardInterrupt:
        print("Server shutting down...")
        s.server.close()