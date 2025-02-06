import pyotp
import uuid
sessions = {}
totpalice = pyotp.TOTP('JBSWY3DPEHPK3PXP')


def loginAndGetSession(number):
    new_uuid = uuid.uuid4()
    sessions[new_uuid] = number
    return new_uuid

def getUserFromSession(some_uuid):
    return sessions.get(uuid.UUID(some_uuid))

def verify_rights(sid):
    if getUserFromSession(sid) != None:
        if getUserFromSession(sid) == 1:
            print('This session belongs to alice.')
    else:
        print('No sid associated.')

while True:
    key = input('Enter Key\n')
    if totpalice.verify(key) == True:
        print("Hi, alice")
        print('Session token:')
        print(loginAndGetSession(1))
    else:
        try:
            print('Userid:')
            print(getUserFromSession(key))
            verify_rights(key)
        except:
            print('INVALID DATA!')