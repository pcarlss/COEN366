import socket
import struct
import os
import time

IP = socket.gethostbyname(socket.gethostname())
PORT = 1234
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024

import os

def put(client, filename, opcode_filename_length_byte, filename_bytes, file_size_bytes):
    try:
        # Concatenate the data into a single byte string
        concatenated_data = opcode_filename_length_byte + filename_bytes + file_size_bytes
        concatenated_data_hex = ' '.join(format(byte, '02X') for byte in concatenated_data)
        #print(concatenated_data_hex)

        client.send(concatenated_data_hex.encode(FORMAT))
        
        file_size = struct.unpack('>I', file_size_bytes)[0]
        file_path = "client_data/" + filename

        total_bytes_sent = 0
        with open(file_path, "rb") as file:
            while total_bytes_sent < file_size:
                # Read a chunk of data
                data = file.read(1024)

                # Send the chunk
                client.sendall(data)
                
                # Update the total bytes sent
                total_bytes_sent += len(data)

        # Check if the total bytes sent match the file size
        if total_bytes_sent == file_size:
            print("File Sent Successfully.")
        else:
            print("File Sending Incomplete.")

        # Receive acknowledgement from the server
        msg = client.recv(SIZE).decode(FORMAT)
        print(f"[SERVER]: {msg}")

    except FileNotFoundError:
        print(f"[CLIENT]: File '{filename}' Not Found.")

def change(client, opcode_to_byte, old_name_bytes, new_to_name, new_name_bytes):
    concatenated_data = opcode_to_byte + old_name_bytes + new_to_name + new_name_bytes
    concatenated_data_hex = ' '.join(format(byte, '02X') for byte in concatenated_data)
    #print(concatenated_data_hex)

    client.send(concatenated_data_hex.encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(f"[SERVER]: {response}")

def get(client, filename, opcode_filename_length_byte, filename_bytes):
    concatenated_data = opcode_filename_length_byte + filename_bytes
    concatenated_data_hex = ' '.join(format(byte, '02X') for byte in concatenated_data)
    #print(concatenated_data_hex)

    client.send(concatenated_data_hex.encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)

    if response == "FileExists":
        file_size = int(client.recv(SIZE).decode())  # Receive file size from server

        received_data = b""
        total_bytes_received = 0

        while total_bytes_received < file_size:
            data = client.recv(SIZE)
            received_data += data
            total_bytes_received += len(data)

        with open("client_data/" + filename, "wb") as file:
            file.write(received_data)
        print(f"[CLIENT]: File '{filename}' Received And Saved.\n")
    else:
        print(f"[CLIENT]: File '{filename}' Does Not Exist On Server.\n")   

def main():
    user_input_ip = input("\nEnter IP address (leave empty for default): ")
    user_input_port = input("Enter Port number (Press Enter for default): ")
    print()

    ip = IP if user_input_ip == "" else user_input_ip
    port = PORT if user_input_port == "" else int(user_input_port)

    ADDR = (ip, port)

    setup = "setup/setup.txt"
    connected = False
    with open(setup, 'w') as file:
        file.write(f"{ip} {port}")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while not connected:
        try:
            client.connect(ADDR)
            connected = True
        except ConnectionRefusedError:
            time.sleep(1)

    while True:
        command = input("Enter command: ").lower()

        if command.startswith("put"):
            parts = command.split()
            if len(parts) != 2:
                print("Invalid Input Format.\n\tExample: put test.txt\n")
                continue

            filename = parts[1]
            file_path = "client_data/" + filename

            try:
                if not os.path.exists(file_path):
                    print(f"[CLIENT]: File '{filename}' Not Found. \n")
                    continue

                file_size = os.path.getsize(file_path)
                max_filename_length = 31

                if len(filename) > max_filename_length:
                    print(f"File Name Exceeds Maximum Length: ({max_filename_length} Characters).")
                else:
                    filename_length_binary = format(len(filename), '05b')
                    filename_bytes = filename.encode('utf-8')
                    combined_byte = (0b000 << 5) | int(filename_length_binary, 2)
                    opcode_filename_length_byte = combined_byte.to_bytes(1, byteorder='big')
                    file_size_bytes = struct.pack('>I', file_size)

                    put(client, filename, opcode_filename_length_byte, filename_bytes, file_size_bytes)

            except FileNotFoundError:
                print(f"[CLIENT]: File '{filename}' Not Found.")


        elif command.startswith("get"):
            parts = command.split()
            if len(parts) == 2:
                filename = parts[1]
                
                # Ensure filename length does not exceed 31 characters
                max_filename_length = 31
                if len(filename) > max_filename_length:
                    print(f"File Name Exceeds Maximum Length: ({max_filename_length} Characters).")
                else:
                    # Convert the filename length to binary (maximum of 5 bits)
                    filename_length_binary = format(len(filename), '05b')  # '05b' formats as a 5-bit binary

                    # Get the filename in bytes
                    filename_bytes = filename.encode('utf-8')  # Encoding the filename string to bytes

                    # Combine opcode (3 bits) and filename length (5 bits) into one byte
                    combined_byte = (0b001 << 5) | int(filename_length_binary, 2)
                    opcode_filename_length_byte = combined_byte.to_bytes(1, byteorder='big')

                    get(client, filename, opcode_filename_length_byte, filename_bytes)

        # Inside the main function where command handling occurs
        elif command.startswith("change"):
            parts = command.split()
            if len(parts) == 3:
                old_name = parts[1]
                new_name = parts[2]

                max_filename_length = 31
                if len(new_name) > max_filename_length:
                    print(f"File Name Exceeds Maximum Length ({max_filename_length} Characters).")
                else:
                    # Convert the filename lengths to binary (5 bits each)
                    old_name_length_binary = format(len(old_name), '05b')
                    new_name_length_binary = format(len(new_name), '05b')

                    # Get the filename bytes
                    old_name_bytes = old_name.encode('utf-8')
                    new_name_bytes = new_name.encode('utf-8')

                    # Construct the byte sequence
                    opcode_byte = (0b010 << 5) | int(old_name_length_binary, 2)
                    new_name = (0b00000000) | int(new_name_length_binary, 2)
                    opcode_to_byte = opcode_byte.to_bytes(1, byteorder='big')
                    new_to_name = new_name.to_bytes(1, byteorder='big')
                    
                    change(client, opcode_to_byte, old_name_bytes, new_to_name, new_name_bytes)
            else:
                response = "Invalid Input Format.\n\tExample: change <oldfilename> <newfilename>"

        elif command == "bye":
            client.send("bye".encode(FORMAT))
            client.close()
            print("[CLIENT]: Connection Closed.\n")
            break

        elif command == "help":
            print("\n\n------------------------------------------------------------")
            print("1. put <filename>                        | upload file")
            print("2. get <filename>                        | retrieve file")
            print("3. summary <filename>                    | statistical summary")
            print("4. change <oldfilename> <newfilename>    | rename file")
            print("5. bye                                   | disconnect")
            print("------------------------------------------------------------\n\n")

        else:
            print("Invalid Choice. Please Choose Again.")

    client.close()

if __name__ == "__main__":
    main()
