import json

with open("serviceAccountKeyFirebase.json", "r") as f:
    data = json.load(f)

# Replace real newlines with literal \n in the private_key
data["private_key"] = data["private_key"].replace("\n", "\\n")

# Dump as a string to be used inside the .env
escaped_json = json.dumps(data)

print("Copy this into your .env:")
print(f'GOOGLE_CREDENTIALS_JSON={escaped_json}')

