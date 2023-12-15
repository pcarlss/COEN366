import socket
import threading
import os

IP = socket.gethostbyname(socket.gethostname())
PORT = 1234
ADDR = (IP, PORT)
SIZE = 1024

def handle_client_connection(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    while True:
        data = conn.recv(SIZE).decode()
        if not data:
            break

        parts = data.split()
        command = parts[0]

        if command == "GET":
            if len(parts) == 2:
                filename = parts[1]
                file_path = "database/" + filename
                if os.path.exists(file_path):
                    conn.send("FileExists".encode())

                    with open(file_path, "rb") as file:
                        file_size = os.path.getsize(file_path)
                        conn.send(str(file_size).encode())  # Send file size to client

                        while True:
                            file_data = file.read(SIZE)
                            if not file_data:
                                break
                            conn.sendall(file_data)  # Send file data in chunks

                else:
                    conn.send("FileNotExists".encode())
            else:
                conn.send("InvalidCommand".encode())
        elif command == "PUT":
            filename = conn.recv(SIZE).decode()
            #conn.send("PUT command accepted\n".encode())

            # Receive the file size information
            file_size = int(conn.recv(SIZE).decode())

            received_data = b""
            total_bytes_received = 0

            # Receive and write chunks until the total size matches the file size
            while total_bytes_received < file_size:
                data = conn.recv(SIZE)
                received_data += data
                total_bytes_received += len(data)

            # Write the received data to the file
            with open("database/" + filename, "wb") as file:
                file.write(received_data)

            # Send acknowledgment
            conn.send("File received successfully\n".encode())

    conn.close()
    print(f"[DISCONNECTED] {addr} disconnected.")

def main():
    print("[STARTING] Server is starting.")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print("[LISTENING] Server is listening.")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client_connection, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    main()
