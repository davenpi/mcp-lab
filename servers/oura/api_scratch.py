import json

import httpx
from dotenv import dotenv_values

config = dotenv_values(".env")

date = "2025-05-28"
params = {
    "start_date": date,
    "end_date": date,
}
url = "https://api.ouraring.com/v2/usercollection/daily_sleep"
headers = {"Authorization": f"Bearer {config['OURA_API_KEY']}"}

response = httpx.get(url, headers=headers, params=params)

# response = httpx.get(url, headers=headers)
print(response)
print("-" * 100)

# pretty print the response
print(json.dumps(response.json(), indent=4))

# Single day

# doc_id = "32e6fbb0-e370-41f4-a5b5-eaf6d733c907"

# print('-' * 100)
# print("Single day")
# print('-' * 100)
# response = httpx.get(f"{url}/{doc_id}", headers=headers)
# print(json.dumps(response.json(), indent=4))
