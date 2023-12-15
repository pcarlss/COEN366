import socket
import struct
import threading
import os

IP = socket.gethostbyname(socket.gethostname())
PORT = 1234
ADDR = (IP, PORT)
SIZE = 1024

def handle_client_connection(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    while True:
        command = conn.recv(SIZE).decode()
        if not command or command == "bye":
            break

        bytes_list = command.split()
        bytes_data = bytes([int(byte, 16) for byte in bytes_list])

        opcode = bytes_data[0]
        msb = opcode >> 5
        opcode = format(msb, '03b')
        

        if opcode == "000":
            filename_length = bytes_data[0] & 0b00011111
            filename_start = 1
            filename_end = filename_start + filename_length
            filename_bytes = bytes_data[filename_start:filename_end]
            filename = filename_bytes.decode('utf-8')
            file_size_start = filename_end
            file_size_end = file_size_start + 4
            file_size_bytes = bytes_data[file_size_start:file_size_end]

            file_size = struct.unpack('>I', file_size_bytes)[0]

            print(f"\nExtracted Opcode: {opcode}")
            print(f"Extracted Filename Length: {filename_length} bytes")
            print(f"Extracted Filename Bytes: {filename}")
            print(f"Extracted File Size: {file_size} bytes")

            received_data = b""
            total_bytes_received = 0

            while total_bytes_received < file_size:
                data = conn.recv(SIZE)
                received_data += data
                total_bytes_received += len(data)

            # Write the received data to the file
            with open("database/" + filename, "wb") as file:
                file.write(received_data)

            # Send acknowledgment
            conn.send("File received successfully\n".encode())


        elif opcode == "001":
            filename_length = bytes_data[0] & 0b00011111
            filename_start = 1
            filename_end = filename_start + filename_length
            filename_bytes = bytes_data[filename_start:filename_end]
            filename = filename_bytes.decode('utf-8')
            file_size_start = filename_end
            file_size_end = file_size_start + 4
            file_size_bytes = bytes_data[file_size_start:file_size_end]

            print(f"\nExtracted Opcode: {opcode}")
            print(f"Extracted Filename Length: {filename_length} bytes")
            print(f"Extracted Filename Bytes: {filename}")

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

        elif opcode == "010":
            old_name_length = bytes_data[0] & 0b00011111
            old_name_start = 1
            old_name_end = old_name_start + old_name_length
            old_name_bytes = bytes_data[old_name_start:old_name_end]
            oldfilename = old_name_bytes.decode('utf-8')

            new_name_length = bytes_data[old_name_end] & 0b00011111
            new_name_start = old_name_end + 1
            new_name_end = new_name_start + new_name_length
            new_name_bytes = bytes_data[new_name_start:new_name_end]
            newfilename = new_name_bytes.decode('utf-8')

            old_file_path = "database/" + oldfilename
            new_file_path = "database/" + newfilename
            
            if os.path.exists(old_file_path):
                print(f"\nExtracted Opcode: {opcode}")
                print(f"Extracted Filename Length: {old_name_length} bytes")
                print(f"Extracted Filename Bytes: {new_name_length}\n")
                os.rename(old_file_path, new_file_path)
                conn.send("File Renamed\n".encode())
            else:
                conn.send("File Not Found\n".encode())


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
