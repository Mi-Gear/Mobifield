def read_token():
    with open("token.txt", "r", encoding="utf-8") as f:
        return f.read()

TOKEN = read_token