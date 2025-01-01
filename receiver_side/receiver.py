import socket
import os


"""Files are gonna be stored in teh received_files folder so we can check and make it globally"""
if not os.path.exists("received_files"):
    os.makedirs("received_files")
saving_dir = "received_files/"


def receive():
    HOST = "0.0.0.0"
    PORT = 5000

    server_socket = None
    while True:
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen(1)
            print(f"Server listening on {HOST}:{PORT}")

            conn, addr = server_socket.accept()
            print(f"Connection established with {addr}")

            # Receive the number of files to be received
            num_files = int.from_bytes(conn.recv(4), byteorder="big")
            print(f"Number of files to receive: {num_files}")

            for _ in range(num_files):
                # Receive file name length (4 bytes)
                file_name_length = int.from_bytes(conn.recv(4), byteorder="big")

                if file_name_length == 0:
                    print("No more files to receive.")
                    break

                # Receive file name
                file_name = conn.recv(file_name_length).decode("utf-8")
                print(f"Receiving file: {file_name}")

                # Create new filename with timestamp (optional)
                base_name, ext = file_name.rsplit(".", 1)
                # timestamp = datetime.datetime.now().strftime('%m-%d-%y-%H-%M-%S')
                new_file_name = f"{base_name}.{ext}"
                new_file_name = (
                    saving_dir + new_file_name.split("/")[-1]
                )  # e.g. /home/sachin/Desktop/all/projects/tyler/fam_12-29-24-20-38-35.mp3
                print(f"Saving as: {new_file_name}")

                # Receive file size (8 bytes)
                file_size = int.from_bytes(conn.recv(8), byteorder="big")
                print(f"File size: {file_size} bytes")

                # Receive file data
                bytes_received = 0
                with open(new_file_name, "wb") as f:
                    while bytes_received < file_size:
                        chunk = conn.recv(min(1024, file_size - bytes_received))
                        if not chunk:
                            break
                        f.write(chunk)
                        bytes_received += len(chunk)
                        print(f"Progress: {bytes_received}/{file_size} bytes")

                print(f"File {new_file_name} received successfully")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            if server_socket:
                try:
                    server_socket.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                server_socket.close()

        print("Restarting server...")


