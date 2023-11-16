from jwt import encode, decode

#Funcion para crear token
def create_token(data: dict):
    token = encode(payload=data, key="my_secret_key", algorithm="HS256")
    return token

#Funcion para validar Token
def validate_token(token: str) -> dict:
    data = decode(token, key="my_secret_key", algorithms=["HS256"])
    return data