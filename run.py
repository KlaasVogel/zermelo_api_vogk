from zermelo_api import ZermeloAPI

testZermelo = ZermeloAPI()

with open("cred.ini") as f:
    token = f.read()
    print(testZermelo.add_token(token))
