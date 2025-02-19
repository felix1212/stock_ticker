import socket

def validate_network(host="www.google.com", port=80, timeout=5):
    try:
        socket.create_connection((host, port), timeout=timeout) # Attempt to create a socket connection to the specified host and port
        return True
    except OSError as e:
        print(f"Network error: {e}")
        return False

