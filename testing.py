import pyotp
import uuid
sessions = {}
totpalice = pyotp.TOTP('JBSWY3DPEHPK3PXP')


def loginAndGetSession(number):
    # Generate a new UUID (version 4)
    new_uuid = uuid.uuid4()

    # Add the UUID and associated number to the dictionary
    sessions[new_uuid] = number

    return new_uuid

def getUserFromSession(some_uuid):
    # Retrieve the associated number using the UUID
    print(sessions)
    return sessions.get(some_uuid, "UUID not found")

def verify_rights(sid):
    if sessions.get(sid) != None:
        if sessions.get(sid)[0] == 'alice':
            print('This session belongs to alice.')
    else:
        print('No sid associated.')
        print(sessions.items())
        print(sessions.get('UUID'))

while True:
    key = input('Enter Key\n')
    if totpalice.verify(key) == True:
        print("Hi, alice")
        print(loginAndGetSession(1))
    else:
        print(key)
        print(getUserFromSession(key))
