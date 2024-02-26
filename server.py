import socket
import sys
import threading
import signal
from contextlib import closing

# Global connection ID counter
connection_id = 0
lock = threading.Lock()

def handle_signal(signum, frame):
    sys.exit(0)

def handle_connection(conn, addr, file_dir, conn_id):
    global lock
    try:
        conn.settimeout(10)
        data = conn.recv(1024)
        if not data:
            with open(f"{file_dir}/{conn_id}.file", 'wb') as f:
                f.write(b'')
        else:
            with open(f"{file_dir}/{conn_id}.file", 'wb') as f:
                while data:
                    f.write(data)
                    data = conn.recv(1024)
    except socket.timeout:
        with open(f"{file_dir}/{conn_id}.file", 'wb') as f:
            f.write(b'ERROR')
    finally:
        conn.close()

def main(port, file_dir):
    global connection_id
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGQUIT, handle_signal)

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(('0.0.0.0', port))
        sock.listen(10)

        while True:
            conn, addr = sock.accept()
            with lock:
                connection_id += 1
                conn_id = connection_id
            threading.Thread(target=handle_connection, args=(conn, addr, file_dir, conn_id)).start()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stderr.write("ERROR: Invalid arguments\n")
        sys.exit(1)
    try:
        port = int(sys.argv[1])
        file_dir = sys.argv[2]
        main(port, file_dir)
    except ValueError:
        sys.stderr.write("ERROR: Port must be an integer\n")
        sys.exit(1)
