Operation Breakdown

    Search Username
        Request (Opcode 0x01):
            4 bytes: Total length
            1 byte: Opcode (0x01)
            2 bytes: Username length
            n bytes: Username (UTF‑8)
        Response (Opcode 0x02):
            4 bytes: Total length
            1 byte: Opcode (0x02)
            1 byte: Status code (0x00 indicates available)

    Create Account
        Request (Opcode 0x03):
            4 bytes: Total length
            1 byte: Opcode (0x03)
            2 bytes: Username length
            n bytes: Username (UTF‑8)
            32 bytes: SHA‑256 hashed password
        Response (Opcode 0x04):
            4 bytes: Total length
            1 byte: Opcode (0x04)
            32 bytes: Session token

    Log into Account
        Request (Opcode 0x05):
            4 bytes: Total length
            1 byte: Opcode (0x05)
            2 bytes: Username length
            n bytes: Username (UTF‑8)
            32 bytes: SHA‑256 hashed password
        Response (Opcode 0x06):
            4 bytes: Total length
            1 byte: Opcode (0x06)
            1 byte: Status (0x00 means success)
            32 bytes: Session token
            4 bytes: Unread messages count

    Log out of Account
        Request (Opcode 0x07):
            4 bytes: Total length
            1 byte: Opcode (0x07)
            2 bytes: User ID
            32 bytes: Session token
        Response (Opcode 0x08):
            4 bytes: Total length
            1 byte: Opcode (0x08)

    List Accounts
        Request (Opcode 0x09):
            4 bytes: Total length
            1 byte: Opcode (0x09)
            2 bytes: User ID
            32 bytes: Session token
            2 bytes: Wildcard string length
            n bytes: Wildcard (UTF‑8)
        Response (Opcode 0x10):
            4 bytes: Total length
            1 byte: Opcode (0x10)
            2 bytes: Account count
            For each account:
                2 bytes: Username length
                n bytes: Username (UTF‑8)

    Display Conversation
        Request (Opcode 0x11):
            4 bytes: Total length
            1 byte: Opcode (0x11)
            2 bytes: User ID
            32 bytes: Session token
            2 bytes: Conversant ID
        Response (Opcode 0x12):
            4 bytes: Total length
            1 byte: Opcode (0x12)
            4 bytes: Message count
            For each message:
                4 bytes: Message ID
                2 bytes: Message length
                1 byte: Sender flag (0x01 if the message is sent by the requester, else 0x00)
                n bytes: Message content (UTF‑8)

    Send Message
        Request (Opcode 0x13):
            4 bytes: Total length
            1 byte: Opcode (0x13)
            2 bytes: Sender User ID
            32 bytes: Session token
            2 bytes: Recipient User ID
            2 bytes: Message length
            n bytes: Message content (UTF‑8)
        Response (Opcode 0x14):
            4 bytes: Total length
            1 byte: Opcode (0x14)

    Read Messages
        Request (Opcode 0x15):
            4 bytes: Total length
            1 byte: Opcode (0x15)
            2 bytes: User ID
            32 bytes: Session token
            4 bytes: Number of messages requested
        Response (Opcode 0x16):
            4 bytes: Total length
            1 byte: Opcode (0x16)

    Delete Message
        Request (Opcode 0x17):
            4 bytes: Total length
            1 byte: Opcode (0x17)
            2 bytes: User ID
            4 bytes: Message UID
            32 bytes: Session token
        Response (Opcode 0x18):
            4 bytes: Total length
            1 byte: Opcode (0x18)

    Delete Account
        Request (Opcode 0x19):
            4 bytes: Total length
            1 byte: Opcode (0x19)
            2 bytes: User ID
            32 bytes: Session token
        Response (Opcode 0x20):
            4 bytes: Total length
            1 byte: Opcode (0x20)

    Get Unread Messages
        Request (Opcode 0x21):
            4 bytes: Total length
            1 byte: Opcode (0x21)
            2 bytes: User ID
            32 bytes: Session token
        Response (Opcode 0x22):
            4 bytes: Total length
            1 byte: Opcode (0x22)
            4 bytes: Count of unread messages
            For each unread message:
                4 bytes: Message UID
                2 bytes: Sender ID
                2 bytes: Receiver ID

    Get Message Information
        Request (Opcode 0x23):
            4 bytes: Total length
            1 byte: Opcode (0x23)
            2 bytes: User ID
            32 bytes: Session token
            4 bytes: Message UID
        Response (Opcode 0x24):
            4 bytes: Total length
            1 byte: Opcode (0x24)
            1 byte: Read flag (nonzero if already read)
            2 bytes: Sender ID
            2 bytes: Content length
            n bytes: Message content (UTF‑8)

    Get Username by ID
        Request (Opcode 0x25):
            4 bytes: Total length
            1 byte: Opcode (0x25)
            2 bytes: User ID
        Response (Opcode 0x26):
            4 bytes: Total length
            1 byte: Opcode (0x26)
            2 bytes: Username length
            n bytes: Username (UTF‑8)

    Mark Message as Read
        Request (Opcode 0x27):
            4 bytes: Total length
            1 byte: Opcode (0x27)
            2 bytes: User ID
            32 bytes: Session token
            4 bytes: Message UID
        Response (Opcode 0x28):
            4 bytes: Total length
            1 byte: Opcode (0x28)

    Get User by Username
        Request (Opcode 0x29):
            4 bytes: Total length
            1 byte: Opcode (0x29)
            2 bytes: Username length
            n bytes: Username (UTF‑8)
        Response (Opcode 0x2A):
            4 bytes: Total length
            1 byte: Opcode (0x2A)
            1 byte: Status (0x00 if found; otherwise, 0x01)
            (If found) 2 bytes: User ID


