import grpc
import hashlib
from typing import Optional, Tuple, List

# Protobuf-generated modules (names may vary based on your actual .proto setup)
import exp_pb2
import exp_pb2_grpc


class Client:
    def __init__(self, host: str = "127.0.0.1", port: int = 50051):
        self.host = host
        self.port = port

        # We won't directly manage a socket; gRPC handles it under the hood
        self.channel: Optional[grpc.Channel] = None
        self.stub: Optional[exp_pb2_grpc.MessagingServiceStub] = None
        self._connected = False

    def connect(self) -> bool:
        """Establish a gRPC channel to the server."""
        if self._connected:
            return True
        try:
            # Create an insecure channel (for testing) to the given host/port
            self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
            # Create a stub from the channel
            self.stub = exp_pb2_grpc.MessagingServiceStub(self.channel)

            # Optionally, you can do a quick channel "health check" or wait_for_ready
            grpc.channel_ready_future(self.channel).result(timeout=5)

            self._connected = True
            return True
        except Exception as e:
            print(f"[CLIENT] gRPC connection failed: {e}")
            self._connected = False
            return False

    def disconnect(self):
        """Gracefully close the gRPC channel."""
        if self.channel:
            self.channel.close()
        self.channel = None
        self.stub = None
        self._connected = False

    def _ensure_connected(self):
        """Utility to ensure the client is connected before an RPC call."""
        if not self._connected and not self.connect():
            raise ConnectionError("[CLIENT] Could not connect to gRPC server.")

    # --------------------------------------------------------------------------
    # 0x01: search_username
    # --------------------------------------------------------------------------
    def search_username(self, username: str) -> bool:
        """
        Check if a username is available.
        
        Returns:
            bool: True if available, else False.
        """
        self._ensure_connected()

        # In your proto, you would define something like:
        # rpc SearchUsername(SearchUsernameRequest) returns (SearchUsernameResponse);
        # message SearchUsernameRequest { string username = 1; }
        # message SearchUsernameResponse { bool available = 1; }

        request = exp_pb2.SearchUsernameRequest(username=username)
        response = self.stub.SearchUsername(request)
        return response.available

    # --------------------------------------------------------------------------
    # 0x03: create_account
    # --------------------------------------------------------------------------
    def create_account(self, username: str, password: str) -> str:
        """
        Create a new account.
        
        Returns the session token (hex string) if successful.
        
        Wire Protocol Reference:
            Request (opcode 0x01 in the old code) ...
            Response (opcode 0x02 in the old code) ...
        """
        self._ensure_connected()

        # Hash password to 32 bytes
        hashed_password = hashlib.sha256(password.encode()).digest()

        # In your proto:
        # rpc CreateAccount(CreateAccountRequest) returns (CreateAccountResponse);
        # message CreateAccountRequest { string username = 1; bytes password_hash = 2; }
        # message CreateAccountResponse { bytes session_token = 1; }

        request = exp_pb2.CreateAccountRequest(
            username=username,
            password_hash=hashed_password
        )
        response = self.stub.CreateAccount(request)

        # Convert 32-byte token to hex
        return response.session_token.hex()

    # --------------------------------------------------------------------------
    # 0x05: log_into_account
    # --------------------------------------------------------------------------
    def log_into_account(self, username: str, password: str) -> Tuple[bool, str, int]:
        """
        Log into an existing account.
        
        Returns:
            (success, session_token_hex, unread_count).
        
        Wire Protocol Reference:
            Request (opcode 0x03) ...
            Response (opcode 0x04) ...
        """
        self._ensure_connected()

        hashed_password = hashlib.sha256(password.encode()).digest()

        # In your proto:
        # rpc Login(LoginRequest) returns (LoginResponse);
        # message LoginRequest { string username = 1; bytes password_hash = 2; }
        # message LoginResponse {
        #     enum Status { SUCCESS = 0; FAILURE = 1; }
        #     Status status = 1;
        #     bytes session_token = 2;
        #     uint32 unread_count = 3;
        # }

        request = exp_pb2.LoginRequest(
            username=username,
            password_hash=hashed_password
        )
        response = self.stub.Login(request)

        success = (response.status == exp_pb2.LoginResponse.Status.SUCCESS)
        token_hex = response.session_token.hex()
        unread_count = response.unread_count
        return success, token_hex, unread_count

    # --------------------------------------------------------------------------
    # 0x07: log_out_of_account
    # --------------------------------------------------------------------------
    def log_out_of_account(self, user_id: int, session_token: str) -> None:
        """
        Log out of an account.
        
        Wire Protocol Reference:
            Request (opcode 0x07) ...
            Response (opcode 0x08) ...
        """
        self._ensure_connected()

        # Suppose your .proto has:
        # rpc Logout(LogoutRequest) returns (LogoutResponse);
        # message LogoutRequest {
        #   uint32 user_id = 1;
        #   bytes session_token = 2; 
        # }
        # message LogoutResponse {} // empty
        token_bytes = bytes.fromhex(session_token)

        request = exp_pb2.LogoutRequest(
            user_id=user_id,
            session_token=token_bytes
        )
        # Empty response
        self.stub.Logout(request)

    # --------------------------------------------------------------------------
    # 0x09: list_accounts
    # --------------------------------------------------------------------------
    def list_accounts(self, user_id: int, session_token: str, wildcard: str) -> List[str]:
        """
        List accounts matching the wildcard.
        
        Returns: list of usernames.
        
        Wire Protocol Reference:
            Request (opcode 0x09) ...
            Response (opcode 0x10) ...
        """
        self._ensure_connected()

        # Suppose in your proto:
        # rpc ListAccounts(ListAccountsRequest) returns (ListAccountsResponse);
        # message ListAccountsRequest {
        #   uint32 user_id = 1;
        #   bytes session_token = 2;
        #   string wildcard = 3;
        # }
        # message ListAccountsResponse {
        #   repeated string usernames = 1;
        # }

        token_bytes = bytes.fromhex(session_token)
        request = exp_pb2.ListAccountsRequest(
            user_id=user_id,
            session_token=token_bytes,
            wildcard=wildcard
        )
        response = self.stub.ListAccounts(request)
        # Return the list of usernames
        return list(response.usernames)

    # --------------------------------------------------------------------------
    # 0x11: display_conversation
    # --------------------------------------------------------------------------
    def display_conversation(self, user_id: int, session_token: str, conversant_id: int) -> list[tuple[int, str, bool]]:
        """
        Display conversation between the calling user (user_id) and conversant_id.
        
        Returns a list of tuples: (message_id, message_content, is_sender).
        
        Wire Protocol Reference:
            Request (opcode 0x11) ...
            Response (opcode 0x12) ...
        """
        self._ensure_connected()
        token_bytes = bytes.fromhex(session_token)

        # In your proto:
        # rpc DisplayConversation(DisplayConversationRequest) returns (DisplayConversationResponse);
        # message DisplayConversationRequest {
        #   uint32 user_id = 1;
        #   bytes  session_token = 2;
        #   uint32 conversant_id = 3;
        # }
        # message ConversationMessage {
        #   uint32 message_id = 1;
        #   bool sender_flag  = 2;
        #   string content    = 3;
        # }
        # message DisplayConversationResponse {
        #   repeated ConversationMessage messages = 1;
        # }

        request = exp_pb2.DisplayConversationRequest(
            user_id=user_id,
            session_token=token_bytes,
            conversant_id=conversant_id
        )
        response = self.stub.DisplayConversation(request)

        # Convert to the desired list of (id, content, is_sender)
        result = []
        for msg in response.messages:
            result.append((msg.message_id, msg.content, msg.sender_flag))
        return result

    # --------------------------------------------------------------------------
    # 0x13: send_message
    # --------------------------------------------------------------------------
    def send_message(self, user_id: int, session_token: str, recipient_id: int, message: str) -> bool:
        """
        Send a message to another user.

        Returns:
            bool: True if message was sent successfully, False otherwise.
        
        Wire Protocol Reference:
            Request (opcode 0x13) ...
            Response (opcode 0x14) ...
        """
        self._ensure_connected()
        token_bytes = bytes.fromhex(session_token)
        if len(token_bytes) != 32:
            print(f"[CLIENT] Invalid session token length: {len(token_bytes)}")
            return False

        # Suppose in your proto:
        # rpc SendMessage(SendMessageRequest) returns (SendMessageResponse);
        # message SendMessageRequest {
        #   uint32 sender_user_id = 1;
        #   bytes  session_token  = 2;
        #   uint32 recipient_user_id = 3;
        #   string message_content = 4;
        # }
        # message SendMessageResponse {}
        
        request = exp_pb2.SendMessageRequest(
            sender_user_id=user_id,
            session_token=token_bytes,
            recipient_user_id=recipient_id,
            message_content=message
        )

        try:
            self.stub.SendMessage(request)
            return True
        except Exception as e:
            print(f"[CLIENT] Failed to send message: {e}")
            return False

    # --------------------------------------------------------------------------
    # 0x15: read_messages
    # --------------------------------------------------------------------------
    def read_messages(self, user_id: int, session_token: str, num_messages: int) -> None:
        """
        Read a number of messages from server (mark them as read or retrieve them).
        
        Wire Protocol Reference:
            Request (opcode 0x15) ...
            Response (opcode 0x16) ...
        """
        self._ensure_connected()
        token_bytes = bytes.fromhex(session_token)

        # Suppose in your proto:
        # rpc ReadMessages(ReadMessagesRequest) returns (ReadMessagesResponse);
        # message ReadMessagesRequest {
        #   uint32 user_id = 1;
        #   bytes session_token = 2;
        #   uint32 number_of_messages_req = 3;
        # }
        # message ReadMessagesResponse {}

        request = exp_pb2.ReadMessagesRequest(
            user_id=user_id,
            session_token=token_bytes,
            number_of_messages_req=num_messages
        )
        self.stub.ReadMessages(request)

    # --------------------------------------------------------------------------
    # 0x17: delete_message
    # --------------------------------------------------------------------------
    def delete_message(self, user_id: int, message_uid: int, session_token: str) -> None:
        """
        Delete a message.
        
        Wire Protocol Reference:
            Request (opcode 0x17) ...
            Response (opcode 0x18) ...
        """
        self._ensure_connected()
        token_bytes = bytes.fromhex(session_token)

        # Suppose in your proto:
        # rpc DeleteMessage(DeleteMessageRequest) returns (DeleteMessageResponse);
        # message DeleteMessageRequest {
        #   uint32 user_id = 1;
        #   uint32 message_uid = 2;
        #   bytes  session_token = 3;
        # }
        # message DeleteMessageResponse {}
        
        request = exp_pb2.DeleteMessageRequest(
            user_id=user_id,
            message_uid=message_uid,
            session_token=token_bytes
        )
        self.stub.DeleteMessage(request)

    # --------------------------------------------------------------------------
    # 0x19: delete_account
    # --------------------------------------------------------------------------
    def delete_account(self, user_id: int, session_token: str) -> None:
        """
        Delete an account.
        
        Wire Protocol Reference:
            Request (opcode 0x19) ...
            Response (opcode 0x20) ...
        """
        self._ensure_connected()
        token_bytes = bytes.fromhex(session_token)

        # Suppose in your proto:
        # rpc DeleteAccount(DeleteAccountRequest) returns (DeleteAccountResponse);
        # message DeleteAccountRequest {
        #   uint32 user_id = 1;
        #   bytes session_token = 2;
        # }
        # message DeleteAccountResponse {}
        
        request = exp_pb2.DeleteAccountRequest(
            user_id=user_id,
            session_token=token_bytes
        )
        self.stub.DeleteAccount(request)

    # --------------------------------------------------------------------------
    # 0x21: get_unread_messages
    # --------------------------------------------------------------------------
    def get_unread_messages(self, user_id: int, session_token: str) -> list[tuple[int, int, int]]:
        """
        Fetch unread messages with minimal metadata:
        Returns a list of tuples (message_uid, sender_id, receiver_id).
        
        Wire Protocol Reference:
            Request (opcode 0x21) ...
            Response (opcode 0x22) ...
        """
        self._ensure_connected()
        token_bytes = bytes.fromhex(session_token)

        # Suppose in your proto:
        # rpc GetUnreadMessages(GetUnreadMessagesRequest) returns (GetUnreadMessagesResponse);
        # message GetUnreadMessagesRequest {
        #   uint32 user_id = 1;
        #   bytes session_token = 2;
        # }
        # message UnreadMessageInfo {
        #   uint32 message_uid = 1;
        #   uint32 sender_id = 2;
        #   uint32 receiver_id = 3;
        # }
        # message GetUnreadMessagesResponse {
        #   repeated UnreadMessageInfo messages = 1;
        # }

        request = exp_pb2.GetUnreadMessagesRequest(
            user_id=user_id,
            session_token=token_bytes
        )
        response = self.stub.GetUnreadMessages(request)

        result = []
        for msg_info in response.messages:
            result.append((msg_info.message_uid, msg_info.sender_id, msg_info.receiver_id))
        return result

    # --------------------------------------------------------------------------
    # 0x23: get_message_info
    # --------------------------------------------------------------------------
    def get_message_info(self, user_id: int, session_token: str, message_uid: int) -> tuple[bool, int, str]:
        """
        Get message information (read status, sender ID, content).
        
        Returns (has_been_read, sender_id, message_content).
        
        Wire Protocol Reference:
            Request (opcode 0x23) ...
            Response (opcode 0x24) ...
        """
        self._ensure_connected()
        token_bytes = bytes.fromhex(session_token)

        # Suppose in your proto:
        # rpc GetMessageInformation(GetMessageInformationRequest) returns (GetMessageInformationResponse);
        # message GetMessageInformationRequest {
        #   uint32 user_id = 1;
        #   bytes  session_token = 2;
        #   uint32 message_uid = 3;
        # }
        # message GetMessageInformationResponse {
        #   bool   read_flag       = 1;
        #   uint32 sender_id       = 2;
        #   string message_content = 3;
        # }

        request = exp_pb2.GetMessageInformationRequest(
            user_id=user_id,
            session_token=token_bytes,
            message_uid=message_uid
        )
        response = self.stub.GetMessageInformation(request)

        has_been_read = response.read_flag
        sender_id = response.sender_id
        message_content = response.message_content
        return has_been_read, sender_id, message_content

    # --------------------------------------------------------------------------
    # 0x25: get_username_by_id
    # --------------------------------------------------------------------------
    def get_username_by_id(self, user_id: int) -> str:
        """
        Retrieve a username by ID.
        
        Wire Protocol Reference:
            Request (opcode 0x25) ...
            Response (opcode 0x26) ...
        """
        self._ensure_connected()

        # Suppose in your proto:
        # rpc GetUsernameByID(GetUsernameByIDRequest) returns (GetUsernameByIDResponse);
        # message GetUsernameByIDRequest { uint32 user_id = 1; }
        # message GetUsernameByIDResponse { string username = 1; }

        request = exp_pb2.GetUsernameByIDRequest(user_id=user_id)
        response = self.stub.GetUsernameByID(request)
        return response.username

    # --------------------------------------------------------------------------
    # 0x27: mark_message_as_read
    # --------------------------------------------------------------------------
    def mark_message_as_read(self, user_id: int, session_token: str, message_uid: int) -> None:
        """
        Mark a specific message as read.
        
        Wire Protocol Reference:
            Request (opcode 0x27) ...
            Response (opcode 0x28) ...
        """
        self._ensure_connected()
        token_bytes = bytes.fromhex(session_token)

        # Suppose in your proto:
        # rpc MarkMessageAsRead(MarkMessageAsReadRequest) returns (MarkMessageAsReadResponse);
        # message MarkMessageAsReadRequest {
        #   uint32 user_id = 1;
        #   bytes  session_token = 2;
        #   uint32 message_uid = 3;
        # }
        # message MarkMessageAsReadResponse {}

        request = exp_pb2.MarkMessageAsReadRequest(
            user_id=user_id,
            session_token=token_bytes,
            message_uid=message_uid
        )
        self.stub.MarkMessageAsRead(request)

    # --------------------------------------------------------------------------
    # 0x29: get_user_by_username
    # --------------------------------------------------------------------------
    def get_user_by_username(self, username: str) -> tuple[bool, Optional[int]]:
        """
        Retrieve user info by username.
        Returns (found: bool, user_id: int or None).
        
        Wire Protocol Reference:
            Request (opcode 0x29) ...
            Response (opcode 0x2A) ...
        """
        self._ensure_connected()

        # Suppose in your proto:
        # rpc GetUserByUsername(GetUserByUsernameRequest) returns (GetUserByUsernameResponse);
        # message GetUserByUsernameRequest { string username = 1; }
        # message GetUserByUsernameResponse {
        #   enum FoundStatus { FOUND = 0; NOT_FOUND = 1; }
        #   FoundStatus status = 1;
        #   uint32 user_id = 2; // if found
        # }

        request = exp_pb2.GetUserByUsernameRequest(username=username)
        response = self.stub.GetUserByUsername(request)

        # If status == FOUND, return True and the user_id; otherwise False, None
        if response.status == exp_pb2.GetUserByUsernameResponse.FoundStatus.FOUND:
            return (True, response.user_id)
        else:
            return (False, None)

    # --------------------------------------------------------------------------
    # Example usage
    # --------------------------------------------------------------------------
    if __name__ == "__main__":
        # Simple usage example
        client = Client()
        try:
            # Connect once; subsequent calls reuse the channel
            if client.connect():
                new_token = client.create_account("alice", "password123")
                print(f"[CLIENT] Created account for alice, token = {new_token[:8]}...")

                success, token, unread = client.log_into_account("alice", "password123")
                if success:
                    print(f"[CLIENT] Logged in successfully, token={token[:8]}..., unread={unread}")
                else:
                    print("[CLIENT] Login failed.")

                # ... Call other methods as needed ...
            else:
                print("[CLIENT] Could not connect to gRPC server.")
        finally:
            client.disconnect()
