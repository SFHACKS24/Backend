import os
import requests

API_ENDPOINT = "https://us-east-2.aws.neurelo.com/rest"
NEURELO_API_KEY = os.getenv('NEURELO_API_KEY')

api_headers = {
    "X-API-KEY": NEURELO_API_KEY
}


def get_user(user_id: str):
    response = requests.post(
        f"{API_ENDPOINT}/users/{user_id}", headers=api_headers, timeout=10)
    user_data = response.json()

    return user_data.data


def update_user(user_id: str, user_data: dict):
    response = requests.put(f"{API_ENDPOINT}/users/{user_id}",
                            headers=api_headers, json=user_data, timeout=10)
    user_data = response.json()

    return user_data.data


def get_compatibility(user_id: str):
    response = requests.post(
        f"{API_ENDPOINT}/compatibility/{user_id}", headers=api_headers, timeout=10)
    compatibility_data = response.json()

    return compatibility_data.data


def get_compatibilities(user_ids: list):
    response = requests.post(
        f"{API_ENDPOINT}/compatibility", headers=api_headers, timeout=10)
    compatibility_data = response.json()

    return compatibility_data
