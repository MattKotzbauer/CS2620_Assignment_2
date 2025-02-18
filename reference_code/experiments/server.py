# server.py
import grpc
from concurrent import futures
import hashlib
import os
import exp_pb2
import exp_pb2_grpc

class MessagingService(exp_pb2_grpc.MessagingServiceServicer):
    def __init__(self):
        # Simple in-memory storage for demo
        self.accounts = {}  # username -> password_hash
        self.sessions = {}  # session_token -> username
        
    def CreateAccount(self, request, context):
        print(f"[SERVER] Received CreateAccount request for user: {request.username}")
        
        if request.username in self.accounts:
            print(f"[SERVER] Account creation failed - username already exists")
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details('Username already exists')
            return exp_pb2.CreateAccountResponse()
            
        # Store account
        self.accounts[request.username] = request.password_hash
        
        # Generate session token
        session_token = os.urandom(32)
        self.sessions[session_token] = request.username
        
        print(f"[SERVER] Account created successfully for {request.username}")
        return exp_pb2.CreateAccountResponse(session_token=session_token)
        
    def Login(self, request, context):
        print(f"[SERVER] Received Login request for user: {request.username}")
        
        # Check if account exists and password matches
        if (request.username not in self.accounts or 
            self.accounts[request.username] != request.password_hash):
            print(f"[SERVER] Login failed - invalid credentials")
            return exp_pb2.LoginResponse(
                status=exp_pb2.LoginResponse.FAILURE,
                unread_count=0
            )
            
        # Generate new session token
        session_token = os.urandom(32)
        self.sessions[session_token] = request.username
        
        print(f"[SERVER] Login successful for {request.username}")
        return exp_pb2.LoginResponse(
            status=exp_pb2.LoginResponse.SUCCESS,
            session_token=session_token,
            unread_count=42  # Demo value
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    exp_pb2_grpc.add_MessagingServiceServicer_to_server(MessagingService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("[SERVER] Server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
