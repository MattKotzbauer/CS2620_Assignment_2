import socket
import hashlib
from typing import Optional, Tuple

class Client:
    def __init__(self, host: str = "127.0.0.1", port: int = 50051):
        self.host = host
        self.port = port
        self.sock: Optional[socket.socket] = None
        self._connected = False

    def connect(self) -> bool:
        """Establish a TCP connection to the server."""
        if self._connected:
            return True
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self._connected = True
            return True
        except Exception as e:
            print(f"[CLIENT] Connection failed: {e}")
            self._connected = False
            return False

    def disconnect(self):
        """Gracefully close the connection."""
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except:
                pass
            self.sock.close()
            self.sock = None
        self._connected = False

    def send_request(self, request_content: bytes) -> bytes:
        """
        Send a request to the server and return its response.
        Will automatically connect if not already connected.
        """
        if not self._connected and not self.connect():
            raise ConnectionError("[CLIENT] Could not connect to server.")

        try:
            self.sock.sendall(request_content)
            # For simplicity, read up to 1024 bytes for the response
            response = self.sock.recv(1024)
            return response
        except Exception as e:
            print(f"[CLIENT] Error sending request: {e}")
            self.disconnect()
            raise

    def create_account(self, username: str, password: str) -> str:
        """
        Create a new account.
        Returns the session token (hex string) if successful.
        
        Request (opcode 0x01):
            4 bytes total length + 1 byte opcode + 
            2 bytes username length + n bytes username + 32 bytes hashed password

        Response (opcode 0x02):
            4 bytes total length + 1 byte opcode + 32 bytes session token
        """
        # Hash password
        hashed_password = hashlib.sha256(password.encode()).digest()

        # Build request body
        opcode = bytes([0x01])
        username_bytes = username.encode('utf-8')
        username_len = len(username_bytes).to_bytes(2, byteorder='big')
        packet_body = opcode + username_len + username_bytes + hashed_password

        # Prepend 4-byte total length
        packet_length = len(packet_body).to_bytes(4, byteorder='big')
        request_packet = packet_length + packet_body

        # Send request and parse response
        response = self.send_request(request_packet)
        if len(response) < 4 + 1 + 32:
            raise Exception("[CLIENT] Incomplete response for create_account.")

        resp_opcode = response[4]
        if resp_opcode != 0x02:
            raise Exception(f"[CLIENT] Unexpected opcode in create_account response: {resp_opcode:#04x}")

        # Extract session token (32 bytes)
        session_token = response[5:37]  # 32 bytes after opcode
        return session_token.hex()

    def log_into_account(self, username: str, password: str) -> Tuple[bool, str, int]:
        """
        Log into an existing account.
        Returns (success, session_token_hex, unread_count).
        
        Request (opcode 0x03):
            4 bytes total length + 1 byte opcode + 
            2 bytes username length + n bytes username + 32 bytes hashed password

        Response (opcode 0x04):
            4 bytes total length + 1 byte opcode + 1 byte status + 
            32 bytes session token + 4 bytes unread messages count
        """
        hashed_password = hashlib.sha256(password.encode()).digest()

        opcode = bytes([0x03])
        username_bytes = username.encode('utf-8')
        username_len = len(username_bytes).to_bytes(2, byteorder='big')
        packet_body = opcode + username_len + username_bytes + hashed_password

        packet_length = len(packet_body).to_bytes(4, byteorder='big')
        request_packet = packet_length + packet_body

        response = self.send_request(request_packet)
        if len(response) < 4 + 1 + 1 + 32 + 4:
            raise Exception("[CLIENT] Incomplete response for log_into_account.")

        resp_opcode = response[4]
        if resp_opcode != 0x04:
            raise Exception(f"[CLIENT] Unexpected opcode in log_into_account response: {resp_opcode:#04x}")

        status = response[5]  # 1 byte status
        success = (status == 0x00)

        session_token = response[6:38]  # 32 bytes
        unread_count = int.from_bytes(response[38:42], byteorder='big')

        return (success, session_token.hex(), unread_count)

if __name__ == "__main__":
    # Simple usage example
    client = Client()
    try:
        new_token = client.create_account("alice", "password123")
        print(f"[CLIENT] Created account for alice, token = {new_token[:8]}...")
        
        success, token, unread = client.log_into_account("alice", "password123")
        if success:
            print(f"[CLIENT] Logged in successfully, token={token[:8]}..., unread={unread}")
        else:
            print("[CLIENT] Login failed.")
    finally:
        client.disconnect()

