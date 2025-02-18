1. Create Account

Request (New Opcode 0x01):

    4 bytes: Total length
    1 byte: Opcode 0x01
    2 bytes: Username length
    n bytes: Username (UTF‑8)
    32 bytes: SHA‑256 hashed password

Response (New Opcode 0x02):

    4 bytes: Total length
    1 byte: Opcode 0x02
    32 bytes: Session token

2. Log into Account

Request (New Opcode 0x03):

    4 bytes: Total length
    1 byte: Opcode 0x03
    2 bytes: Username length
    n bytes: Username (UTF‑8)
    32 bytes: SHA‑256 hashed password

Response (New Opcode 0x04):

    4 bytes: Total length
    1 byte: Opcode 0x04
    1 byte: Status (0x00 means success)
    32 bytes: Session token
    4 bytes: Unread messages count

3. List Accounts

Request (New Opcode 0x05):

    4 bytes: Total length
    1 byte: Opcode 0x05
    2 bytes: User ID
    32 bytes: Session token
    2 bytes: Wildcard length
    n bytes: Wildcard (UTF‑8)

Response (New Opcode 0x06):

    4 bytes: Total length
    1 byte: Opcode 0x06
    2 bytes: Account count
    Then, for each account:
        2 bytes: Username length
        n bytes: Username (UTF‑8)

4. Display Conversation

Request (New Opcode 0x07):

    4 bytes: Total length
    1 byte: Opcode 0x07
    2 bytes: User ID
    32 bytes: Session token
    2 bytes: Conversant ID

Response (New Opcode 0x08):

    4 bytes: Total length
    1 byte: Opcode 0x08
    4 bytes: Message count
    Then, for each message:
        4 bytes: Message ID
        2 bytes: Message length
        1 byte: Sender flag (0x01 if sent by the requester, else 0x00)
        n bytes: Message content (UTF‑8)

5. Send Message

Request (New Opcode 0x09):

    4 bytes: Total length
    1 byte: Opcode 0x09
    2 bytes: Sender User ID
    32 bytes: Session token
    2 bytes: Recipient User ID
    2 bytes: Message length
    n bytes: Message content (UTF‑8)

Response (New Opcode 0x0A):

    4 bytes: Total length
    1 byte: Opcode 0x0A

6. Read Messages

Request (New Opcode 0x0B):

    4 bytes: Total length
    1 byte: Opcode 0x0B
    2 bytes: User ID
    32 bytes: Session token
    4 bytes: Number of messages requested

Response (New Opcode 0x0C):

    4 bytes: Total length
    1 byte: Opcode 0x0C

7. Delete Message

Request (New Opcode 0x0D):

    4 bytes: Total length
    1 byte: Opcode 0x0D
    2 bytes: User ID
    4 bytes: Message UID
    32 bytes: Session token

Response (New Opcode 0x0E):

    4 bytes: Total length
    1 byte: Opcode 0x0E

8. Delete Account

Request (New Opcode 0x0F):

    4 bytes: Total length
    1 byte: Opcode 0x0F
    2 bytes: User ID
    32 bytes: Session token

Response (New Opcode 0x10):

    4 bytes: Total length
    1 byte: Opcode 0x10

9. Get Unread Messages

Request (New Opcode 0x11):

    4 bytes: Total length
    1 byte: Opcode 0x11
    2 bytes: User ID
    32 bytes: Session token

Response (New Opcode 0x12):

    4 bytes: Total length
    1 byte: Opcode 0x12
    4 bytes: Count of unread messages
    Then, for each unread message:
        4 bytes: Message UID
        2 bytes: Sender ID
        2 bytes: Receiver ID

10. Get Message Information

Request (New Opcode 0x13):

    4 bytes: Total length
    1 byte: Opcode 0x13
    2 bytes: User ID
    32 bytes: Session token
    4 bytes: Message UID

Response (New Opcode 0x14):

    4 bytes: Total length
    1 byte: Opcode 0x14
    1 byte: Read flag (nonzero if already read)
    2 bytes: Sender ID
    2 bytes: Content length
    n bytes: Message content (UTF‑8)

11. Get Username by ID

Request (New Opcode 0x15):

    4 bytes: Total length
    1 byte: Opcode 0x15
    2 bytes: User ID

Response (New Opcode 0x16):

    4 bytes: Total length
    1 byte: Opcode 0x16
    2 bytes: Username length
    n bytes: Username (UTF‑8)

12. Mark Message as Read

Request (New Opcode 0x17):

    4 bytes: Total length
    1 byte: Opcode 0x17
    2 bytes: User ID
    32 bytes: Session token
    4 bytes: Message UID

Response (New Opcode 0x18):

    4 bytes: Total length
    1 byte: Opcode 0x18

13. Get User by Username

Request (New Opcode 0x19):

    4 bytes: Total length
    1 byte: Opcode 0x19
    2 bytes: Username length
    n bytes: Username (UTF‑8)

Response (New Opcode 0x1A):

    4 bytes: Total length
    1 byte: Opcode 0x1A
    1 byte: Status (0x00 if found; 0x01 if not)
    (If found) 2 bytes: User ID
