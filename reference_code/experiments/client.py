# client.py
import grpc
import hashlib
import exp_pb2
import exp_pb2_grpc

def create_account(stub, username, password):
    print(f"\n[CLIENT] Attempting to create account for {username}")
    password_hash = hashlib.sha256(password.encode()).digest()
    
    try:
        response = stub.CreateAccount(exp_pb2.CreateAccountRequest(
            username=username,
            password_hash=password_hash
        ))
        print(f"[CLIENT] Account created successfully!")
        print(f"[CLIENT] Session token received: {response.session_token.hex()[:8]}...")
        return response.session_token
    except grpc.RpcError as e:
        print(f"[CLIENT] Account creation failed: {e.details()}")
        return None

def login(stub, username, password):
    print(f"\n[CLIENT] Attempting to login as {username}")
    password_hash = hashlib.sha256(password.encode()).digest()
    
    response = stub.Login(exp_pb2.LoginRequest(
        username=username,
        password_hash=password_hash
    ))
    
    if response.status == exp_pb2.LoginResponse.SUCCESS:
        print(f"[CLIENT] Login successful!")
        print(f"[CLIENT] Session token: {response.session_token.hex()[:8]}...")
        print(f"[CLIENT] Unread messages: {response.unread_count}")
        return response.session_token
    else:
        print("[CLIENT] Login failed!")
        return None

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = exp_pb2_grpc.MessagingServiceStub(channel)
        
        # Test account creation
        token1 = create_account(stub, "alice", "password123")
        token2 = create_account(stub, "alice", "password123")  # Should fail
        token3 = create_account(stub, "bob", "password456")
        
        # Test login
        login(stub, "alice", "password123")  # Should succeed
        login(stub, "alice", "wrongpass")    # Should fail
        login(stub, "bob", "password456")    # Should succeed
        login(stub, "carol", "password789")  # Should fail

if __name__ == '__main__':
    run()
