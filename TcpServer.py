import threading
import socket
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

socket_list = []
socket_list_lock = threading.Lock()

def read_from_client(client_socket):
    try:
        data = client_socket.recv(1024)
        if data:
            return data.decode('utf-8')
        else:
            return None
    except Exception as e:
        logging.error(f"Error reading from client: {e}")
        return None

def server_target(client_socket, client_address):
    try:
        while True:
            content = read_from_client(client_socket)
            if content is None:
                break

            length = len(content)
            if length > 0:
                logging.info(f"Received from {client_address}: {content}")

                try:
                    message = json.loads(content)
                    if message.get("msgtype") == "heart":
                        response = json.dumps({"msgtype": "heart"}) + " from server"
                    else:
                        response = "Unknown message type"
                except json.JSONDecodeError:
                    response = "Invalid JSON"

                logging.info(f"Sent to {client_address}: {response}")
                client_socket.send(response.encode('utf-8'))
    except IOError as e:
        logging.error(f"IOError from {client_address}: {e.strerror}")
    finally:
        with socket_list_lock:
            if client_socket in socket_list:
                socket_list.remove(client_socket)
        client_socket.close()
        logging.info(f"Connection closed for {client_address}")

def accept_connections(server_socket):
    while True:
        client_socket, client_address = server_socket.accept()
        with socket_list_lock:
            socket_list.append(client_socket)
        threading.Thread(target=server_target, args=(client_socket, client_address)).start()

def main():
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 9999))
    server_socket.listen()
    logging.info("Server started on port 9999")

    accept_connections(server_socket)

if __name__ == "__main__":
    main()
