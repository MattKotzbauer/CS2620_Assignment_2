import socket
import selectors
import types
import os
import traceback
from typing import Dict

class Server:
    def __init__(self, host: str = "127.0.0.1", port: int = 50051):
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()
        self.sock = None

        # For demo: store credentials and sessions in memory
        # username -> (hashed_password: bytes)
        self.accounts: Dict[str, bytes] = {}
        # username -> (session_token: bytes)
        self.sessions: Dict[str, bytes] = {}
        # For demo: store an arbitrary unread count
        self.user_unread_counts: Dict[str, int] = {}

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        print(f"[SERVER] Listening on {(self.host, self.port)}")
        self.sock.setblocking(False)
        self.sel.register(self.sock, selectors.EVENT_READ, data=None)

    def run(self):
        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self._accept_connection(key.fileobj)
                    else:
                        self._handle_client_socket(key, mask)
        except KeyboardInterrupt:
            print("[SERVER] Keyboard interrupt, shutting down.")
        finally:
            self.sel.close()
            if self.sock:
                self.sock.close()

    def _accept_connection(self, sock: socket.socket):
        conn, addr = sock.accept()
        print(f"[SERVER] Accepted connection from {addr}")
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)

    def _handle_client_socket(self, key: selectors.SelectorKey, mask: int):
        sock = key.fileobj
        data = key.data

        if mask & selectors.EVENT_READ:
            try:
                recv_data = sock.recv(1024)
                if recv_data:
                    data.inb += recv_data
                    self._process_data(sock, data)
                else:
                    print(f"[SERVER] Client {data.addr} disconnected")
                    self._close_connection(sock)
            except Exception as e:
                print(f"[SERVER] Error reading from client: {e}")
                self._close_connection(sock)

        if mask & selectors.EVENT_WRITE:
            if data.outb:
                try:
                    sent = sock.send(data.outb)
                    data.outb = data.outb[sent:]
                except Exception as e:
                    print(f"[SERVER] Error sending to client: {e}")
                    self._close_connection(sock)

    def _close_connection(self, sock: socket.socket):
        try:
            self.sel.unregister(sock)
        except Exception:
            pass
        sock.close()

    def _process_data(self, sock: socket.socket, data: types.SimpleNamespace):
        """
        Continuously parse any complete packets from data.inb.
        Each packet: 4-byte length (N), then N bytes of payload.
        We only handle two opcodes (0x01 for Create Account, 0x03 for Login).
        """
        buffer = data.inb

        while True:
            # Check if we have at least a length field
            if len(buffer) < 4:
                break  # incomplete header

            total_length = int.from_bytes(buffer[:4], byteorder='big')
            if len(buffer) < 4 + total_length:
                break  # we haven't received the full packet yet

            # Extract exactly one packet from the buffer
            packet_content = buffer[4 : 4 + total_length]
            data.inb = buffer[4 + total_length :]  # advance buffer
            buffer = data.inb

            # Process the single packet
            response = self._handle_packet(packet_content)
            if response:
                data.outb += response

    def _handle_packet(self, packet: bytes) -> bytes:
        """
        Dispatch the packet based on the opcode byte.
        Packet layout:
          - byte 0: opcode
          - rest: fields depend on opcode
        """
        if len(packet) < 1:
            return b""

        opcode = packet[0]

        if opcode == 0x01:
            return self._handle_create_account(packet)
        elif opcode == 0x03:
            return self._handle_log_in(packet)
        else:
            print(f"[SERVER] Unrecognized opcode: {opcode:#04x}")
            return b""

    def _handle_create_account(self, packet: bytes) -> bytes:
        """
        Create Account request (opcode 0x01):
          1 byte:  opcode (0x01)
          2 bytes: username length
          N bytes: username (UTF-8)
          32 bytes: hashed password

        Response (opcode 0x02):
          4 bytes: length
          1 byte:  opcode (0x02)
          32 bytes: session token
        """
        if len(packet) < 1 + 2:
            return b""

        username_len = int.from_bytes(packet[1:3], byteorder='big')
        if len(packet) < 1 + 2 + username_len + 32:
            print("[SERVER] Incomplete Create Account packet.")
            return b""

        username_start = 3
        username_end = 3 + username_len
        username = packet[username_start:username_end].decode('utf-8')
        password_hash = packet[username_end : username_end + 32]

        print(f"[SERVER] CreateAccount: username='{username}'")

        if username in self.accounts:
            # If account already exists, let's just generate a random token to mimic "conflict"
            print("[SERVER] Account already exists, but we’ll still send a token (demo).")
        else:
            # Store the account
            self.accounts[username] = password_hash
            self.user_unread_counts[username] = 0

        # Generate a random 32-byte token
        session_token = os.urandom(32)
        self.sessions[username] = session_token

        # Build response
        #   opcode 0x02 + session token
        response_body = bytes([0x02]) + session_token
        length_header = len(response_body).to_bytes(4, byteorder='big')
        return length_header + response_body

    def _handle_log_in(self, packet: bytes) -> bytes:
        """
        Log into Account request (opcode 0x03):
          1 byte:  opcode (0x03)
          2 bytes: username length
          N bytes: username (UTF-8)
          32 bytes: hashed password

        Response (opcode 0x04):
          4 bytes: length
          1 byte:  opcode (0x04)
          1 byte:  status (0x00 = success, 0x01 = fail)
          32 bytes: session token
          4 bytes: unread_count
        """
        if len(packet) < 1 + 2:
            return b""

        username_len = int.from_bytes(packet[1:3], byteorder='big')
        if len(packet) < 1 + 2 + username_len + 32:
            print("[SERVER] Incomplete Log In packet.")
            return b""

        username_start = 3
        username_end = 3 + username_len
        username = packet[username_start:username_end].decode('utf-8')
        password_hash = packet[username_end : username_end + 32]

        print(f"[SERVER] LogIn: username='{username}'")

        status = 0x01  # assume fail
        session_token = bytes(32)  # zero placeholder
        unread_count = 0

        if username in self.accounts and self.accounts[username] == password_hash:
            # Valid login
            status = 0x00
            # Generate fresh session token
            session_token = os.urandom(32)
            self.sessions[username] = session_token
            unread_count = self.user_unread_counts.get(username, 0)
        else:
            print("[SERVER] Invalid credentials for user:", username)

        # Build response
        response_body = bytearray([0x04, status])
        response_body += session_token
        response_body += unread_count.to_bytes(4, byteorder='big')

        length_header = len(response_body).to_bytes(4, byteorder='big')
        return length_header + response_body

if __name__ == "__main__":
    server = Server()
    server.start()
    server.run()

