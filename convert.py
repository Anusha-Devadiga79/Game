import base64
print(base64.b64encode(open("credentials.json","rb").read()).decode())
