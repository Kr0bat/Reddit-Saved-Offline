import requests, requests.auth, sys, socket, webbrowser, pprint, subprocess


def getConnection():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8080))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client

print("Allow RSO.py temporary access to Reddit account functions\nThe web page will not close on its own")
subprocess.Popen(['C:/Program Files/Mozilla Firefox/firefox.exe', 'https://www.reddit.com/api/v1/authorize?client_id=UM-7ULt2BwjccQ&response_type=code&state=wontworkbro&redirect_uri=http://localhost:8080&duration=temporary&scope=save,history,identity'])

client = getConnection()
data = client.recv(1024).decode("utf-8")
code = data.split()[1].split('=')[2]
print(code)

headers = {"Authorization": f"Bearer {code}", "User-Agent": "Reddit-Saved-Offline by kr0bat"}
response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
print(response)