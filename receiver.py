import socket
import time
import datetime

def receive():
    HOST = '0.0.0.0'
    PORT = 5000
    
    server_socket = None
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"Server listening on {HOST}:{PORT}")

        conn, addr = server_socket.accept()
        print(f"Connection established with {addr}")
        
        # Receive file name length (4 bytes)
        file_name_length = int.from_bytes(conn.recv(4), byteorder='big')
        print(f"File name length: {file_name_length}")
        
        # Receive file name
        file_name = conn.recv(file_name_length).decode('utf-8')
        print(f"Receiving file: {file_name}")

        # Create new filename with timestamp
        base_name, ext = file_name.rsplit('.', 1)
        timestamp = datetime.datetime.now().strftime('%m-%d-%y-%H-%M-%S')
        new_file_name = f"{base_name}_{timestamp}.{ext}"
        print(f"Saving as: {new_file_name}")

        # Receive file size (8 bytes)
        file_size = int.from_bytes(conn.recv(8), byteorder='big')
        print(f"File size: {file_size} bytes")

        # Receive file data
        bytes_received = 0
        with open(new_file_name, 'wb') as f:
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

# if __name__ == "__main__":
#     receive()