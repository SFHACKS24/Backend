import os
import requests
import json

API_ENDPOINT = "https://us-east-2.aws.neurelo.com/rest"
NEURELO_API_KEY = os.getenv('NEURELO_API_KEY')

api_headers = {
    "X-API-KEY": NEURELO_API_KEY
}
qstr = '{"$scalars": true, "$innerObjects": true}'


def get_user(user_id: str):
    response = requests.post(
        f"{API_ENDPOINT}/users/{user_id}?select={qstr}", headers=api_headers, timeout=10)
    user_data = response.json()

    return user_data.data


def update_user(user_id: str, user_data: dict):
    query = {"$scalars": True, "responses": {
        "$scalars": True}, "profile": {"$scalars": True}}
    response = requests.patch(f"{API_ENDPOINT}/users/{user_id}",
                              headers=api_headers, json=user_data, timeout=10)
    user_data = response.json()

    return user_data.data


def filter_user(query: dict):
    response = requests.post(
        f"{API_ENDPOINT}/users?filter={json.dumps(query)}&select={qstr}", headers=api_headers, timeout=10)
    user_data = response.json()

    return user_data.data


def get_compatibility(user_id: str):
    query = {"originUserId": {"equals": user_id}}
    response = requests.get(
        f"{API_ENDPOINT}/compatibility?filter={json.dumps(query)}", headers=api_headers, timeout=10)
    compatibility_data = response.json()

    return compatibility_data.data


def get_compatibilities(origin_id: str, target_ids: list):
    query = {"originUserId": {"equals": origin_id},
             "targetUserId": {"in": target_ids}}
    response = requests.post(
        f"{API_ENDPOINT}/compatibility?filter={json.dumps(query)}", headers=api_headers, timeout=10)
    compatibility_data = response.json()

    return compatibility_data.data


def update_compatibility(origin_id: str, target_id: str, compatibility_data: dict):
    query = {"originUserId": {"equals": origin_id},
             "targetUserId": {"equals": target_id}},
    response = requests.patch(
        f"{API_ENDPOINT}/compatibility?filter={json.dumps(query)}", headers=api_headers, json=compatibility_data, timeout=10)
    compatibility_data = response.json()

    return compatibility_data.data


def update_compatibilities_from_query(query: dict, compatibility_data: dict):
    response = requests.patch(
        f"{API_ENDPOINT}/compatibility?filter={json.dumps(query)}", headers=api_headers, json=compatibility_data, timeout=10)
    compatibility_data = response.json()

    return compatibility_data.data


def get_question_by_question_id(user_id: str, question_id: str):
    response = requests.get(
        f"{API_ENDPOINT}/users/{user_id}?select={qstr}", headers=api_headers, timeout=10)
    user_data = response.json().data

    return user_data["responses"].find(lambda x: x["questionId"] == question_id)
