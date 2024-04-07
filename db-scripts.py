import requests
import json
import os
from dotenv import load_dotenv

# Get NEURELO_API_KEY from environment variables
load_dotenv()
NEURELO_API_KEY = os.getenv('NEURELO_API_KEY')

# Open the user.json file and parse as a JSON
with open('./user.json') as file:
    user_data = json.load(file)

with open("./compatibility.json") as file:
    compatibility_data = json.load(file)

# Send a POST request to an API endpoint with headers and json
url = "https://us-east-2.aws.neurelo.com"
headers = {"X-API-KEY": NEURELO_API_KEY}
qstr = '{"$scalars": true, "$innerObjects": true}'

def init_data():
    # Iterate through the key-value pairs of user_data
    data = []
    for idx, value in user_data.items():
        profile = value["profile"]
        sample = []
        for k, v in value["responses"].items():
            v["questionId"] = k
            sample.append(v)
        print(profile)
        data.append({
            "profile": profile,
            "leadingPrompt": value["leadingPrompt"],
            "responses": sample,
            "userId": idx,
        })

    response = requests.post(
        f"{url}/rest/users?select={qstr}", headers=headers, json=data)

    print(response.json()["errors"][0])

# init_data()


def init_comp():
    data = compatibility_data["0"]
    comps = []
    for k, v in data.items():
        v["originUserId"] = "0"
        v["targetUserId"] = k
        comps.append(v)
    response = requests.post(
        f"{url}/rest/compatibility?select={qstr}", headers=headers, json=comps)
    print(response.json()["errors"][0])


init_comp()
