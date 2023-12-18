import socket
import struct
import os
import time

IP = socket.gethostbyname(socket.gethostname())
PORT = 5555
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024


def summary_tcp(client, concatenated_data_hex):
    client.send(concatenated_data_hex)
    response = client.recv(SIZE).decode(FORMAT)
    return response

def summary_udp(client, concatenated_data_hex, server_addr):
    client.sendto(concatenated_data_hex, server_addr)
    response, _ = client.recvfrom(SIZE)
    return response.decode(FORMAT)

def summary(client, filename, opcode_filename_length_byte, filename_bytes, protocol_choice, server_addr):
    concatenated_data = opcode_filename_length_byte + filename_bytes
    concatenated_data_hex = ' '.join(format(byte, '02X') for byte in concatenated_data)

    if protocol_choice == "TCP":
        response = summary_tcp(client, concatenated_data_hex.encode(FORMAT))
    elif protocol_choice == "UDP":
        response = summary_udp(client, concatenated_data_hex.encode(FORMAT), server_addr)
    else:
        print("Invalid protocol choice.")
        return
    
    if response == "FileExists":
        file_size = int(client.recv(SIZE).decode())

        received_data = b""
        total_bytes_received = 0

        while total_bytes_received < file_size:
            data = client.recv(SIZE)
            received_data += data
            total_bytes_received += len(data)

        with open("client_data/" + filename + "_summary", "wb") as file:
            sum_filename = filename + "_summmary"
            file.write(received_data)
        print(f"[CLIENT]: File '{sum_filename}' Received And Saved.\n")
    else:
        print(f"[CLIENT]: File '{filename}' Does Not Exist On Server.\n") 




def put_tcp(client, data):
    client.sendall(data)

def put_udp(client, data, server_addr):
    client.sendto(data, server_addr)
    #print(data)


def put(client, filename, opcode_filename_length_byte, filename_bytes, file_size_bytes, protocol_choice, server_addr):
    try:
        concatenated_data = opcode_filename_length_byte + filename_bytes + file_size_bytes
        concatenated_data_hex = ' '.join(format(byte, '02X') for byte in concatenated_data)

        if protocol_choice == "TCP":
            put_tcp(client, concatenated_data_hex.encode(FORMAT))
        elif protocol_choice == "UDP":
            put_udp(client, concatenated_data_hex.encode(FORMAT), server_addr)
        
        file_size = struct.unpack('>I', file_size_bytes)[0]
        file_path = "client_data/" + filename

        time.sleep(1)
        total_bytes_sent = 0
        with open(file_path, "rb") as file:
            while total_bytes_sent < file_size:
                data = file.read(SIZE)
                if protocol_choice == "TCP":
                    client.sendall(data)
                elif protocol_choice == "UDP":
                    client.sendto(data, server_addr)
                total_bytes_sent += len(data)

        if total_bytes_sent == file_size:
            print("File Sent Successfully.")
        else:
            print("File Sending Incomplete.")

        if protocol_choice == "TCP":
            msg = client.recv(SIZE).decode(FORMAT)
            print(f"[SERVER]: {msg}")
        elif protocol_choice == "UDP":
            response, _ = client.recvfrom(SIZE)
            print(f"[SERVER]: {response.decode(FORMAT)}")
            
    except FileNotFoundError:
        print(f"[CLIENT]: File '{filename}' Not Found.")

def change_udp(client, data, server_addr):
    client.sendto(data, server_addr)
    response, _ = client.recvfrom(SIZE)
    print(f"[SERVER]: {response.decode(FORMAT)}")

def change_tcp(client, data):
    client.sendall(data)
    response = client.recv(SIZE).decode(FORMAT)
    print(f"[SERVER]: {response}")   

def change(client, opcode_to_byte, old_name_bytes, new_to_name, new_name_bytes, protocol_choice, server_addr):
    concatenated_data = opcode_to_byte + old_name_bytes + new_to_name + new_name_bytes
    concatenated_data_hex = ' '.join(format(byte, '02X') for byte in concatenated_data)
    #print(concatenated_data_hex)

    if protocol_choice == "TCP":
            put_tcp(client, concatenated_data_hex.encode(FORMAT))
            msg = client.recv(SIZE).decode(FORMAT)
            print(f"[SERVER]: {msg}")
    elif protocol_choice == "UDP":
            put_udp(client, concatenated_data_hex.encode(FORMAT), server_addr)
            response, _ = client.recvfrom(SIZE)
            print(f"[SERVER]: {response.decode(FORMAT)}")

def get_tcp(client, concatenated_data_hex):
    client.send(concatenated_data_hex)
    response = client.recv(SIZE).decode(FORMAT)
    return response

def get_udp(client, concatenated_data_hex, server_addr):
    client.sendto(concatenated_data_hex, server_addr)
    response, _ = client.recvfrom(SIZE)
    return response.decode(FORMAT)

def get(client, filename, opcode_filename_length_byte, filename_bytes, protocol_choice, server_addr):
    concatenated_data = opcode_filename_length_byte + filename_bytes
    concatenated_data_hex = ' '.join(format(byte, '02X') for byte in concatenated_data)
    # print(concatenated_data_hex)

    if protocol_choice == "TCP":
        response = get_tcp(client, concatenated_data_hex.encode(FORMAT))
    elif protocol_choice == "UDP":
        response = get_udp(client, concatenated_data_hex.encode(FORMAT), server_addr)
    else:
        print("Invalid protocol choice.")
        return

    if response == "FileExists":
        file_size = int(client.recv(SIZE).decode())

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
    protocol_choice = input("Choose Protocol (TCP or UDP): ").upper()
    print()

    ip = IP if user_input_ip == "" else user_input_ip
    port = PORT if user_input_port == "" else int(user_input_port)

    ADDR = (ip, port)

    setup = "setup/setup.txt"
    connected = False
    with open(setup, 'w') as file:
        file.write(f"{ip} {port} {protocol_choice}")

    if protocol_choice == "TCP":
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while not connected:
            try:
                client.connect(ADDR)
                connected = True
            except ConnectionRefusedError:
                time.sleep(1)
    elif protocol_choice == "UDP":
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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

                    put(client, filename, opcode_filename_length_byte, filename_bytes, file_size_bytes, protocol_choice, ADDR)

            except FileNotFoundError:
                print(f"[CLIENT]: File '{filename}' Not Found.")


        elif command.startswith("get"):
            parts = command.split()
            if len(parts) == 2:
                filename = parts[1]
                
                # filename length does not exceed 31 characters
                max_filename_length = 31
                if len(filename) > max_filename_length:
                    print(f"File Name Exceeds Maximum Length: ({max_filename_length} Characters).")
                else:
                    # Convert the filename length to binary (maximum of 5 bits)
                    filename_length_binary = format(len(filename), '05b')  # format as a 5-bit binary

                    # Get the filename in bytes
                    filename_bytes = filename.encode('utf-8')  # Encoding the filename string to bytes

                    # Combine opcode (3 bits) and filename length (5 bits) into one byte
                    combined_byte = (0b001 << 5) | int(filename_length_binary, 2)
                    opcode_filename_length_byte = combined_byte.to_bytes(1, byteorder='big')

                    get(client, filename, opcode_filename_length_byte, filename_bytes, protocol_choice, ADDR)

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

                    opcode_byte = (0b010 << 5) | int(old_name_length_binary, 2)
                    new_name = (0b00000000) | int(new_name_length_binary, 2)
                    opcode_to_byte = opcode_byte.to_bytes(1, byteorder='big')
                    new_to_name = new_name.to_bytes(1, byteorder='big')
                    
                    change(client, opcode_to_byte, old_name_bytes, new_to_name, new_name_bytes, protocol_choice, ADDR)
            else:
                response = "Invalid Input Format.\n\tExample: change <oldfilename> <newfilename>"
       
        elif command.startswith("summary"):
            parts = command.split()
            if len(parts) == 2:
                filename = parts[1]

                if filename.endswith(".txt"):
                    # Ensure filename length does not exceed 31 characters
                    max_filename_length = 31
                    if len(filename) > max_filename_length:
                        print(f"File Name Exceeds Maximum Length: ({max_filename_length} Characters).")
                    else:
                        # Convert the filename length to binary (maximum of 5 bits)
                        filename_length_binary = format(len(filename), '05b')  # format as a 5-bit binary

                        # Get the filename in bytes
                        filename_bytes = filename.encode('utf-8')  # Encoding the filename string to bytes

                        # Combine opcode (3 bits) and filename length (5 bits) into one byte
                        combined_byte = (0b011 << 5) | int(filename_length_binary, 2)
                        opcode_filename_length_byte = combined_byte.to_bytes(1, byteorder='big')

                        summary(client, filename, opcode_filename_length_byte, filename_bytes, protocol_choice, ADDR)
                else:
                    print("The file is not a text file.")
                    break   

        elif command == "bye":
            if protocol_choice == "TCP":
                client.send("bye".encode())
                #client.close()
                print("[CLIENT]: Connection Closed.\n")
            elif protocol_choice == "UDP":
                client.sendto("bye".encode(), ADDR)
                #client.close()
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
