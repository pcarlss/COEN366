import socket
import struct
import threading
import os
import time

IP = socket.gethostbyname(socket.gethostname())
PORT = 5555
ADDR = (IP, PORT)
SIZE = 1024

def tcp(conn, addr):
    print(f"\n[NEW CONNECTION] {addr} connected.")

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
                    conn.send(str(file_size).encode()) 

                    while True:
                        file_data = file.read(SIZE)
                        if not file_data:
                            break
                        conn.sendall(file_data) 

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

        elif opcode == "011":
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

            file_path = os.path.join("database", filename)
            if os.path.exists(file_path):
                conn.send("FileExists".encode())

                with open(file_path, "r") as file:
                    numbers = [float(num) for line in file for num in line.split()]
                    if numbers:
                        min_num = min(numbers)
                        max_num = max(numbers)
                        avg_num = sum(numbers) / len(numbers)
                    
                    summary_content = f"Minimum: {min_num}\nMaximum: {max_num}\nAverage: {avg_num}"

                    summary_filename = f"{filename}_summary.txt"
                    with open("database/" + summary_filename, "w") as summary_file:
                        summary_file.write(summary_content)

                    file_path = "database/" + summary_filename
                    summary_file_path = os.path.join("database", summary_filename)
                    with open(summary_file_path, "rb") as summary_file:
                        file_size = os.path.getsize(summary_file_path)
                        conn.send(str(file_size).encode()) 

                    with open(summary_file_path, "rb") as summary_file:
                        while True:
                            file_data = summary_file.read(SIZE)
                            if not file_data:
                                break
                            conn.sendall(file_data)

                    os.remove(summary_file_path)
            else:
                conn.send("FileNotExists".encode())

    conn.close()
    print(f"[DISCONNECTED] {addr} disconnected.\n")
    return main()

def main():
    try:
        os.remove("setup/setup.txt")
    except:
        print()

    print("[STARTING] Server is starting.")
    file_path = "setup/setup.txt"
    while True:
        try:
                with open(file_path, 'r') as file:
                    data = file.read().split()
                    if len(data) != 3:
                        time.sleep(1)
                        continue

                ip = data[0]
                port = int(data[1])
                protocol = data[2].upper()

                ADDR = (ip, port)

                if protocol == "TCP":
                    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server.bind(ADDR)
                    server.listen()
                    print("[LISTENING] Server is listening on:", ADDR)
                    break
                elif protocol == "UDP":
                    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    server.bind(ADDR)
                    print("[BOUND] Server is bound to:", ADDR)
                    break
                else:
                    print("Invalid protocol specified in setup file.")
                    time.sleep(1)
                    continue

        except FileNotFoundError:
             continue

    while True:
        if protocol == "TCP":
            conn, addr = server.accept()
            thread = threading.Thread(target=tcp, args=(conn, ADDR))
            thread.start()
        elif protocol == "UDP":
            data, addr = server.recvfrom(SIZE)
            if data.decode() == "bye":
                break
            else:
                print(f"\n[NEW CONNECTION] {ADDR} connected.")
                #server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                while True:
                    command = data
                    if not command or command == "bye":
                        break
                    
                    hex_bytes = command.decode().split()
                    bytes_data = bytes.fromhex(''.join(hex_bytes))

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
                            data = server.recv(SIZE)
                            received_data += data
                            total_bytes_received += len(data)

                        # Write the received data to the file
                        with open("database/" + filename, "wb") as file:
                            file.write(received_data)

                        # Send acknowledgment
                        server.sendto("File received successfully\n".encode(), addr)
                    


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
                            server.sendto("FileExists".encode(), addr)

                            with open(file_path, "rb") as file:
                                file_size = os.path.getsize(file_path)
                                server.sendto(str(file_size).encode(), addr) 

                                while True:
                                    file_data = file.read(SIZE)
                                    if not file_data:
                                        break
                                    server.sendto(file_data, addr)

                        else:
                            server.sendto("FileNotExists".encode(), addr)

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
                            server.sendto("File Renamed\n".encode(), addr)
                        else:
                            server.sendto("File Not Found\n".encode(), addr)

                    elif opcode == "011":
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

                        file_path = os.path.join("database", filename)
                        if os.path.exists(file_path):
                            server.sendto("FileExists".encode(), addr)

                            with open(file_path, "r") as file:
                                numbers = [float(num) for line in file for num in line.split()]
                                if numbers:
                                    min_num = min(numbers)
                                    max_num = max(numbers)
                                    avg_num = sum(numbers) / len(numbers)
                                
                                summary_content = f"Minimum: {min_num}\nMaximum: {max_num}\nAverage: {avg_num}"

                                summary_filename = f"{filename}_summary.txt"
                                with open("database/" + summary_filename, "w") as summary_file:
                                    summary_file.write(summary_content)

                                file_path = "database/" + summary_filename
                                summary_file_path = os.path.join("database", summary_filename)
                                with open(summary_file_path, "rb") as summary_file:
                                    file_size = os.path.getsize(summary_file_path)
                                    server.sendto(str(file_size).encode(), addr)

                                with open(summary_file_path, "rb") as summary_file:
                                    while True:
                                        file_data = summary_file.read(SIZE)
                                        if not file_data:
                                            break
                                        server.sendto(file_data, addr) 

                                os.remove(summary_file_path)
                        else:
                            server.sendto("FileNotExists".encode(), addr)

                    #server.close()
                    print(f"[DISCONNECTED] {ADDR} disconnected.")
                    break
                
    if protocol == "TCP":
        server.close()  # Close the server socket for TCP
        os.remove("setup/setup.txt")
        print(f"[DISCONNECTED] {ADDR} disconnected.")
        return main()
    elif protocol == "UDP":
        #server.close()  # Close the server socket for UDP
        print(f"[DISCONNECTED] {ADDR} disconnected.")
        os.remove("setup/setup.txt")
        return main()

if __name__ == "__main__":
    main()