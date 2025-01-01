import socket
import time
import os


"""DO NOT FORGET TO PUT RECEIVER IP(IPV4)"""

SERVER_IP = "PUT_YOUR_IP"
PORT = 5000

is_sent = False # to check if the file has been sent


def sending(main_path, files_to_send):
    global is_sent
    files_to_send = [main_path + i for i in files_to_send]
    print(f"Files to send in sender function: {files_to_send}")
    while not is_sent:
        time.sleep(1)
        print(f"Sent yet? : {is_sent}")

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((SERVER_IP, PORT))
            print(f"Connected to server {SERVER_IP}:{PORT}")

            # Send the number of files to be sent
            num_files = len(files_to_send)
            client_socket.send(num_files.to_bytes(4, byteorder="big"))

            for file_to_send in files_to_send:
                # Check if file exists
                if not os.path.isfile(file_to_send):
                    print(f"Error: File '{file_to_send}' not found. Skipping.")
                    continue
                # Send file name length as 4 bytes
                file_name_bytes = file_to_send.encode("utf-8")
                client_socket.send(len(file_name_bytes).to_bytes(4, byteorder="big"))

                # Send file name
                client_socket.send(file_name_bytes)

                # Get and send file size as 8 bytes
                file_size = os.path.getsize(file_to_send)
                client_socket.send(file_size.to_bytes(8, byteorder="big"))

                # Send file data
                bytes_sent = 0
                with open(file_to_send, "rb") as f:
                    while chunk := f.read(1024):
                        client_socket.send(chunk)
                        bytes_sent += len(chunk)
                        print(f"Progress: {bytes_sent}/{file_size} bytes")

                print(f"File {file_to_send} sent successfully!")

            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()
            print("Connection closed")
            is_sent = True

        except Exception as e:
            print(f"Error: {e}")
            client_socket.close()
            time.sleep(5)  # Wait before retrying

    print("Exiting Sender Loop!!!")
